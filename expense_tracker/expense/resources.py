# coding=utf-8
from __future__ import absolute_import, unicode_literals, print_function, division
from decimal import Decimal
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.conf.urls import url
from tastypie import http
from tastypie.resources import ModelResource
from tastypie.authentication import ApiKeyAuthentication
from tastypie.authorization import Authorization
from tastypie.utils import trailing_slash
from expense.models import Expense


class BaseModelResource(ModelResource):
    """
    Provides default format for other models.
    """

    def determine_format(self, request):
        return 'application/json'


# Tasypie authenticate code inspired by:
# http://stackoverflow.com/questions/11770501/how-can-i-login-to-django-using-tastypie
class UserResource(BaseModelResource):

    class Meta:
        queryset = User.objects.all()
        fields = ['first_name', 'last_name', 'username']
        list_allowed_methods = []  # Disallow all batch requests
        detail_allowed_methods = ['put', 'post']  # Get get
        resource_name = 'user'
        authorization = Authorization()

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/authenticate%s$" % (self._meta.resource_name, trailing_slash()),
                self.wrap_view('authenticate'), name="api_login"),
            url(r"^(?P<resource_name>%s)/register%s$" % (self._meta.resource_name, trailing_slash()),
                self.wrap_view('register'), name="api_register"),
        ]

    def authenticate(self, request, **kwargs):
        """
        Fetch the user API after the user has supplied username and password.
        :param request: Django request object
        :param kwargs:
        :return:
        """
        self.method_check(request, allowed=['post'])
        data = self.deserialize(request, request.body, format=request.META.get('CONTENT_TYPE', 'application/json'))
        username = data.get('username', '')
        password = data.get('password', '')
        # Test if the user credentials will authenticate
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                # Hooray, the user authenticates and is valid. Respond with Api Key and some other useful fields
                return self.create_response(request, {
                    'success': True,
                    'username': user.username,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'api_key': user.api_key.key,
                })
            else:
                return self.create_response(request, {'success': False, 'reason': 'Your account has been disabled', },
                                            http.HttpForbidden)
        else:
            return self.create_response(request, {'success': False, 'reason': 'Username or password is incorrect', },
                                        http.HttpUnauthorized)

    def register(self, request, **kwargs):
        """
        Create a user object and return an API Key.
        :param request: Django request object
        :param kwargs:
        :return:
        """
        self.method_check(request, allowed=['post'])
        data = self.deserialize(request, request.body, format=request.META.get('CONTENT_TYPE', 'application/json'))
        username = data.get('username')
        password = data.get('password')

        valid = True
        message = ""

        if not username:
            valid = False
            message = "A username is required"
        elif User.objects.filter(username=username).exists():
            valid = False
            message = "That username has already been taken"
        elif not password:
            valid = False
            message = "A password is required"

        if valid:
            # Passed the basic validation, not try create the user, which might raise further validation issues.
            try:
                user = User.objects.create_user(username, data.get('email'), password)
                user.first_name = data.get('first_name', '')
                user.last_name = data.get('last_name', '')
                user.save()
            except Exception as e:
                # Model entity validation
                return self.create_response(request, {'success': False, 'reason': e, }, http.HttpBadRequest)
        else:
            return self.create_response(request, {'success': False, 'reason': message, }, http.HttpBadRequest)

        return self.authenticate(request, **kwargs)


class ExpenseResource(BaseModelResource):
    """ Expose the Expense objects over REST, and provide a level of authorisation """

    def obj_create(self, bundle, **kwargs):
        """
        Any "create" methods must use the session user always.
        """
        return super(ExpenseResource, self).obj_create(bundle, user=bundle.request.user)

    def authorized_read_list(self, object_list, bundle):
        """
        All "list" methods must filter by this user only.
        """
        return object_list.filter(user=bundle.request.user)

    def alter_list_data_to_serialize(self, request, data):
        """
        Add total amount and average to meta response.
        """
        total_amount = Decimal('0')
        average = Decimal('0')

        # Sum the amount for all objects to get the total_amount
        for obj in data['objects']:
            total_amount += obj.obj.amount

        # Divide the total by the number of items to get average
        count = len(data['objects'])
        if count:
            average = total_amount / count

        data['meta']['total_amount'] = total_amount
        data['meta']['average'] = average
        return data

    class Meta:
        list_allowed_methods = ['get', 'post']
        detail_allowed_methods = ['get', 'put', 'delete']
        queryset = Expense.objects.all()
        resource_name = 'expense'
        authorization = Authorization()
        authentication = ApiKeyAuthentication()
        filtering = {'date': ['range']}
