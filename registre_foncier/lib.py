from registre_foncier.models import VJouGrundstTotal



def get_provisory_state(numcad, nummai):
    """
    If a property has an entry in the Journal, it means that
    a mutation is currently affecting it.
    This function checks that.
    """
    sql = (
        VJouGrundstTotal.objects.filter(VJouGrundstTotal.no_immeuble == nummai, VJouGrundstTotal.no_cadastre == numcad)
        .count()
    )

    return sql
