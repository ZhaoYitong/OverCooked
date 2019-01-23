from django.db import models


class FoodType(models.Model):
    name = models.CharField(max_length=32)


class Food(models.Model):
    name = models.CharField(max_length=32)
    describe = models.CharField(max_length=300, blank=True)
    image = models.CharField(max_length=300)
    type = models.ForeignKey('FoodType', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    available = models.BooleanField(default=True)
    score = models.IntegerField(default=0)
    material = models.ManyToManyField('warehouse.Material', through='warehouse.Bom')


class Order(models.Model):
    type = models.CharField(max_length=16)
    foods = models.ManyToManyField('Food', through='Detail')
    price = models.DecimalField(max_digits=8, decimal_places=2)
    guest = models.CharField(max_length=32, null=True, blank=True)
    phone = models.CharField(max_length=16, null=True, blank=True)
    address = models.CharField(max_length=300, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    state = models.CharField(max_length=8, blank=True)
    checked = models.BooleanField(default=False)


class Detail(models.Model):
    order = models.ForeignKey('Order', on_delete=models.CASCADE)
    food = models.ForeignKey('Food', on_delete=models.CASCADE)
    mark = models.CharField(max_length=300, null=True, blank=True)
    state = models.CharField(max_length=8)
    station = models.ForeignKey('kitchen.Station', on_delete=models.CASCADE, null=True, blank=True)
