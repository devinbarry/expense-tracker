# coding=utf-8
from __future__ import absolute_import, unicode_literals, print_function, division
import hashlib
import time
import datetime
from decimal import Decimal
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


class WeeklyTotal(object):
    """
    This model stores weekly expense total data.
    """

    def __init__(self, year, week_number, expenses):
        """
        Initialise the weekly total.
        :param year: The year for which this is a weekly total
        :param week_number: The number of the week in the year, for which this is the total
        :param expenses: The list of expenses for this week
        :return: None
        """
        self.year = year
        self.week_number = week_number
        # Fetch the date for the start of this week
        self.start_date = self.iso_to_gregorian(year, week_number, 1)
        self.total = 0
        self.average = 0
        self.count = len(expenses)

        for expense in expenses:
            self.total += expense.amount

        # Daily Average is always divided by 7 because there are 7 days in a week
        self.average = self.total / Decimal('7.00')

    # Inversing the ISO calendar data. Taken directly from this answer
    # http://stackoverflow.com/questions/304256/whats-the-best-way-to-find-the-inverse-of-datetime-isocalendar
    def iso_to_gregorian(self, iso_year, iso_week, iso_day):
        """
        Gregorian calendar date for the given ISO year, week and day
        :param iso_year: The ISO year as returned by datetime.isocalendar() function
        :param iso_week: The ISO week as returned by datetime.isocalendar() function
        :param iso_day: The ISO day as returned by datetime.isocalendar() function
        :return: gregorian date
        """
        year_start = self._iso_year_start(iso_year)
        return year_start + datetime.timedelta(days=iso_day - 1, weeks=iso_week - 1)

    @staticmethod
    def _iso_year_start(iso_year):
        """
        The gregorian calendar date of the first day of the given ISO year.
        :param iso_year: The ISO year as returned by datetime.isocalendar() function
        :return: The start date of the ISO year
        """
        fourth_jan = datetime.date(iso_year, 1, 4)
        delta = datetime.timedelta(fourth_jan.isoweekday() - 1)
        return fourth_jan - delta

    def __unicode__(self):
        return 'Week Number: {0}'.format(self.week_number)
