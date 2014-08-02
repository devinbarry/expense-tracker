# coding=utf-8
from __future__ import absolute_import, unicode_literals, print_function, division
from tastypie.test import ResourceTestCase
from django.contrib.auth.models import User


class UserResourceTest(ResourceTestCase):
    # Use ``fixtures`` & ``urls`` as normal. See Django's ``TestCase`` documentation for the gory details.
    fixtures = ['user.json']

    def setUp(self):
        super(UserResourceTest, self).setUp()

        self.base_url = '/api/v1/user/'
        self.auth_url = self.base_url + 'authenticate/'
        self.reg_url = self.base_url + 'register/'

        # The data we'll send on POST requests. Again, because we'll use it frequently (enough).
        self.reg_post_data = {
            'username': 'jamesl',
            'first_name': 'James',
            'last_name': 'Lin',
            'email': 'jamesl@test.com',
            'password': 'jamesl'
        }

        # This username and password matches a user record in the fixtures
        self.auth_post_data = {
            'username': 'jamesw',
            'password': 'jamesw',
        }

    def test_get_schema(self):
        resp = self.api_client.get('/api/v1/user/schema/', format='json')
        self.assertValidJSONResponse(resp)

    def test_get_user_list(self):
        # Should return 405 when we try to GET the list of users
        self.assertHttpMethodNotAllowed(self.api_client.get(self.base_url, format='json'))

    def test_post_user_list(self):
        # Should return 405 when we try to POST the list of users
        self.assertHttpMethodNotAllowed(self.api_client.post(self.base_url, format='json', data=self.reg_post_data))

    def test_delete_user_list(self):
        self.assertHttpMethodNotAllowed(self.api_client.delete(self.base_url, format='json'))

    def test_put_user_list(self):
        self.assertHttpMethodNotAllowed(self.api_client.put(self.base_url, format='json', data={}))

    def test_get_user_detail(self):
        # Should return 405 when we try to GET the detail for a specific user
        self.assertHttpMethodNotAllowed(self.api_client.get(self.base_url + '1/', format='json'))

    def test_get_user_authenticate(self):
        # Should return 405 when we try to GET the auth URI
        self.assertHttpMethodNotAllowed(self.api_client.get(self.auth_url, format='json'))

    def test_post_user_authenticate(self):
        resp = self.api_client.post(self.auth_url, format='json', data=self.auth_post_data)
        self.assertHttpOK(resp)
        self.assertValidJSONResponse(resp)
        data = self.deserialize(resp)

        # Check that the response contains our expected data
        self.assertKeys(data, ['api_key', 'first_name', 'last_name', 'success', 'username'])
        self.assertEqual(data['username'], 'jamesw')
        self.assertEqual(data['success'], True)

    def test_delete_user_authenticate(self):
        self.assertHttpMethodNotAllowed(self.api_client.delete(self.auth_url, format='json'))

    def test_put_user_authenticate(self):
        self.assertHttpMethodNotAllowed(self.api_client.put(self.auth_url, format='json', data={}))

    def test_get_user_register(self):
        # Should return 405 when we try to GET the register URI
        self.assertHttpMethodNotAllowed(self.api_client.get(self.reg_url, format='json'))

    def test_post_user_register(self):
        # Check how many are there first.
        self.assertEqual(User.objects.count(), 4)

        resp = self.api_client.post(self.reg_url, format='json', data=self.reg_post_data)
        self.assertHttpOK(resp)

        # Verify a new one has been added.
        self.assertEqual(User.objects.count(), 5)

    def test_delete_user_register(self):
        self.assertHttpMethodNotAllowed(self.api_client.delete(self.reg_url, format='json'))

    def test_put_user_register(self):
        self.assertHttpMethodNotAllowed(self.api_client.put(self.reg_url, format='json', data={}))
