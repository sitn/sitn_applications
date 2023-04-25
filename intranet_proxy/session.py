import requests
from django.conf import settings

class GeoshopSession(object):
    """
    Singleton session for storing credentials accross requests
    """
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(GeoshopSession, cls).__new__(cls)
            cls.instance._base_url = settings.INTRANET_PROXY.get('geoshop_url')
            cls.instance._credentials = {
                "username": settings.INTRANET_PROXY.get('geoshop_user'),
                "password": settings.INTRANET_PROXY.get('geoshop_password')
            }
            cls.instance._access_token = None
        return cls.instance

    def _authenticate(self):
        response = requests.post(f'{self._base_url}token/', self._credentials)
        if response.status_code == 200:
            tokens = response.json()
            self._access_token = tokens.get('access')

    def _get_access_token(self):
        if not self._access_token:
            self._authenticate()
        return self._access_token

    def http_get(self, path, retry=0):
        access_token = self._get_access_token()
        headers = {'Authorization': f'Bearer {access_token}'}
        response = requests.get(f'{self._base_url}{path}', headers=headers)
        if response.status_code == 401 and retry == 0:
            self._access_token = None
            return self.http_get(path, 1)
        return response


class VcronApi():
    """
    Helper class to communicate with VCRON
    """
    VCRON_URL = settings.INTRANET_PROXY.get('vcron_url') + \
        '/VisualCron/json/{}?username=' + \
        settings.INTRANET_PROXY.get('vcron_user') + \
        '&password=' + \
        settings.INTRANET_PROXY.get('vcron_password') + \
        '&id={}'

    @classmethod
    def _http_get(cls, url):
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception(f'{str(response.status_code)} {response.text}')
        return response.json()

    @classmethod
    def run_job(cls, guid, vcron_vars):
        url = cls.VCRON_URL.format('Job/Run', guid)
        if vcron_vars:
            url += f'&variables={vcron_vars}'
        return cls._http_get(url)

    @classmethod
    def get_job_stats(cls, guid):
        url = cls.VCRON_URL.format('Job/Get', guid)
        response_data = cls._http_get(url)
        return response_data.get('Stats')
