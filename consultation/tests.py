import shutil
import tempfile
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.gis.geos import LineString
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from .models import (Answer, Chapter, ChapterDocument, Consultation, Feedback, MatrixRow, Proposal, Question,
                     Questionnaire, QuestionnaireResponse, ResponseOption, Taxonomy, TaxonomyGroup)

MEDIA_ROOT = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class ConsultationTestCase(TestCase):

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        User = get_user_model()
        self.alice = User.objects.create_user("alice", "alice@example.org", "x")
        self.bob = User.objects.create_user("bob", "bob@example.org", "x")
        self.consultation = Consultation.objects.create(
            title="Plan directeur VTT", slug="vtt", about="<p>Présentation</p>", is_published=True)
        self.chapter = Chapter.objects.create(consultation=self.consultation, title="Diagnostic",
                                              intro="<p>Introduction</p>")
        self.proposal = Proposal.objects.create(
            consultation=self.consultation, reference="C1", title="Connexion", summary="<p>Résumé</p>",
            geom=LineString((2560000, 1205000), (2561000, 1206000), srid=2056))

    def build_questionnaire(self):
        questionnaire = Questionnaire.objects.create(chapter=self.chapter, title="Votre pratique")
        q = {}
        q["short"] = Question.objects.create(questionnaire=questionnaire, position=1, body="Commune",
                                             question_type=Question.SHORT_RESPONSE, mandatory=True)
        q["title"] = Question.objects.create(questionnaire=questionnaire, position=2, body="Pratique",
                                             question_type=Question.TITLE_AND_DESCRIPTION)
        q["single"] = Question.objects.create(questionnaire=questionnaire, position=3, body="Profil",
                                              question_type=Question.SINGLE_OPTION, mandatory=True)
        self.vttiste = ResponseOption.objects.create(question=q["single"], body="Vététiste", position=1)
        self.other = ResponseOption.objects.create(question=q["single"], body="Autre", free_text=True, position=2)
        q["multiple"] = Question.objects.create(questionnaire=questionnaire, position=4, body="Types",
                                                question_type=Question.MULTIPLE_OPTION, max_choices=2)
        self.multi = [ResponseOption.objects.create(question=q["multiple"], body=b, position=i)
                      for i, b in enumerate(["XC", "Enduro", "Gravel"])]
        q["sorting"] = Question.objects.create(questionnaire=questionnaire, position=5, body="Priorités",
                                               question_type=Question.SORTING)
        self.sort = [ResponseOption.objects.create(question=q["sorting"], body=b, position=i)
                     for i, b in enumerate(["Parcours", "Signalisation"])]
        q["matrix"] = Question.objects.create(questionnaire=questionnaire, position=6, body="Satisfaction",
                                              question_type=Question.MATRIX_SINGLE)
        self.matrix_options = [ResponseOption.objects.create(question=q["matrix"], body=b, position=i)
                               for i, b in enumerate(["Oui", "Non"])]
        self.matrix_row = MatrixRow.objects.create(question=q["matrix"], body="Balisage")
        return questionnaire, q

    def valid_answers(self, q):
        return {
            f"q{q['short'].pk}": "Neuchâtel",
            f"q{q['single'].pk}": str(self.other.pk),
            f"q{q['single'].pk}_o{self.other.pk}": "Randonneur",
            f"q{q['multiple'].pk}": [str(self.multi[0].pk), str(self.multi[2].pk)],
            f"q{q['sorting'].pk}_o{self.sort[0].pk}": "2",
            f"q{q['sorting'].pk}_o{self.sort[1].pk}": "1",
            f"q{q['matrix'].pk}_r{self.matrix_row.pk}": str(self.matrix_options[1].pk),
        }


class PublicPagesTest(ConsultationTestCase):

    def test_unpublished_consultation_is_hidden(self):
        self.consultation.is_published = False
        self.consultation.save()
        self.assertEqual(self.client.get(reverse("consultation:list")).context["consultations"].count(), 0)
        self.assertEqual(self.client.get(reverse("consultation:detail", args=["vtt"])).status_code, 404)
        self.assertEqual(self.client.get(self.proposal.get_absolute_url()).status_code, 404)

    def test_home_page_shows_about_chapters_and_proposals(self):
        self.build_questionnaire()
        ChapterDocument.objects.create(chapter=self.chapter, title="Rapport",
                                       file=SimpleUploadedFile("rapport.pdf", b"%PDF-1.4"))
        response = self.client.get(reverse("consultation:detail", args=["vtt"]))
        self.assertContains(response, "Présentation")
        self.assertContains(response, "Diagnostic")
        self.assertContains(response, "Rapport")
        self.assertContains(response, "Répondre au questionnaire")
        self.assertContains(response, reverse("consultation:proposals", args=["vtt"]))

    def test_proposal_list_and_detail(self):
        response = self.client.get(reverse("consultation:proposals", args=["vtt"]))
        self.assertContains(response, "Connexion")
        response = self.client.get(self.proposal.get_absolute_url())
        self.assertContains(response, "Se connecter pour donner son avis")
        self.assertNotIn("form", response.context)

    def test_measures_section_position(self):
        self.chapter.position = 1
        self.chapter.save()
        last = Chapter.objects.create(consultation=self.consultation, title="Mise en oeuvre", position=3)
        chapters = self.consultation.chapters.all()
        self.assertEqual(self.consultation.sections(chapters), [self.chapter, last, None])
        self.consultation.measures_position = 2
        self.assertEqual(self.consultation.sections(chapters), [self.chapter, None, last])
        self.consultation.measures_position = 0
        self.assertEqual(self.consultation.sections(chapters), [None, self.chapter, last])

    def test_proposal_search_and_taxonomy_filters(self):
        regions = TaxonomyGroup.objects.create(name="Régions")
        scope = TaxonomyGroup.objects.create(name="Portée")
        littoral = Taxonomy.objects.create(group=regions, name="Littoral")
        montagnes = Taxonomy.objects.create(group=regions, name="Montagnes")
        cantonal = Taxonomy.objects.create(group=scope, name="Cantonal")
        self.proposal.taxonomies.set([littoral, cantonal])
        other = Proposal.objects.create(consultation=self.consultation, reference="I2", title="Itinéraire")
        other.taxonomies.set([montagnes])

        def titles(**params):
            response = self.client.get(reverse("consultation:proposals", args=["vtt"]), params)
            return sorted(p.title for p in response.context["proposals"])

        self.assertEqual(titles(), ["Connexion", "Itinéraire"])
        self.assertEqual(titles(q="itin"), ["Itinéraire"])
        self.assertEqual(titles(q="montagnes"), ["Itinéraire"])
        # Same group: OR; different groups: AND
        self.assertEqual(titles(tag=[littoral.pk, montagnes.pk]), ["Connexion", "Itinéraire"])
        self.assertEqual(titles(tag=[montagnes.pk, cantonal.pk]), [])

    def test_rich_text_is_sanitized(self):
        self.consultation.about = '<p>ok</p><script>alert(1)</script>'
        self.consultation.full_clean()
        self.assertNotIn("script", self.consultation.about)


class QuestionnaireTest(ConsultationTestCase):

    def test_login_required(self):
        self.build_questionnaire()
        url = reverse("consultation:questionnaire", args=["vtt", self.chapter.pk])
        self.assertEqual(self.client.get(url).status_code, 302)

    def test_all_question_types_are_saved(self):
        _, q = self.build_questionnaire()
        self.client.force_login(self.alice)
        url = reverse("consultation:questionnaire", args=["vtt", self.chapter.pk])
        self.assertEqual(self.client.get(url).status_code, 200)
        response = self.client.post(url, self.valid_answers(q))
        self.assertRedirects(response, self.consultation.get_absolute_url())

        answers = {a.question_id: a for a in Answer.objects.filter(response__user=self.alice)}
        self.assertEqual(answers[q["short"].pk].text, "Neuchâtel")
        self.assertNotIn(q["title"].pk, answers)
        self.assertEqual(answers[q["single"].pk].display(), "Autre (Randonneur)")
        self.assertEqual(answers[q["multiple"].pk].display(), "XC ; Gravel")
        self.assertEqual(answers[q["sorting"].pk].display(), "1. Signalisation ; 2. Parcours")
        self.assertEqual(answers[q["matrix"].pk].display(), "Balisage : Non")

    def test_mandatory_and_limits(self):
        _, q = self.build_questionnaire()
        self.client.force_login(self.alice)
        url = reverse("consultation:questionnaire", args=["vtt", self.chapter.pk])
        data = self.valid_answers(q)
        data[f"q{q['short'].pk}"] = ""
        data[f"q{q['multiple'].pk}"] = [str(o.pk) for o in self.multi]
        data[f"q{q['sorting'].pk}_o{self.sort[1].pk}"] = "2"
        form = self.client.post(url, data).context["form"]
        self.assertIn(f"q{q['short'].pk}", form.errors)
        self.assertIn(f"q{q['multiple'].pk}", form.errors)
        self.assertTrue(form.non_field_errors())
        self.assertFalse(QuestionnaireResponse.objects.exists())

    def test_one_response_per_user_can_be_edited(self):
        questionnaire, q = self.build_questionnaire()
        self.client.force_login(self.alice)
        url = reverse("consultation:questionnaire", args=["vtt", self.chapter.pk])
        self.client.post(url, self.valid_answers(q))

        form = self.client.get(url).context["form"]
        self.assertEqual(form[f"q{q['short'].pk}"].value(), "Neuchâtel")
        self.assertEqual(form[f"q{q['single'].pk}_o{self.other.pk}"].value(), "Randonneur")
        self.assertEqual(form[f"q{q['multiple'].pk}"].value(), [str(self.multi[0].pk), str(self.multi[2].pk)])
        self.assertEqual(form[f"q{q['sorting'].pk}_o{self.sort[1].pk}"].value(), "1")
        self.assertEqual(form[f"q{q['matrix'].pk}_r{self.matrix_row.pk}"].value(), str(self.matrix_options[1].pk))

        first_date = questionnaire.responses.get().created_at
        data = self.valid_answers(q)
        data[f"q{q['short'].pk}"] = "Boudry"
        self.client.post(url, data)
        self.assertEqual(questionnaire.responses.count(), 1)
        self.assertEqual(Answer.objects.get(question=q["short"]).text, "Boudry")
        self.assertGreater(questionnaire.responses.get().created_at, first_date)

    def test_double_submission_keeps_last_answers(self):
        questionnaire, q = self.build_questionnaire()
        url = reverse("consultation:questionnaire", args=["vtt", self.chapter.pk])
        self.client.force_login(self.alice)
        # Both submissions start from the same form, without an existing response
        first, second = self.valid_answers(q), self.valid_answers(q)
        second[f"q{q['short'].pk}"] = "Boudry"
        self.client.post(url, first)
        self.client.post(url, second)
        self.assertEqual(questionnaire.responses.count(), 1)
        self.assertEqual(Answer.objects.filter(question=q["short"]).get().text, "Boudry")

    def test_closed_consultation_shows_answers_read_only(self):
        _, q = self.build_questionnaire()
        self.client.force_login(self.alice)
        url = reverse("consultation:questionnaire", args=["vtt", self.chapter.pk])
        self.client.post(url, self.valid_answers(q))
        self.consultation.closes_on = timezone.localdate() - timedelta(days=1)
        self.consultation.save()

        form = self.client.get(url).context["form"]
        self.assertTrue(all(field.disabled for field in form.fields.values()))
        data = self.valid_answers(q)
        data[f"q{q['short'].pk}"] = "Boudry"
        self.client.post(url, data)
        self.assertEqual(Answer.objects.get(question=q["short"]).text, "Neuchâtel")

    def test_closed_consultation_refuses_responses(self):
        _, q = self.build_questionnaire()
        self.consultation.closes_on = timezone.localdate() - timedelta(days=1)
        self.consultation.save()
        self.client.force_login(self.alice)
        url = reverse("consultation:questionnaire", args=["vtt", self.chapter.pk])
        self.client.post(url, self.valid_answers(q))
        self.assertFalse(QuestionnaireResponse.objects.exists())


class FeedbackTest(ConsultationTestCase):

    def test_feedback_is_saved_with_location(self):
        self.client.force_login(self.alice)
        response = self.client.get(self.proposal.get_absolute_url())
        self.assertIn("form", response.context)
        self.assertIsNotNone(response.context["proposal_geojson"])
        response = self.client.post(self.proposal.get_absolute_url(), {
            "body": "Trop raide", "location": '{"type": "Point", "coordinates": [2560500, 1205500]}'})
        self.assertRedirects(response, f"{self.proposal.get_absolute_url()}#avis", fetch_redirect_response=False)
        feedback = Feedback.objects.get()
        self.assertEqual((feedback.user, feedback.body), (self.alice, "Trop raide"))
        self.assertEqual(feedback.location.srid, 2056)
        self.assertAlmostEqual(feedback.location.x, 2560500)

    def test_location_is_optional(self):
        self.client.force_login(self.alice)
        self.client.post(self.proposal.get_absolute_url(), {"body": "Sans point", "location": ""})
        self.assertIsNone(Feedback.objects.get().location)

    def test_feedback_is_private(self):
        Feedback.objects.create(proposal=self.proposal, user=self.alice, body="Avis d'Alice")
        self.client.force_login(self.bob)
        response = self.client.get(self.proposal.get_absolute_url())
        self.assertNotContains(response, "Avis d'Alice")
        self.client.force_login(self.alice)
        self.assertContains(self.client.get(self.proposal.get_absolute_url()), "Avis d&#x27;Alice")

    def test_closed_consultation_has_no_form(self):
        self.consultation.opens_on = timezone.localdate() + timedelta(days=1)
        self.consultation.save()
        self.client.force_login(self.alice)
        self.client.post(self.proposal.get_absolute_url(), {"body": "Trop tôt"})
        self.assertFalse(Feedback.objects.exists())


class FileTest(ConsultationTestCase):

    def test_proposal_pdf_can_be_embedded(self):
        self.proposal.file = SimpleUploadedFile("fiche.pdf", b"%PDF-1.4")
        self.proposal.save()
        response = self.client.get(reverse("consultation:proposal_file", args=["vtt", self.proposal.pk]))
        self.assertEqual(response["Content-Type"], "application/pdf")
        self.assertEqual(response["X-Frame-Options"], "SAMEORIGIN")
        self.assertIn("inline", response["Content-Disposition"])
        self.assertContains(self.client.get(self.proposal.get_absolute_url()), "<iframe")

    def test_files_of_unpublished_consultations_are_hidden(self):
        document = ChapterDocument.objects.create(chapter=self.chapter, title="Rapport",
                                                  file=SimpleUploadedFile("rapport.pdf", b"%PDF-1.4"))
        url = reverse("consultation:document_file", args=["vtt", document.pk])
        self.assertEqual(self.client.get(url).status_code, 200)
        self.consultation.is_published = False
        self.consultation.save()
        self.assertEqual(self.client.get(url).status_code, 404)


class AdminExportTest(ConsultationTestCase):

    def setUp(self):
        super().setUp()
        self.admin = get_user_model().objects.create_superuser("admin", "admin@example.org", "x")
        self.client.force_login(self.admin)

    def test_export_feedbacks(self):
        Feedback.objects.create(proposal=self.proposal, user=self.alice, body="Avis CSV")
        response = self.client.post(reverse("admin:consultation_feedback_changelist"), {
            "action": "export_feedbacks", "_selected_action": [f.pk for f in Feedback.objects.all()]})
        content = response.content.decode("utf-8")
        self.assertIn("Avis CSV", content)
        self.assertIn("alice@example.org", content)

    def test_export_questionnaire_responses(self):
        questionnaire, q = self.build_questionnaire()
        self.client.force_login(self.alice)
        self.client.post(reverse("consultation:questionnaire", args=["vtt", self.chapter.pk]), self.valid_answers(q))
        self.client.force_login(self.admin)
        response = self.client.post(reverse("admin:consultation_questionnaire_changelist"), {
            "action": "export_responses", "_selected_action": [questionnaire.pk]})
        content = response.content.decode("utf-8")
        self.assertIn("Autre (Randonneur)", content)
        self.assertIn("Balisage : Non", content)

    def test_admin_pages_render(self):
        questionnaire, q = self.build_questionnaire()
        for url in [reverse("admin:consultation_consultation_change", args=[self.consultation.pk]),
                    reverse("admin:consultation_chapter_change", args=[self.chapter.pk]),
                    reverse("admin:consultation_questionnaire_change", args=[questionnaire.pk]),
                    reverse("admin:consultation_question_change", args=[q["matrix"].pk]),
                    reverse("admin:consultation_proposal_change", args=[self.proposal.pk])]:
            self.assertEqual(self.client.get(url).status_code, 200, url)
