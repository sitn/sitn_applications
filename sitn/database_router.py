class TerrisRouter:
    """
    This database router directs database operations for the
    'registre_foncier' app to the 'terris' database for read operations.

    allow_migrate prevents migrations on the 'terris' database and fixes checks that are
    run before lauching tests.
    """

    def db_for_read(self, model, **hints):
        if model._meta.app_label == "registre_foncier":
            return "terris"
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == "registre_foncier":
            return None
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if db == "terris":
            return False
        return None
