from django.http import HttpResponse
from django.template import loader
from django.shortcuts import get_object_or_404

from intranet_proxy.session import GeoshopSession, VcronApi
from intranet_proxy.models import VcronRoute

def get_metadata(request, path):
    geoshop_session = GeoshopSession()
    response = geoshop_session.http_get(f'metadata/{path}')
    return HttpResponse(response.content)

def vcron_proxy_index(request):
    template = loader.get_template('intranet_proxy/vcron_index.html')
    return HttpResponse(template.render({}, request))

def vcron_proxy_run(request, task_name):
    route = get_object_or_404(VcronRoute, url=task_name)

    stats = VcronApi.get_job_stats(route.vcron_guid)

    execution_time = stats['ExecutionTime']

    vcron_vars = request.GET.get('variables')
    response_data = VcronApi.run_job(route.vcron_guid, vcron_vars)

    status = 'ok'
    if response_data.get('JobStartedResult') != 1:
        status = 'ko'

    template = loader.get_template('intranet_proxy/vcron_task.html')
    return HttpResponse(
        template.render({
            "task_guid": route.vcron_guid,
            "status": status,
            "execution_time": execution_time
        }, request)
    )

def vcron_proxy_status(request, task_guid):
    stats = VcronApi.get_job_stats(task_guid)
    if stats['Status'] == 0:
        return HttpResponse('Running')
    if stats['Status'] == 1:
        if stats['ExitCode'] == 0:
            return HttpResponse('Done')
    return HttpResponse('Error')
