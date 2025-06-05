from django.db import models

# Create your models here.
class Pokemon(models.Model):
    zukan_no = models.IntegerField()
    name = models.CharField(max_length=20)
    type = models.CharField(max_length=10)
    color = models.CharField(max_length=20)
    weight = models.FloatField()
    height = models.FloatField()
    evolution = models.IntegerField()
    can_fly = models.BooleanField()
    habitat = models.CharField(max_length=50)
    is_legendary = models.BooleanField()
    feature = models.CharField(max_length=50)
    is_fossil = models.BooleanField()
    has_special_skill = models.BooleanField()
    has_sash = models.BooleanField()
    characteristic = models.CharField(max_length=10)
    initial = models.CharField(max_length=1)