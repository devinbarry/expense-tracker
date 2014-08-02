# coding=utf-8
from __future__ import absolute_import, unicode_literals, print_function, division
import hashlib
import time
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.conf import settings
from tastypie.models import ApiKey


def make_api_key():
    """
    Similar to Tastypie's generate_key method for its ApiKey Model, this
    function uses the current timestamp and secret key salt, hashed with
    SHA1 to produce the API key. The default method uses UUID and runs it
    through the HMAC algorithm (using SHA1) to produce its key.
    :return: A unique API key
    """
    timestamp = str(time.time())
    return hashlib.sha1(timestamp + ":" + settings.SECRET_KEY).hexdigest()


def create_api_key(sender, instance, created, **kwargs):
    """
    Create an API Key in the database to use when authenticating
    the user passed in as instance. Note a new key is only created
    when a new user is created.
    """
    if created:
        ApiKey.objects.get_or_create(user=instance, key=make_api_key())


# Connect the post save signal to the above function.
post_save.connect(create_api_key, sender=User)


class Expense(models.Model):
    """
    This model stores details about an expense.
    """
    user = models.ForeignKey(User)
    date = models.DateTimeField(db_index=True)
    description = models.CharField(max_length=255)
    amount = models.DecimalField(default=0, decimal_places=2, max_digits=8, blank=True,
                                 help_text="The dollar amount of this expense")
    comment = models.TextField()

    def __unicode__(self):
        return self.description
