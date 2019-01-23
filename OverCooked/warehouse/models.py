from django.db import models


class Material(models.Model):
    name = models.CharField(max_length=32)
    type = models.CharField(max_length=16)
    unit = models.CharField(max_length=8)
    gd = models.IntegerField()


class Supplier(models.Model):
    name = models.CharField(max_length=32)
    charger = models.CharField(max_length=32)
    phone = models.CharField(max_length=16)
    address = models.CharField(max_length=300)


class Bom(models.Model):
    food = models.ForeignKey('foreground.Food', on_delete=models.CASCADE)
    material = models.ForeignKey('Material', on_delete=models.CASCADE)
    num = models.IntegerField()


class Storage(models.Model):
    material = models.ForeignKey('Material', on_delete=models.CASCADE)
    num = models.IntegerField()
    md = models.DateTimeField()
    date = models.DateTimeField(auto_now_add=True)


class Junk(models.Model):
    storage = models.ForeignKey('Storage', on_delete=models.CASCADE)
    num = models.IntegerField()
    reason = models.CharField(max_length=300)
    date = models.DateTimeField(auto_now_add=True)


class Purchase(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    term = models.DateTimeField(null=True)
    person = models.ForeignKey('personnel.Employee', on_delete=models.CASCADE)
    supplier = models.ForeignKey('Supplier', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    method = models.CharField(max_length=16, null=True)
    paid = models.BooleanField(default=False)
    received = models.BooleanField(default=False)


class PurchaseDetail(models.Model):
    purchase = models.ForeignKey('Purchase', on_delete=models.CASCADE)
    material = models.ForeignKey('Material', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    num = models.IntegerField()
    left = models.IntegerField(default=0)


class Entry(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    person = models.ForeignKey('personnel.Employee', on_delete=models.CASCADE)


class EntryDetail(models.Model):
    entry = models.ForeignKey('Entry', on_delete=models.CASCADE)
    material = models.ForeignKey('Material', on_delete=models.CASCADE)
    num = models.IntegerField()


class Delivery(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    person = models.ForeignKey('personnel.Employee', on_delete=models.CASCADE)


class DeliveryDetail(models.Model):
    delivery = models.ForeignKey('Delivery', on_delete=models.CASCADE)
    material = models.ForeignKey('Material', on_delete=models.CASCADE)
    num = models.IntegerField()
