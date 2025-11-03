import magic
import os

from django.core.exceptions import ValidationError
from django.contrib.gis.db import models
from django.utils.timezone import now

from django_extended_ol.forms.widgets import WMTSWithSearchWidget 

# Define maximum file sizes for PDF's and ZIP's
MAX_PDF_SIZE = 2 * 1024 * 1024  # 2 MB
MAX_ZIP_SIZE = 250 * 1024 * 1024  # 250 MB

def unique_folder_path(instance, filename):
    """ Define the new storage path from login_code
        and prefix the uploaded files with the date
    """
    date_prefix = now().strftime('%Y%m%d_%H%M%S')
    new_filename = f"{date_prefix}.zip"
    return '/'.join([instance.dossier_ppe.login_code, new_filename])

def rename_pdf_accord(instance, filename):
    """ Define the new filename using a date prefix
    """
    date_prefix = now().strftime('%Y%m%d_%H%M%S')
    new_filename = f"{date_prefix}_{filename}"
    return '/'.join(['pdfs', new_filename])

class Geolocalisation(models.Model):
    geom = models.PointField(srid=2056)


class AdresseFacturation(models.Model):
    type_personne = models.CharField(
        choices=(
            ("pp", "Personne physique"),
            ("pm", "Personne morale")
              ),
                max_length=50, default="pp")
    nom_raison_sociale = models.CharField(max_length=150)
    prenom = models.CharField(max_length=100)
    complement = models.CharField(max_length=100, blank=True)
    rue = models.CharField(max_length=100)
    no_rue = models.CharField(max_length=10, blank=True)
    npa = models.IntegerField()
    localite = models.CharField(max_length=100)
    file = models.FileField(upload_to=rename_pdf_accord)

    def __str__(self):
        return self.nom_raison_sociale

    def filename(self):
        return os.path.basename(self.zipfile.name)
    
    def clean(self):
        """
        Custom model-level validation to check the uploaded file.
        """
        # Check if the pdffile field has a value
        if not self.file:
            return  # No file provided, nothing to validate

        # Validate the file size
        self.validate_file_size()

        # Validate the file type (PDF)
        self.validate_pdf_mimetype()

    def validate_file_size(self):
        """
        Validates that the uploaded file does not exceed the maximum allowed size.
        """
        file_size = self.file.size  # Get the size in bytes
        
        if file_size > MAX_PDF_SIZE:
            raise ValidationError(f"Le fichier dépasse la taille maximale autorisée de {MAX_PDF_SIZE / (1024 * 1024)} MB.")

    def validate_pdf_mimetype(self):
        """
        Validates that the uploaded file is a PDF file.
        """
        accept = 'application/pdf'
        file_mime_type = magic.from_buffer(self.file.read(1024), mime=True)
        
        if file_mime_type != accept:
            raise ValidationError("Unsupported file type. Please upload a valid .pdf file.")

    class Meta:
        ordering = ["nom_raison_sociale"]


class ContactPrincipal(models.Model):
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    no_tel = models.CharField(max_length=15)
    raison_sociale = models.CharField(max_length=150, blank=True)

    def __str__(self):
        return self.nom + str(' ') + self.prenom

    class Meta:
        ordering = ["nom"]

class Notaire(models.Model):
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    complement = models.CharField(max_length=100, blank=True)
    rue = models.CharField(max_length=100)
    no_rue = models.CharField(max_length=10, blank=True)
    npa = models.IntegerField()
    localite = models.CharField(max_length=100)

    def __str__(self):
        return self.nom + str(' ') + self.prenom

    class Meta:
        ordering = ["nom"]

class Signataire(models.Model):
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    complement = models.CharField(max_length=100, blank=True)
    rue = models.CharField(max_length=100)
    no_rue = models.CharField(max_length=10, blank=True)
    npa = models.IntegerField()
    localite = models.CharField(max_length=100)

    def __str__(self):
        return self.nom + str(' ') + self.prenom

    class Meta:
        ordering = ["nom"]

class DossierPPE(models.Model):
    login_code = models.CharField(max_length=16)
    cadastre = models.CharField(max_length=50)
    numcad = models.IntegerField()
    nummai = models.CharField(max_length=10)
    coord_E = models.IntegerField()
    coord_N = models.IntegerField()
    statut = models.CharField(
        choices=(
            ("P", "En projet"),
            ("S", "Soumis"),
            ("T", "En traitement"),
            ("R","Rejeté")
        ),
        default="P", max_length=20)
    type_dossier = models.CharField(
        choices=(
            ("C", "Constitution"),
            ("R", "Révision"),
            ("M", "Modification")
        ),
        max_length=20)
    revision_jouissances = models.CharField(max_length=3, default=None, blank=True)
    elements_rf_identiques = models.CharField(max_length=3, default=None, blank=True)
    nouveaux_droits = models.CharField(max_length=3, default=None, blank=True)
    ref_geoshop = models.CharField(max_length=20, default=None, blank=True)
    ref_dossier_initial = models.IntegerField(null=True)
    contact_principal = models.ForeignKey(ContactPrincipal, on_delete=models.CASCADE)
    signataire = models.ForeignKey(Signataire, on_delete=models.CASCADE)
    notaire = models.ForeignKey(Notaire, on_delete=models.CASCADE)
    adresse_facturation = models.ForeignKey(AdresseFacturation, on_delete=models.CASCADE)
    date_creation = models.DateTimeField("Date de création", auto_now=True)
    date_soumission = models.DateTimeField("Date de soumission", auto_now=True, blank=True)
    date_validation = models.DateTimeField("Date de validation", auto_now=True, blank=True)
    geom = models.PointField(srid=2056)


class Zipfile(models.Model):
    zipfile = models.FileField(upload_to=unique_folder_path)
    upload_date = models.DateTimeField("Date de chargement", auto_now=True)
    file_statut = models.CharField(
        choices=(
            ("CMA", "Contrôle automatique : archivé"),
            ("CAC", "Contrôle automatique : en cours"),
            ("CAE", "Contrôle automatique : erreurs à corriger"),
            ("ERR", "Contrôle automatique : erreur interne"),
            ("CAV", "Contrôle automatique : validé"),
            ("CMC", "Contrôle manuel : en cours"),
            ("CME", "Contrôle manuel : erreurs à corriger"),
            ("CMV", "Contrôle manuel : validé"),
            ("DPV", "Dossier papier validé"),
        ),
        max_length=3, default="CAC")
    dossier_ppe = models.ForeignKey(DossierPPE, on_delete=models.CASCADE, blank=True)

    def filename(self):
        return os.path.basename(self.zipfile.name)
    
    def clean(self):
        """
        Custom model-level validation to check the uploaded file.
        """
        # Check if the zipfile field has a value
        if not self.zipfile:
            return  # No file provided, nothing to validate

        # Validate the file size
        self.validate_file_size()

        # Validate the file type (ZIP)
        self.validate_zip_mimetype()

    def validate_file_size(self):
        """
        Validates that the uploaded file does not exceed the maximum allowed size.
        """
        file_size = self.zipfile.size  # Get the size in bytes
        
        if file_size > MAX_ZIP_SIZE:
            raise ValidationError(f"Le fichier dépasse la taille maximale autorisée de {MAX_ZIP_SIZE / (1024 * 1024)} MB.")

    def validate_zip_mimetype(self):
        """
        Validates that the uploaded file is a zip file.
        """
        accept = 'application/zip'
        file_mime_type = magic.from_buffer(self.zipfile.read(1024), mime=True)
        
        if file_mime_type != accept:
            raise ValidationError("Unsupported file type. Please upload a valid .zip file.")
