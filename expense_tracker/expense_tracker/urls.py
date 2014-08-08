# coding=utf-8
from __future__ import absolute_import, unicode_literals, print_function, division
from tastypie.api import Api
from django.conf.urls import patterns, include, url
from django.conf import settings
from django.contrib import admin
from expense.resources import ExpenseResource, UserResource, WeeklyTotalResource

v1_api = Api(api_name='v1')
v1_api.register(UserResource())
v1_api.register(ExpenseResource())
v1_api.register(WeeklyTotalResource())

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'expense_tracker.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^$', 'frontend.views.index'),
    url(r'^api/', include(v1_api.urls)),
    url(r'^admin/', include(admin.site.urls)),
)


# Static files should always be served by Apache/Nginx/Other
# But for development purposes they can just be served by Django
if settings.DEBUG:
    urlpatterns += patterns(
        '',
        url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT, }),
    )
