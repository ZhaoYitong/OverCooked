from django.db import models

class Total(models.Model):
    date = models.DateTimeField(auto_now=True)
    flowType = models.CharField(max_length=32) # 库存采购  员工工资   营业收入
    flow = models.DecimalField(max_digits=32, decimal_places=2)
    fromId=models.IntegerField() #现金流来源
    marks = models.CharField(max_length=4096,null=True,blank=True)









