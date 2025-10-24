import magic
import phonenumbers

from django.contrib.gis import forms
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django_extended_ol.forms.widgets import WMTSWithSearchWidget

from .models import DossierPPE, Geolocalisation, AdresseFacturation, Zipfile
from .models import ContactPrincipal, Notaire, Signataire

from django.utils.translation import gettext_lazy as _

zip_validator = FileExtensionValidator('zip')
pdf_validator = FileExtensionValidator('pdf')


def validate_phone_number(phone):
    """ Check if the phone number is valid for a selection of european countries """
    country_codes = ['CH', 'FR', 'DE', 'IT', 'ES']  # Country codes to check
    
    for country_code in country_codes:
        try:
            # Parse the phone number for each country code
            parsed_number = phonenumbers.parse(phone, country_code)
            
            if phonenumbers.is_valid_number(parsed_number):
                return  # If valid, return and stop further checks
            
        except phonenumbers.phonenumberutil.NumberParseException:
            continue  # If parsing fails for this country code, try the next one
    
    # If no valid number is found for any of the countries
    raise ValidationError("Numéro de téléphone invalide. Format attendu: +41 79 123 45 67, +33 ... (FR), ou +49 ... (DE)")

def validate_npa(npa):
    if not isinstance(npa, int):
        raise ValidationError(_("La NPA doit être un entier à quatre chiffres"))
    if npa < 1000 or npa > 9999:
        raise ValidationError(_("La NPA doit faire partie de l'intervalle 1000 à 9999."))
    
class ZipfileForm(forms.ModelForm):
    class Meta:
        model = Zipfile
        prefix = "zip"
        fields = "__all__"
        widgets = {
            'upload_date': forms.HiddenInput(),
            'file_statut': forms.HiddenInput(),
            'dossier_ppe': forms.HiddenInput(),
            'zipfile': forms.FileInput(
                attrs={'accept': '.zip,application/zip', 'placeholder': 'Choisir un dossier .zip','class': 'form-control placeholder'}
            ),
        }
        labels = {
            "zipfile": _("Dossier *.zip"),
        }

class GeolocalisationForm(forms.ModelForm):
    geom = forms.PointField(widget=WMTSWithSearchWidget(attrs={"geom": ""}), label=False)
    class Meta: 
        model = Geolocalisation
        fields = "__all__"

class AdresseFacturationForm(forms.ModelForm):
    class Meta:
        model = AdresseFacturation
        prefix = "facturation"
        fields = "__all__"
        labels = {
            "type_personne": _("Type *"),
            "nom_raison_sociale": _("Nom/Raison sociale *"),
            "prenom": _("Prénom/A l'att. *"),
            "complement": _("Complément/Réf."),
            "rue": _("Rue *"),
            "no_rue": _("No."),
            "npa": _("NPA *"),
            "localite": _("Localité *"),
            "file": _("Accord de prise en charge *"),
        }
        widgets = {
            'type_personne': forms.Select(attrs={"class": "form-select"}),
            'nom_raison_sociale': forms.TextInput(attrs={"placeholder": "Nom ou raison sociale", "class": "form-control placeholder"}),
            "prenom": forms.TextInput(attrs={"placeholder": "Prénom", "class": "form-control placeholder"}),
            "complement": forms.TextInput(attrs={"placeholder": "(Case postale, appt., unité)", "class": "form-control placeholder"}),
            "rue": forms.TextInput(attrs={"placeholder": "Rue du 1er Mars", "class": "form-control placeholder"}),
            "no_rue": forms.TextInput(attrs={"placeholder": "(17B)", "class": "form-control placeholder"}),
            "npa": forms.TextInput(attrs={"placeholder": "1000 - 9999", 'validators':[validate_npa], "class": "form-control placeholder"}),
            "localite": forms.TextInput(attrs={"placeholder": "Localité", "class": "form-control placeholder"}),
            'file': forms.FileInput(attrs={'accept': '.pdf,application/pdf', 'validators':[pdf_validator], "class": "form-control placeholder"}),
            }
        #help_texts = {
        #    "complement": _("Case postale, appt., unité, etc."),
        #    "file": _("Document"),
        #}
        error_messages = {
            "complement": {
                "max_length": _("Le contenu du champ est trop long."),
            },
        }

    def clean_npa(self):
        npa = self.cleaned_data.get("npa")
        if not isinstance(npa, int):
            raise forms.ValidationError("Veuillez entrer une NPA suisse valide.")
        return npa
    
#    def clean_file(self):
#        filename = self.cleaned_data.get("filename")
#        print(filename)
#        return filename


class ContactPrincipalForm(forms.ModelForm):
    class Meta:
        model = ContactPrincipal
        prefix="contact"
        fields = fields = "__all__"
        labels = {
            "nom": _("Nom *"),
            "prenom": _("Prénom *"),
            "email": _("E-mail *"),
            "no_tel": _("Téléphone *"),
            "raison_sociale": _("Raison sociale"),
        }
        widgets = {
            "nom": forms.TextInput(attrs={"placeholder": "Nom de famille", "class": "form-control placeholder"}),
            "prenom": forms.TextInput(attrs={"placeholder": "Prénom", "class": "form-control placeholder"}),
            "email": forms.EmailInput(attrs={"placeholder": "exemple@domaine.com", "class": "form-control placeholder"}),
            "no_tel": forms.TextInput(attrs={"placeholder": "(+41 79 123 45 67)", 'validators':[validate_phone_number], "class": "form-control placeholder"}),
            "raison_sociale": forms.TextInput(attrs={"placeholder": "(Exemple SA)", "class": "form-control placeholder"})
        }

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if not email:
            raise forms.ValidationError("Veuillez entrer une adresse mail valide.")
        return email


class NotaireForm(forms.ModelForm):
    class Meta:
        model = Notaire
        prefix="notaire"
        fields = fields = "__all__"
        labels = {
            "nom": _("Nom *"),
            "prenom": _("Prénom *"),
            "complement": _("Complément"),
            "rue": _("Rue *"),
            "no_rue": _("No."),
            "npa": _("NPA *"),
            "localite": _("Localité *"),
        }
        widgets = {
            "nom": forms.TextInput(attrs={"placeholder": "Nom de famille", "class": "form-control placeholder"}),
            "prenom": forms.TextInput(attrs={"placeholder": "Prénom", "class": "form-control placeholder"}),
            "complement": forms.TextInput(attrs={"placeholder": "(Case postale, appt., unité)", "class": "form-control placeholder"}),
            "rue": forms.TextInput(attrs={"placeholder": "Rue du 1er Mars", "class": "form-control placeholder"}),
            "no_rue": forms.TextInput(attrs={"placeholder": "(17B)", "class": "form-control placeholder"}),
            "npa": forms.TextInput(attrs={"placeholder": "1000 - 9999", 'validators':[validate_npa], "class": "form-control placeholder"}),
            "localite": forms.TextInput(attrs={"placeholder": "Localité", "class": "form-control placeholder"}),
        }

class SignataireForm(forms.ModelForm):
    class Meta:
        model = Signataire
        prefix="signataire"
        fields = "__all__"
        labels = {
            "nom": _("Nom *"),
            "prenom": _("Prénom *"),
            "complement": _("Complément"),
            "rue": _("Rue *"),
            "no_rue": _("No."),
            "npa": _("NPA *"),
            "localite": _("Localité *"),
        }
        widgets = {
            "nom": forms.TextInput(attrs={"placeholder": "Nom de famille", "class": "form-control placeholder"}),
            "prenom": forms.TextInput(attrs={"placeholder": "Prénom", "class": "form-control placeholder"}),
            "complement": forms.TextInput(attrs={"placeholder": "(Case postale, appt., unité)", "class": "form-control placeholder"}),
            "rue": forms.TextInput(attrs={"placeholder": "Rue du 1er Mars", "class": "form-control placeholder"}),
            "no_rue": forms.TextInput(attrs={"placeholder": "(17B)", "class": "form-control placeholder"}),
            "npa": forms.TextInput(attrs={"placeholder": "1000 - 9999", 'validators':[validate_npa], "class": "form-control placeholder"}),
            "localite": forms.TextInput(attrs={"placeholder": "Localité", "class": "form-control placeholder"}),
        }

class DossierPPEForm(forms.ModelForm):
    geom = forms.PointField(widget=WMTSWithSearchWidget())
    class Meta: 
        model = DossierPPE
        fields = [
            'cadastre',
            'numcad',
            'nummai',
            'coord_E',
            'coord_N',
            'statut',
            'type_dossier',
            'contact_principal',
            'signataire',
            'notaire',
            'adresse_facturation',
            #'date_creation',
            #'date_soumission',
            #'date_validation,
        ]