from django.test import SimpleTestCase
from intranet_proxy.session import GeoshopSession
from django.conf import settings


class GeoshopTest(SimpleTestCase):

    def setUp(self) -> None:
        super().setUp()
        self.url = settings.INTRANET_PROXY.get('geoshop_url') + settings.INTRANET_PROXY.get('test_url')
        # Skip if it's not installed
        if __package__ not in settings.INSTALLED_APPS:
            self.skipTest(f"Skipping {__package__}")


    def test_access_internal_metadata(self):
        """
        Simple access to an internal metadata
        """
        internal_session = GeoshopSession()
        response = internal_session.http_get(self.url)
        self.assertEquals(200, response.status_code)

    def test_same_session(self):
        internal_session = GeoshopSession()
        internal_session.http_get(self.url)
        first_access_token = internal_session._get_access_token()
        internal_session2 = GeoshopSession()
        internal_session.http_get(self.url)
        second_access_token = internal_session2._get_access_token()
        self.assertEquals(first_access_token, second_access_token)

    def test_token_expired(self):
        internal_session = GeoshopSession()
        internal_session.http_get(self.url)
        first_access_token = internal_session._get_access_token()
        internal_session._access_token = 'toto'
        response = internal_session.http_get(self.url)
        second_access_token = internal_session._get_access_token()
        self.assertEquals(200, response.status_code)
        self.assertNotEquals(first_access_token, second_access_token)
