from django.db import models
from django.contrib import auth
from django.core.validators import MaxLengthValidator
def get_temp_user():
    am = auth.get_user_model()
    return am.objects.get(id=3).id
# 员工基本信息表
class Employee(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=32,verbose_name='姓名',default='Zhao')
    phone = models.CharField(max_length=16,verbose_name='联系电话',default='18800209387')
    account = models.ForeignKey('auth.user', on_delete=models.CASCADE, null=True, default=get_temp_user,verbose_name='登陆账号')
    gender = models.CharField(max_length=8,verbose_name='性别',default='男') #default='男'
    age = models.IntegerField(default=18,verbose_name='年龄')
    email = models.EmailField(blank=True, null=True,verbose_name='邮箱')
    idCardNum = models.CharField(max_length=18,verbose_name='身份证号',default='370401199702135689') #default='370401199702135689'
    entryTime = models.CharField(max_length=20,verbose_name='入职时间',default='2017/02/15') #default='2017/02/15'
    personPhoto = models.ImageField(upload_to='staff_Photo',null=True,blank=True)
    bankCard = models.CharField(max_length=30,verbose_name='银行卡号',default='1234567890123456789') #default='1234567890123456789'
    ethnic = models.CharField(max_length=50,verbose_name='民族', default='汉族')
    position = models.CharField(max_length=80,null=True,blank=True,verbose_name='职位',default='员工')
    department = models.CharField(max_length=64,default='厨房',verbose_name='部门')
    iswork = models.CharField(max_length=8,default='是')
    staffId = models.CharField(max_length=9,null=True,blank=True,verbose_name='员工工号') # 不可重复使用

    # 工号 (入职时间 + 部门 + 序号(三位)) ## 由招聘时间 和 工作部门决定工号
     #如工号 160703002 表示 2016年7月入职 工作位置在库存采购部门(03) 在201607 第二个入职该部门的员工
         # 部门分配方式如下
            # 前台 01
            # 厨房 02
            # 库存采购 03
            # 财务 04
            # 人事 05
# 工资表
class Salary(models.Model):
    employee = models.ForeignKey('Employee',on_delete=models.CASCADE,default='1')
    salary = models.DecimalField(max_digits=16, decimal_places=2, null=True, blank=True,verbose_name='工资',default='3200')
    releaseDate = models.DateTimeField(default='2018-06-01 23:40:22.814392')
    baseWage = models.DecimalField(max_digits=16, decimal_places=2, null=True, blank=True,verbose_name='基本工资',default='2000')
    checkstatus = models.BooleanField(default=False)
    # class Meta:
    #     db_table ="personnel_salary"

class performance(models.Model):
    employee = models.ForeignKey('Employee',on_delete=models.CASCADE,default='30')
    logTime = models.DateTimeField(default='2018-06-01 23:40:22.814392')
    bonus = models.DecimalField(max_digits=16, decimal_places=2, null=True, blank=True)
    penalty = models.DecimalField(max_digits=16, decimal_places=2, null=True, blank=True)
    reason  = models.TextField(validators=[MaxLengthValidator(1000)],default='原因如下：')

## 排班计划
# 姓名
# 工号
# 工作部门
# 工作时间范围
    ## 工作时间：
      # 周一 ~ 周日
      # 9：00 am ~ 14:00pm    17:00pm ~ 22:00pm
# 排班计划表
class Distribute(models.Model):
    # even_id -- PK
    employee = models.ForeignKey('Employee', on_delete=models.CASCADE)
    # work_date = models.CharField(max_length=15,default='2017-02-15')
    start_work_hour = models.DateTimeField(null=True,blank=True)
    # workingTime= models.CharField(max_length=10,null=True,blank=True,verbose_name='工作总时间',default='2hours')# 小时制
    end_work_hour = models.DateTimeField(null=True,blank=True)
    # isHoliday = models.BooleanField(default=False)
    eventType = models.CharField(max_length=32,null=True,blank=True) #工作  休息












# 请假表
# class Leave(models.Model):
#     employee = models.ForeignKey('Employee',on_delete=models.CASCADE,default='1')
#     leaveStart = models.DateTimeField(default='2018-06-01 23:40:22.814392')
#     leavingTimeTotal = models.CharField(max_length=10,null=True,blank=True,default='3hours') # 小时制
#     leaveEnd = models.DateTimeField(default='2018-06-01 23:40:22.814392')

###############################
# DATE  &  DATETIME  in Mysql #
###############################
# The DATE type is used for values with a date part but no time part.
#  MySQL retrieves and displays DATE values in 'YYYY-MM-DD' format.
# The supported range is '1000-01-01' to '9999-12-31'.

# The DATETIME type is used for values that contain both date and time parts.
# MySQL retrieves and displays DATETIME values in 'YYYY-MM-DD HH:MM:SS' format.
# The supported range is '1000-01-01 00:00:00' to '9999-12-31 23:59:59'.

