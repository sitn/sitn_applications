import json
import mimetypes
import os
from urllib.parse import urlencode

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction
from django.db.models import Q
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.clickjacking import xframe_options_sameorigin

from .forms import FeedbackForm, QuestionnaireForm
from .models import ChapterDocument, Consultation, Proposal, Questionnaire, QuestionnaireResponse, Taxonomy


def _published(slug):
    return get_object_or_404(Consultation, slug=slug, is_published=True)


def consultation_list(request):
    consultations = Consultation.objects.filter(is_published=True)
    first_two = list(consultations[:2])
    if len(first_two) == 1:
        return redirect(first_two[0])
    return render(request, "consultation/consultation_list.html", {"consultations": consultations})


def consultation_detail(request, slug):
    consultation = _published(slug)
    chapters = consultation.chapters.prefetch_related("documents").select_related("questionnaire")
    answered = set()
    if request.user.is_authenticated:
        answered = set(QuestionnaireResponse.objects.filter(
            user=request.user, questionnaire__chapter__consultation=consultation
        ).values_list("questionnaire_id", flat=True))
    return render(request, "consultation/consultation_detail.html", {
        "consultation": consultation,
        "sections": consultation.sections(chapters),
        "answered": answered,
        "proposal_count": consultation.proposals.count(),
    })


@login_required
def questionnaire(request, slug, chapter_id):
    consultation = _published(slug)
    questionnaire = get_object_or_404(Questionnaire, chapter_id=chapter_id, chapter__consultation=consultation)
    response = QuestionnaireResponse.objects.filter(questionnaire=questionnaire, user=request.user).first()
    editable = consultation.is_open
    if response is None and not editable:
        messages.warning(request, "La participation à cette consultation est close.")
        return redirect(consultation)

    data = request.POST if editable and request.method == "POST" else None
    form = QuestionnaireForm(data, questionnaire=questionnaire, response=response, disabled=not editable)
    if data is not None and form.is_valid():
        try:
            with transaction.atomic():
                if response is None:
                    response = QuestionnaireResponse.objects.create(questionnaire=questionnaire, user=request.user)
                else:
                    response.answers.all().delete()
                form.save(response)
        except IntegrityError:
            # Double submission: the unique constraint already holds a response
            pass
        messages.success(request, "Merci, vos réponses ont été enregistrées.")
        return redirect(consultation)
    return render(request, "consultation/questionnaire.html", {
        "consultation": consultation,
        "questionnaire": questionnaire,
        "form": form,
        "response": response,
        "editable": editable,
    })


def proposal_list(request, slug):
    """
    ``q`` searches titles, references and taxonomies; each ``tag`` is a taxonomy id.
    Tags of one group are alternatives (OR), tags of different groups are cumulative (AND).
    """
    consultation = _published(slug)
    query = request.GET.get("q", "").strip()
    selected = {int(t) for t in request.GET.getlist("tag") if t.isdigit()}

    taxonomies = Taxonomy.objects.filter(proposals__consultation=consultation).select_related("group").distinct()
    groups = {}
    for taxonomy in taxonomies:
        params = {"q": query} if query else {}
        params["tag"] = sorted(selected ^ {taxonomy.pk})
        taxonomy.active = taxonomy.pk in selected
        taxonomy.toggle_url = "?" + urlencode(params, doseq=True)
        groups.setdefault(taxonomy.group, []).append(taxonomy)

    proposals = consultation.proposals.prefetch_related("taxonomies__group")
    if query:
        proposals = proposals.filter(
            Q(title__icontains=query) | Q(reference__icontains=query)
            | Q(taxonomies__name__icontains=query) | Q(taxonomies__group__name__icontains=query)
        ).distinct()
    for group, group_taxonomies in groups.items():
        ids = [t.pk for t in group_taxonomies if t.active]
        if ids:
            proposals = proposals.filter(pk__in=Proposal.objects.filter(taxonomies__in=ids).values("pk"))

    return render(request, "consultation/proposal_list.html", {
        "consultation": consultation,
        "proposals": proposals,
        "groups": groups.items(),
        "query": query,
        "is_filtered": bool(query or selected),
    })


def proposal_detail(request, slug, pk):
    consultation = _published(slug)
    proposal = get_object_or_404(Proposal, pk=pk, consultation=consultation)
    context = {"consultation": consultation, "proposal": proposal}

    if request.user.is_authenticated:
        # Feedback is private: only the current user's own entries are ever shown
        context["feedbacks"] = proposal.feedbacks.filter(user=request.user)
        if consultation.is_open:
            form = FeedbackForm(request.POST or None, proposal=proposal)
            if request.method == "POST" and form.is_valid():
                feedback = form.save(commit=False)
                feedback.proposal = proposal
                feedback.user = request.user
                feedback.save()
                messages.success(request, "Merci, votre avis a été enregistré. Il n'est visible que par vous.")
                return redirect(f"{proposal.get_absolute_url()}#avis")
            context["form"] = form
            context["proposal_geojson"] = json.loads(proposal.geom.geojson) if proposal.geom else None
    return render(request, "consultation/proposal_detail.html", context)


def _serve(file_field, as_attachment):
    try:
        handle = file_field.open("rb")
    except FileNotFoundError:
        raise Http404("Fichier introuvable")
    filename = os.path.basename(file_field.name)
    content_type = mimetypes.guess_type(filename)[0] or "application/octet-stream"
    return FileResponse(handle, as_attachment=as_attachment, filename=filename, content_type=content_type)


def banner_file(request, slug):
    consultation = _published(slug)
    if not consultation.banner:
        raise Http404("Aucune bannière")
    return _serve(consultation.banner, as_attachment=False)


def document_file(request, slug, pk):
    document = get_object_or_404(ChapterDocument, pk=pk, chapter__consultation=_published(slug))
    download = "telecharger" in request.GET or not document.file.name.lower().endswith(".pdf")
    return _serve(document.file, as_attachment=download)


@xframe_options_sameorigin
def proposal_file(request, slug, pk):
    """Inline so the PDF or image can be embedded in the proposal page."""
    proposal = get_object_or_404(Proposal, pk=pk, consultation=_published(slug))
    if not proposal.file:
        raise Http404("Aucun document")
    return _serve(proposal.file, as_attachment=False)
