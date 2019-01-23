from django.db import models


class Station(models.Model):
    charger = models.ForeignKey('personnel.Employee', on_delete=models.CASCADE)
    foods = models.ManyToManyField('foreground.Food', through='Capacity')


class Capacity(models.Model):
    station = models.ForeignKey('Station', on_delete=models.CASCADE)
    food = models.ForeignKey('foreground.Food', on_delete=models.CASCADE)
    time = models.FloatField()


class Prepare(models.Model):
    food = models.ForeignKey('foreground.Food', on_delete=models.CASCADE)
    num = models.IntegerField(default=0)
    used = models.IntegerField(default=0)
    total = models.IntegerField(default=0)
    date = models.TimeField(auto_now=True)
