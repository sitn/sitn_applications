from registre_foncier.models import VJouGrundstTotal


def get_provisory_state(numcad, nummai):
    """
    If a property has an entry in the Journal, it means that
    a mutation is currently affecting it.
    This function checks that.
    """

    nummai = nummai.replace('#', '').strip()

    sql = VJouGrundstTotal.objects.filter(no_immeuble=nummai, no_cadastre=numcad).count()

    if sql == 0:
        return False
    else:
        return True
