# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from __future__ import unicode_literals

from django.db import models


class Settings(models.Model):
    id = models.AutoField(primary_key=True)
    prefix = models.CharField(max_length=20, default='$')
    currency_name = models.CharField(max_length=50, default='candy')
    currency_plrname = models.CharField(max_length=50, default='candies')
    currency_sign = models.CharField(max_length=50, default='🍬')
    owner = models.CharField(max_length=100, default='None')

    class Meta:
        managed = True
        db_table = 'settings'


class Currency(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=100, null=True)
    userid = models.BigIntegerField()
    amount = models.IntegerField()

    class Meta:
        managed = True
        db_table = 'currency'
