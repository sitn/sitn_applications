import uuid

from django.contrib.gis.db import models
from django.utils.timezone import now

from django_extended_ol.forms.widgets import WMTSWithSearchWidget 


class ZipFile(models.Model):
    zipfile = models.FileField(upload_to="files/zips/")

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
    file = models.FileField(upload_to="files/")

    def __str__(self):
        return self.nom_raison_sociale

    class Meta:
        ordering = ["nom_raison_sociale"]


class ContactPrincipal(models.Model):
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
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
    contact_principal = models.ForeignKey(ContactPrincipal, on_delete=models.CASCADE)
    signataire = models.ForeignKey(Signataire, on_delete=models.CASCADE)
    notaire = models.ForeignKey(Notaire, on_delete=models.CASCADE)
    adresse_facturation = models.ForeignKey(AdresseFacturation, on_delete=models.CASCADE)
    date_creation = models.DateTimeField("Date de création", auto_now=True)
    date_soumission = models.DateTimeField("Date de soumission", auto_now=True, blank=True)
    date_validation = models.DateTimeField("Date de validation", auto_now=True, blank=True)
    geom = models.PointField(srid=2056)