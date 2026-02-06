from django.db.models import Func, JSONField

class JsonBuildObject(Func):
    output_field = JSONField()
    function = 'json_build_object'