from django.db import models
from django.utils.timezone import now


class DossierPPE(models.Model):
    id_dossier = models.CharField(max_length=200, primary_key = True)
    token = models.CharField(max_length=200)
    egrid = models.CharField(max_length=14)
    cadastre = models.CharField(max_length=50)
    numcad = models.IntegerField()
    nummai = models.CharField(max_length=10)
    coord_E = models.IntegerField()
    coord_N = models.IntegerField()
    statut = models.CharField(max_length=20)
    date_creation = models.DateTimeField("Date de création", auto_now=True)


class Contact(models.Model):
    id_contact = models.IntegerField(primary_key = True)
    type_contact = models.CharField(max_length=50)
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    nom_entreprise = models.CharField(max_length=100)
    departement = models.CharField(max_length=100)
    complement = models.CharField(max_length=100)
    rue = models.CharField(max_length=100)
    no_rue = models.CharField(max_length=10)
    npa = models.IntegerField()
    localite = models.CharField(max_length=100)
    pays= models.CharField(max_length=30)


class Role(models.Model):
    role = models.CharField(max_length=30)
    dossier = models.ForeignKey(DossierPPE, on_delete=models.CASCADE)
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE)