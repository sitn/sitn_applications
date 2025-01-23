from django.contrib.gis.db import models
from django.utils.timezone import now

from django_extended_ol.forms.widgets import WMTSWidget

class Geolocalisation(models.Model):
    geom = models.PointField(srid=2056)

class Document(models.Model):
    nom_document = models.CharField(max_length=150)
    file = models.FileField()

    def __str__(self):
        return self.nom_document

class AdresseFacturation(models.Model):
    type_personne = models.CharField(
        choices=(
            ("pp", "Personne physique"),
            ("pm", "Personne morale")
              ),
                max_length=50, default="pp")
    nom_raison_sociale = models.CharField(max_length=150)
    prenom = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    no_tel = models.CharField(max_length=15)
    complement = models.CharField(max_length=100, blank=True)
    rue = models.CharField(max_length=100)
    no_rue = models.CharField(max_length=10, blank=True)
    npa = models.IntegerField()
    localite = models.CharField(max_length=100)
    pays= models.CharField(max_length=50)

    def __str__(self):
        return self.nom_raison_sociale

    class Meta:
        ordering = ["nom_raison_sociale"]


class ContactPrincipal(models.Model):
    politesse = models.CharField(
        choices=(
            ("M", "Monsieur"),
            ("Mme", "Madame"),
            ("Me", "Maître"),
            ("A", "")
            ),
            max_length=30, default="A")
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    raison_sociale = models.CharField(max_length=150)
    email = models.CharField(max_length=100)
    no_tel = models.CharField(max_length=15)
    complement = models.CharField(max_length=100, blank=True)
    rue = models.CharField(max_length=100)
    no_rue = models.CharField(max_length=10, blank=True)
    npa = models.IntegerField()
    localite = models.CharField(max_length=100)
    pays= models.CharField(max_length=50)

    def __str__(self):
        return self.nom

    class Meta:
        ordering = ["nom"]

class Notaire(models.Model):
    politesse = models.CharField(default="Me", max_length=2)
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    raison_sociale = models.CharField(max_length=150)
    email = models.CharField(max_length=100)
    no_tel = models.CharField(max_length=15)
    complement = models.CharField(max_length=100, blank=True)
    rue = models.CharField(max_length=100)
    no_rue = models.CharField(max_length=10, blank=True)
    npa = models.IntegerField()
    localite = models.CharField(max_length=100)
    pays= models.CharField(max_length=50)

    def __str__(self):
        return self.nom

    class Meta:
        ordering = ["nom"]

class Signataire(models.Model):
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    raison_sociale = models.CharField(max_length=150)
    email = models.CharField(max_length=100)
    no_tel = models.CharField(max_length=15)
    complement = models.CharField(max_length=100, blank=True)
    rue = models.CharField(max_length=100)
    no_rue = models.CharField(max_length=10, blank=True)
    npa = models.IntegerField()
    localite = models.CharField(max_length=100)
    pays= models.CharField(max_length=50)

    def __str__(self):
        return self.nom

    class Meta:
        ordering = ["nom"]

class DossierPPE(models.Model):
    id_unique = models.CharField(max_length=200)
    egrid = models.CharField(max_length=14, blank=True)
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
        max_length=20)
    type_dossier = models.CharField(
        choices=(
            ("C", "Constitution"),
            ("R", "Révision"),
            ("M", "Modification")
        ),
        max_length=20)
    contact_principal = models.ForeignKey(ContactPrincipal, on_delete=models.CASCADE)
    signataire = models.ForeignKey(Signataire, on_delete=models.CASCADE)
    notaire = models.ForeignKey(Notaire, on_delete=models.CASCADE)
    adresse_facturation = models.ForeignKey(AdresseFacturation, on_delete=models.CASCADE)
    accord_frais = models.ForeignKey(Document, on_delete=models.CASCADE)
    date_creation = models.DateTimeField("Date de création", auto_now=True)
    date_soumission = models.DateTimeField("Date de soumission", auto_now=True, blank=True)
    date_validation = models.DateTimeField("Date de validation", auto_now=True, blank=True)
    geom = models.PointField(srid=2056)