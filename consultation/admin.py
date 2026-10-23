import csv

from django.contrib import admin
from django.http import HttpResponse
from django.urls import reverse
from django.utils import timezone
from django.utils.html import format_html
from django_extended_ol.admin import WMTSGISModelAdmin

from .models import (Answer, Chapter, ChapterDocument, Consultation, Feedback, MatrixRow, Proposal, Question,
                     Questionnaire, QuestionnaireResponse, ResponseOption, Taxonomy, TaxonomyGroup)


def csv_response(filename, header, rows):
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="{filename}-{timezone.localdate():%Y%m%d}.csv"'
    response.write("﻿")  # BOM so Excel reads UTF-8
    writer = csv.writer(response, delimiter=";")
    writer.writerow(header)
    writer.writerows(rows)
    return response


def edit_link(obj, label="Modifier"):
    if not obj or not obj.pk:
        return "—"
    url = reverse(f"admin:{obj._meta.app_label}_{obj._meta.model_name}_change", args=[obj.pk])
    return format_html('<a href="{}">{}</a>', url, label)


class ChapterInline(admin.TabularInline):
    model = Chapter
    fields = ["position", "title", "details"]
    readonly_fields = ["details"]
    extra = 0

    @admin.display(description="Introduction, documents, questionnaire")
    def details(self, obj):
        return edit_link(obj, "Modifier le chapitre")


@admin.register(Consultation)
class ConsultationAdmin(admin.ModelAdmin):
    list_display = ["title", "slug", "is_published", "opens_on", "closes_on", "proposals_link"]
    list_filter = ["is_published"]
    search_fields = ["title"]
    prepopulated_fields = {"slug": ["title"]}
    inlines = [ChapterInline]

    @admin.display(description="Mesures")
    def proposals_link(self, obj):
        url = reverse("admin:consultation_proposal_changelist") + f"?consultation__id__exact={obj.pk}"
        return format_html('<a href="{}">{}</a>', url, obj.proposals.count())


class ChapterDocumentInline(admin.TabularInline):
    model = ChapterDocument
    fields = ["position", "title", "file"]
    extra = 0


@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ["title", "consultation", "position", "questionnaire_link"]
    list_filter = ["consultation"]
    fields = ["consultation", "position", "title", "intro", "questionnaire_link"]
    readonly_fields = ["questionnaire_link"]
    inlines = [ChapterDocumentInline]

    @admin.display(description="Questionnaire")
    def questionnaire_link(self, obj):
        if not obj or not obj.pk:
            return "Enregistrez le chapitre pour lui ajouter un questionnaire."
        if hasattr(obj, "questionnaire"):
            return edit_link(obj.questionnaire, obj.questionnaire.title)
        url = reverse("admin:consultation_questionnaire_add") + f"?chapter={obj.pk}"
        return format_html('<a href="{}">Ajouter un questionnaire</a>', url)


class QuestionInline(admin.StackedInline):
    model = Question
    fields = [("position", "question_type", "mandatory"), "body", "description",
              ("max_choices", "max_characters"), "options_link"]
    readonly_fields = ["options_link"]
    extra = 0

    @admin.display(description="Options / lignes")
    def options_link(self, obj):
        if not obj or not obj.pk:
            return "Enregistrez pour ajouter des options."
        if not obj.has_options:
            return "—"
        return edit_link(obj, f"{obj.options.count()} option(s), {obj.matrix_rows.count()} ligne(s) — modifier")


@admin.register(Questionnaire)
class QuestionnaireAdmin(admin.ModelAdmin):
    list_display = ["title", "chapter", "response_count"]
    list_filter = ["chapter__consultation"]
    inlines = [QuestionInline]
    actions = ["export_responses"]

    @admin.display(description="Réponses")
    def response_count(self, obj):
        return obj.responses.count()

    @admin.action(description="Exporter les réponses (CSV)")
    def export_responses(self, request, queryset):
        rows, header = [], ["questionnaire", "date", "participant", "e-mail"]
        questions = []
        for questionnaire in queryset:
            questions += [q for q in questionnaire.questions.all() if not q.is_display_only]
        header += [str(q) for q in questions]
        responses = QuestionnaireResponse.objects.filter(questionnaire__in=queryset).select_related(
            "questionnaire", "user").prefetch_related("answers__question__options", "answers__question__matrix_rows")
        for response in responses:
            answers = {a.question_id: a.display() for a in response.answers.all()}
            rows.append([response.questionnaire.title, timezone.localtime(response.created_at).strftime("%Y-%m-%d %H:%M"),
                         response.user.get_full_name() or response.user.username, response.user.email]
                        + [answers.get(q.pk, "") for q in questions])
        return csv_response("reponses-questionnaire", header, rows)


class ResponseOptionInline(admin.TabularInline):
    model = ResponseOption
    fields = ["position", "body", "free_text"]
    extra = 0


class MatrixRowInline(admin.TabularInline):
    model = MatrixRow
    fields = ["position", "body"]
    extra = 0
    verbose_name_plural = "lignes de matrice (questions de type matrice uniquement)"


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ["__str__", "questionnaire", "question_type", "position"]
    list_filter = ["questionnaire", "question_type"]
    fields = ["questionnaire", ("position", "question_type", "mandatory"), "body", "description",
              ("max_choices", "max_characters")]
    inlines = [ResponseOptionInline, MatrixRowInline]


class AnswerInline(admin.TabularInline):
    model = Answer
    fields = ["question", "answer"]
    readonly_fields = fields
    extra = 0
    can_delete = False

    @admin.display(description="réponse")
    def answer(self, obj):
        return obj.display()

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(QuestionnaireResponse)
class QuestionnaireResponseAdmin(admin.ModelAdmin):
    list_display = ["questionnaire", "user", "created_at"]
    list_filter = ["questionnaire"]
    readonly_fields = ["questionnaire", "user", "created_at"]
    inlines = [AnswerInline]

    def has_add_permission(self, request):
        return False


class TaxonomyInline(admin.TabularInline):
    model = Taxonomy
    fields = ["position", "name"]
    extra = 1


@admin.register(TaxonomyGroup)
class TaxonomyGroupAdmin(admin.ModelAdmin):
    list_display = ["name", "position", "taxonomy_names"]
    search_fields = ["name", "taxonomies__name"]
    inlines = [TaxonomyInline]

    @admin.display(description="Taxonomies")
    def taxonomy_names(self, obj):
        return ", ".join(t.name for t in obj.taxonomies.all())

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("taxonomies")


@admin.register(Taxonomy)
class TaxonomyAdmin(admin.ModelAdmin):
    """Not in the admin menu: groups are edited with their taxonomies, this only feeds the autocomplete."""
    search_fields = ["name", "group__name"]

    def has_module_permission(self, request):
        return False


@admin.register(Proposal)
class ProposalAdmin(WMTSGISModelAdmin):
    list_display = ["__str__", "consultation", "position", "feedback_count"]
    list_filter = ["consultation", "taxonomies"]
    search_fields = ["reference", "title", "taxonomies__name"]
    fields = ["consultation", ("position", "reference"), "title", "summary", "taxonomies", "file", "geom"]
    autocomplete_fields = ["taxonomies"]

    @admin.display(description="Avis")
    def feedback_count(self, obj):
        return obj.feedbacks.count()


@admin.register(Feedback)
class FeedbackAdmin(WMTSGISModelAdmin):
    list_display = ["proposal", "user", "created_at", "has_location"]
    list_filter = ["proposal__consultation", "created_at"]
    search_fields = ["body", "proposal__title", "proposal__reference", "user__username", "user__email"]
    readonly_fields = ["proposal", "user", "body", "created_at"]
    actions = ["export_feedbacks"]

    @admin.display(description="Localisé", boolean=True)
    def has_location(self, obj):
        return obj.location is not None

    def has_add_permission(self, request):
        return False

    @admin.action(description="Exporter les avis (CSV)")
    def export_feedbacks(self, request, queryset):
        rows = [[timezone.localtime(f.created_at).strftime("%Y-%m-%d %H:%M"), f.proposal.consultation.title,
                 f.proposal.reference, f.proposal.title, f.user.get_full_name() or f.user.username, f.user.email,
                 f.body, round(f.location.x, 1) if f.location else "", round(f.location.y, 1) if f.location else ""]
                for f in queryset.select_related("proposal__consultation", "user")]
        return csv_response("avis", ["date", "consultation", "référence", "mesure", "participant", "e-mail",
                                     "avis", "E (LV95)", "N (LV95)"], rows)
