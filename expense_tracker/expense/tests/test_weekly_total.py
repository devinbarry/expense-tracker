# coding=utf-8
from __future__ import absolute_import, unicode_literals, print_function, division
from django.contrib.auth.models import User
from tastypie.test import ResourceTestCase


class WeeklyTotalResourceTest(ResourceTestCase):
    # WeeklyTotal depends upon the existence of expenses
    fixtures = ['user.json', 'expenses.json']

    def setUp(self):
        super(WeeklyTotalResourceTest, self).setUp()

        # Create a user.
        self.username = 'devinb'
        self.user = User.objects.get(username=self.username)

        self.base_url = '/api/v1/weeklytotal/'
        self.detail_url = self.base_url + '1/'

        # The data we'll send on POST requests. Again, because we'll use it frequently (enough).
        self.post_data = {
            'description': 'Tastypie test expense',
            'amount': 87,
            'date': '2012-05-01T22:05:12'
        }

    def get_credentials(self):
        """
        Creates and returns the HTTP Authorization header for use
        with ApiKeyAuthentication.
        """
        return self.create_apikey(username=self.username, api_key=self.user.api_key.key)

    def test_get_schema(self):
        resp = self.api_client.get(self.base_url + 'schema/', format='json', authentication=self.get_credentials())
        self.assertValidJSONResponse(resp)

    def test_get_list_unauthorized(self):
        self.assertHttpUnauthorized(self.api_client.get(self.base_url, format='json'))

    def test_get_list_json(self):
        resp = self.api_client.get(self.base_url, format='json', authentication=self.get_credentials())
        self.assertValidJSONResponse(resp)
        # Fetch the objects data from the response
        objects = self.deserialize(resp)['objects']
        # Check that all the keys we expect are in the returned data
        self.assertKeys(objects[0], ['count', 'average', 'year', 'week_number', 'total', 'start_date', 'resource_uri'])

    def test_get_detail_unauthenticated(self):
        self.assertHttpMethodNotAllowed(self.api_client.get(self.detail_url, format='json'))

    def test_get_detail_json(self):
        self.assertHttpMethodNotAllowed(self.api_client.get(self.detail_url, format='json',
                                                            authentication=self.get_credentials()))

    def test_post_list_unauthenticated(self):
        self.assertHttpMethodNotAllowed(self.api_client.post(self.base_url, format='json', data=self.post_data))

    def test_post_list(self):
        self.assertHttpMethodNotAllowed(self.api_client.post(self.base_url, format='json', data=self.post_data,
                                                             authentication=self.get_credentials()))

    def test_put_detail_unauthenticated(self):
        self.assertHttpMethodNotAllowed(self.api_client.put(self.detail_url, format='json', data={}))

    def test_put_detail(self):
        self.assertHttpMethodNotAllowed(self.api_client.get(self.detail_url, format='json',
                                                            authentication=self.get_credentials()))

    def test_delete_detail_unauthenticated(self):
        self.assertHttpMethodNotAllowed(self.api_client.delete(self.detail_url, format='json'))

    def test_delete_detail(self):
        self.assertHttpMethodNotAllowed(self.api_client.delete(self.detail_url, format='json',
                                                               authentication=self.get_credentials()))
