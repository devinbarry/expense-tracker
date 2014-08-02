# coding=utf-8
from __future__ import absolute_import, unicode_literals, print_function, division
from django.contrib import admin
from expense.models import Expense


class ExpenseAdmin(admin.ModelAdmin):
    date_hierarchy = 'date'
    list_display = ('__unicode__', 'date', )


admin.site.register(Expense, ExpenseAdmin)
