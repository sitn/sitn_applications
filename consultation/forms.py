from django.conf import settings
from django.contrib.gis import forms
from django.core.exceptions import ValidationError
from django_extended_ol.forms.widgets import WMTSWidget

from .models import Answer, Feedback, Question


class FeedbackForm(forms.ModelForm):
    location = forms.PointField(
        srid=settings.DEFAULT_SRID, required=False, label="Localisation (facultatif)",
        help_text="Cliquez sur la carte pour situer votre avis.")

    class Meta:
        model = Feedback
        fields = ["body", "location"]
        widgets = {"body": forms.Textarea(attrs={"rows": 5, "class": "form-control"})}
        labels = {"body": "Votre avis"}

    def __init__(self, *args, proposal=None, **kwargs):
        super().__init__(*args, **kwargs)
        attrs = {}
        # Open the map on the proposal instead of the default canton view
        if proposal is not None and proposal.geom:
            centroid = proposal.geom.centroid
            attrs["default_map_center"] = [round(centroid.x, 2), round(centroid.y, 2)]
        self.fields["location"].widget = WMTSWidget(attrs=attrs)


class QuestionnaireForm(forms.Form):
    """
    Fields are built from the questions: ``q<id>`` per question, ``q<id>_r<row>`` per matrix row,
    ``q<id>_o<option>`` per sorting rank or free-text option.
    A previous ``response`` pre-fills the form; ``disabled`` makes it read-only.
    """

    def __init__(self, *args, questionnaire, response=None, disabled=False, **kwargs):
        if response is not None:
            kwargs["initial"] = self._initial_from(response)
        super().__init__(*args, **kwargs)
        self.questions = list(questionnaire.questions.prefetch_related("options", "matrix_rows"))
        for question in self.questions:
            self._add_fields(question)
        for field in self.fields.values():
            field.disabled = disabled

    @staticmethod
    def _initial_from(response):
        """Field values of a saved response, the reverse of ``save``."""
        initial = {}
        for answer in response.answers.select_related("question"):
            question = answer.question
            name = f"q{question.pk}"
            kind = question.question_type
            if kind in (Question.SHORT_RESPONSE, Question.LONG_RESPONSE):
                initial[name] = answer.text
            elif kind in (Question.SINGLE_OPTION, Question.MULTIPLE_OPTION):
                selected = [str(c["option"]) for c in answer.choices]
                initial[name] = selected[0] if kind == Question.SINGLE_OPTION and selected else selected
                for choice in answer.choices:
                    if choice.get("text"):
                        initial[f"{name}_o{choice['option']}"] = choice["text"]
            elif kind == Question.SORTING:
                for choice in answer.choices:
                    initial[f"{name}_o{choice['option']}"] = str(choice["position"])
            elif kind == Question.MATRIX_SINGLE:
                for choice in answer.choices:
                    initial[f"{name}_r{choice['row']}"] = str(choice["option"])
            elif kind == Question.MATRIX_MULTIPLE:
                for choice in answer.choices:
                    initial.setdefault(f"{name}_r{choice['row']}", []).append(str(choice["option"]))
        return initial

    def _add_fields(self, question):
        name = f"q{question.pk}"
        required = question.mandatory
        options = list(question.options.all())
        choices = [(str(o.pk), o.body) for o in options]
        kind = question.question_type

        if kind == Question.SHORT_RESPONSE:
            self.fields[name] = forms.CharField(
                label=question.body, required=required, max_length=question.max_characters or None,
                widget=forms.TextInput(attrs={"class": "form-control"}))
        elif kind == Question.LONG_RESPONSE:
            self.fields[name] = forms.CharField(
                label=question.body, required=required, max_length=question.max_characters or None,
                widget=forms.Textarea(attrs={"class": "form-control", "rows": 4}))
        elif kind == Question.SINGLE_OPTION:
            self.fields[name] = forms.ChoiceField(
                label=question.body, required=required, choices=choices, widget=forms.RadioSelect)
        elif kind == Question.MULTIPLE_OPTION:
            self.fields[name] = forms.MultipleChoiceField(
                label=question.body, required=required, choices=choices, widget=forms.CheckboxSelectMultiple)
        elif kind == Question.SORTING:
            ranks = [("", "—")] + [(str(i), str(i)) for i in range(1, len(options) + 1)]
            for option in options:
                self.fields[f"{name}_o{option.pk}"] = forms.ChoiceField(
                    label=option.body, required=required, choices=ranks,
                    widget=forms.Select(attrs={"class": "form-select form-select-sm w-auto"}))
        elif question.is_matrix:
            field_class = forms.ChoiceField if kind == Question.MATRIX_SINGLE else forms.MultipleChoiceField
            widget = forms.RadioSelect if kind == Question.MATRIX_SINGLE else forms.CheckboxSelectMultiple
            for row in question.matrix_rows.all():
                self.fields[f"{name}_r{row.pk}"] = field_class(
                    label=row.body, required=required, choices=choices, widget=widget)

        if kind in (Question.SINGLE_OPTION, Question.MULTIPLE_OPTION):
            for option in options:
                if option.free_text:
                    self.fields[f"{name}_o{option.pk}"] = forms.CharField(
                        label=f"Précisez ({option.body})", required=False,
                        widget=forms.TextInput(attrs={"class": "form-control form-control-sm"}))

    def items(self):
        """(question, [bound fields]) in display order, for the template."""
        for question in self.questions:
            prefix = f"q{question.pk}"
            fields = [self[name] for name in self.fields if name == prefix or name.startswith(prefix + "_")]
            yield question, fields

    def clean(self):
        cleaned = super().clean()
        for question in self.questions:
            name = f"q{question.pk}"
            if question.question_type == Question.MULTIPLE_OPTION and question.max_choices:
                if len(cleaned.get(name) or []) > question.max_choices:
                    self.add_error(name, f"Choisissez au maximum {question.max_choices} option(s).")
            elif question.question_type == Question.MATRIX_MULTIPLE and question.max_choices:
                for row in question.matrix_rows.all():
                    if len(cleaned.get(f"{name}_r{row.pk}") or []) > question.max_choices:
                        self.add_error(f"{name}_r{row.pk}", f"Choisissez au maximum {question.max_choices} option(s).")
            elif question.question_type == Question.SORTING:
                ranks = [cleaned.get(f"{name}_o{o.pk}") for o in question.options.all()]
                given = [r for r in ranks if r]
                if len(given) != len(set(given)):
                    raise ValidationError(f"« {question.body} » : chaque rang ne peut être utilisé qu'une fois.")
        return cleaned

    def save(self, response):
        """Store one Answer per answerable question of ``response``."""
        data = self.cleaned_data
        answers = []
        for question in self.questions:
            if question.is_display_only:
                continue
            name = f"q{question.pk}"
            text, choices = "", []
            kind = question.question_type
            if kind in (Question.SHORT_RESPONSE, Question.LONG_RESPONSE):
                text = data.get(name, "")
            elif kind in (Question.SINGLE_OPTION, Question.MULTIPLE_OPTION):
                selected = data.get(name) or []
                for option_id in [selected] if isinstance(selected, str) else selected:
                    if option_id:
                        choices.append({"option": int(option_id), "text": data.get(f"{name}_o{option_id}", "")})
            elif kind == Question.SORTING:
                for option in question.options.all():
                    if rank := data.get(f"{name}_o{option.pk}"):
                        choices.append({"option": option.pk, "position": int(rank)})
            elif question.is_matrix:
                for row in question.matrix_rows.all():
                    selected = data.get(f"{name}_r{row.pk}") or []
                    for option_id in [selected] if isinstance(selected, str) else selected:
                        if option_id:
                            choices.append({"option": int(option_id), "row": row.pk})
            if text or choices:
                answers.append(Answer(response=response, question=question, text=text, choices=choices))
        Answer.objects.bulk_create(answers)
