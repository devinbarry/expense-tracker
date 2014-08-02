# coding=utf-8
from __future__ import absolute_import, unicode_literals, print_function, division
import datetime
from pytz import timezone
from django.contrib.auth.models import User
from tastypie.test import ResourceTestCase
from expense.models import Expense


class ExpenseResourceTest(ResourceTestCase):
    # Use ``fixtures`` & ``urls`` as normal. See Django's ``TestCase`` documentation for the gory details.
    fixtures = ['user.json', 'expenses.json']

    def setUp(self):
        super(ExpenseResourceTest, self).setUp()

        # Create a user.
        self.username = 'devinb'
        self.user = User.objects.get(username=self.username)

        # Fetch the ``Expense`` object we'll use in testing.
        # Note that we aren't using PKs because they can change depending on what other tests are running.
        self.expense1 = Expense.objects.get(pk=1)
        self.expense3 = Expense.objects.get(pk=3)

        # We also build a detail URI, since we will be using it all over. DRY, baby. DRY.
        self.detail_url = '/api/v1/expense/{0}/'.format(self.expense3.pk)

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
        resp = self.api_client.get('/api/v1/expense/schema/', format='json', authentication=self.get_credentials())
        self.assertValidJSONResponse(resp)

    def test_get_list_unauthorized(self):
        self.assertHttpUnauthorized(self.api_client.get('/api/v1/expense/', format='json'))

    def test_get_list_json(self):
        resp = self.api_client.get('/api/v1/expense/', format='json', authentication=self.get_credentials())
        self.assertValidJSONResponse(resp)
        # Fetch the objects data from the response
        objects = self.deserialize(resp)['objects']

        # Scope out the data for correctness.
        self.assertEqual(len(objects), 8)

        # Here, we're checking an entire structure for the expected data.
        self.assertEqual(objects[0], {
            'id': self.expense1.pk,
            'description': 'Airplane',
            'comment': 'Fly so high!',
            'amount': '747',
            'date': '2014-06-30T00:00:00',
            'resource_uri': '/api/v1/expense/{0}/'.format(self.expense1.pk)
        })

    def test_get_detail_unauthenticated(self):
        self.assertHttpUnauthorized(self.api_client.get(self.detail_url, format='json'))

    def test_get_detail_json(self):
        resp = self.api_client.get(self.detail_url, format='json', authentication=self.get_credentials())
        self.assertValidJSONResponse(resp)

        # We use ``assertKeys`` here to just verify the keys, not all the data.
        self.assertKeys(self.deserialize(resp), ['amount', 'comment', 'date', 'description', 'id', 'resource_uri'])
        self.assertEqual(self.deserialize(resp)['description'], 'Maths')

    def test_post_list_unauthenticated(self):
        self.assertHttpUnauthorized(self.api_client.post('/api/v1/expense/', format='json', data=self.post_data))

    def test_post_list(self):
        # Check how many are there first.
        self.assertEqual(Expense.objects.count(), 8)
        self.assertHttpCreated(self.api_client.post('/api/v1/expense/', format='json', data=self.post_data,
                                                    authentication=self.get_credentials()))
        # Verify a new one has been added.
        self.assertEqual(Expense.objects.count(), 9)

    def test_put_detail_unauthenticated(self):
        self.assertHttpUnauthorized(self.api_client.put(self.detail_url, format='json', data={}))

    def test_put_detail(self):
        id = self.expense3.pk  # This is the expense we are modifying

        # Grab the current data & modify it slightly.
        original_data = self.deserialize(self.api_client.get(self.detail_url, format='json',
                                                             authentication=self.get_credentials()))
        new_data = original_data.copy()
        new_data['description'] = 'Updated: First Post'
        new_data['date'] = '2012-05-01T20:06:12+12:00'

        self.assertEqual(Expense.objects.count(), 8)
        self.assertHttpAccepted(self.api_client.put(self.detail_url, format='json', data=new_data,
                                                    authentication=self.get_credentials()))
        # Make sure the count hasn't changed when we did the update.
        self.assertEqual(Expense.objects.count(), 8)
        # Check for updated data.
        self.assertEqual(Expense.objects.get(pk=id).description, 'Updated: First Post')
        self.assertEqual(Expense.objects.get(pk=id).comment, 'I can has sums')

        auckland = timezone('Pacific/Auckland')
        auckland_time = auckland.localize(datetime.datetime(2012, 5, 1, 20, 6, 12))
        self.assertEqual(Expense.objects.get(pk=id).date, auckland_time)

    def test_delete_detail_unauthenticated(self):
        self.assertHttpUnauthorized(self.api_client.delete(self.detail_url, format='json'))

    def test_delete_detail(self):
        self.assertEqual(Expense.objects.count(), 8)
        self.assertHttpAccepted(self.api_client.delete(self.detail_url, format='json',
                                                       authentication=self.get_credentials()))
        self.assertEqual(Expense.objects.count(), 7)
