from django.db import models

class CATSAllYears(models.Model):
    idobj = models.CharField(max_length=200, primary_key=True, null=False)
    nom = models.CharField(max_length=200)
    matricule = models.IntegerField()
    date = models.DateField()
    imputation = models.CharField(max_length=200)
    texte_imputation = models.CharField(max_length=200)
    element_otp_recepteur = models.CharField(max_length=200)
    ordre_recepteur = models.CharField(max_length=200)
    recepteur_general = models.CharField(max_length=200)
    imputation_multiple = models.CharField(max_length=200)
    nombre_heure = models.FloatField()
    unite_mesure_interne = models.CharField(max_length=200)
    designation = models.CharField(max_length=200)
    type_activite = models.CharField(max_length=200)
    cat_absence_pres = models.IntegerField()
    societe = models.CharField(max_length=200)
    cree_le = models.DateField()
    heure_de_saisie = models.TimeField()
    cree_par = models.CharField(max_length=200)
    derniere_modificat = models.DateField()
    modifie_a = models.TimeField()
    modifie_par = models.CharField(max_length=200)
    autorise_par = models.CharField(max_length=200)
    date_autorisation = models.DateField()
    nom_prenom = models.CharField(max_length=200)
    centre_emetteur = models.IntegerField()
    username = models.CharField(max_length=500)

    class Meta:
        db_table = 'cockpit_sgrf\".\"cats_toutes_annees'
        managed = False
    
    def year():
        return 