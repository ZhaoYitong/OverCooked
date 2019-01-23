from django.shortcuts import render,HttpResponse,HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from . import models
from  decimal import Decimal
from django.db.models import Sum
import json,os,re,time,datetime

@csrf_exempt
def employeeInfo(request):
    if request.method == 'GET':
        return render(request,'employeeInfo.html')
    elif request.method == 'POST':
        photo = request.FILES.get('personalPhoto',None) # 获取上传文件，如果没有，则默认为none
        if not photo:
            return HttpResponse('没有上传图片')
        destination = open(os.path.join('static/img/staff_Photo/',photo.name),'wb+') # 打开特定的二进制文件进行操作
        for chunk in photo.chunks():
            destination.write(chunk)
        destination.close()
        models.Employee.objects.create(name=request.POST['name'], gender=request.POST.get('radios'),
                                       age=request.POST['age'], ethnic = request.POST['ethnic'],
                                       phone=request.POST['phoneNumber'],
                                       email=request.POST['email'], idCardNum=request.POST['IDNumber'],
                                       bankCard=request.POST['AccountantNumber'],
                                       department=request.POST.get('selectDepartment'),
                                       staffId=request.POST['staffId'],
                                       position=request.POST.get('selectPosition'),
                                       iswork='是',
                                       entryTime=request.POST['entryTime'],
                                       personPhoto='/static/img/staff_Photo/'+ request.FILES.get('personalPhoto',None).name)
        return HttpResponse(str({"status": "提交成功"}).replace("'", '"'), content_type='application/json')   # 提交成功后以 alert形式显示 ?
@csrf_exempt
def employeeBasicInfo(request):
     if request.method == 'GET':
        staffList = models.Employee.objects.all()  # 员工信息表
        return render(request,'employeeBasicInfo.html',{'staffList':staffList})
     elif request.method == 'POST':
            staffs = json.loads(request.body.decode('utf-8'))
            # print(staffs)
            for key,val in staffs.items():
                staff_obj = models.Employee.objects.get(id=int(key)) # 更改数据
                staff_obj.name = val['NAME']
                staff_obj.phone = val['PHONE']
                staff_obj.gender = val['GENDER']
                staff_obj.age = val['AGE']
                staff_obj.email = val['EMAIL']
                staff_obj.idCardNum = val['IDCARD']
                staff_obj.entryTime = val['ENTRYTIME']
                staff_obj.bankCard = val['BANKCARD']
                staff_obj.ethnic = val['ETHNIC']
                staff_obj.position = val['POSITION']
                staff_obj.department = val['DEPARTMENT']
                staff_obj.iswork = val['ISWORK']
                staff_obj.staffId = val['STAFFID']
                staff_obj.save()
            return HttpResponse(str({"status": "提交成功"}).replace("'", '"'), content_type='application/json')
@csrf_exempt
def employeeDistribute(request):
    if request.method == 'GET':
# 是否工作的查找
        def workEvent_Depart(work,depart):
            id_arr = []
            for item in models.Employee.objects.filter(department=depart):
                id_arr.append(item)
            all_distribute_W = models.Distribute.objects.filter(eventType=str(work),employee_id__in=id_arr)
            context_w = [{
                 'id_PK':str(obj.id),
                 'name': models.Employee.objects.get(id=obj.employee_id).name,
                 'staffId': models.Employee.objects.get(id=obj.employee_id).staffId,
                 'department': models.Employee.objects.get(id=obj.employee_id).department,
                 'startWorkTime': str(obj.start_work_hour)[0:10],
                 'endWorkTime': str(obj.end_work_hour)[0:10],
            }for obj in all_distribute_W]
            return context_w
# 筛选不同部门下的可选的在职员工  如  前台  是
        def getSt_Fr_De(department,workType):
            distribute_De = models.Employee.objects.filter(department=str(department),iswork=str(workType)) #workType 是 否
            text_De = [{
                        'name':De_obj.name,
                        'staffId':De_obj.staffId,
                        'department':De_obj.department,
                        'employee_id':De_obj.id }for De_obj in distribute_De]
            return text_De
        # print(workEvent_Depart('work','厨房'))
        return render(request, 'employeeDistribute.html',{'fore':workEvent_Depart('work','前台'),
                                                          'kit':workEvent_Depart('work','厨房'),
                                                          'ware':workEvent_Depart('work','人事'),
                                                          'per':workEvent_Depart('work','人事'),
                                                          'fina':workEvent_Depart('work','财务'),
                                                          # 排版表 选择日期 生成模态框
                                                          #  下拉选择不同部门下的员工  待实现 ......
                                                          'fore_avail':getSt_Fr_De('前台','是'),
                                                          'kit_avail': getSt_Fr_De('厨房', '是'),
                                                          'ware_avail': getSt_Fr_De('库存采购', '是'),
                                                          'per_avail': getSt_Fr_De('人事', '是'),
                                                          'fina_avail': getSt_Fr_De('财务', '是')
                                                          })


    elif request.method == 'POST':
        def unixToISO(TIME):
            timestamp = int(TIME[0:10])
            timeArray = time.localtime(timestamp)
            timeISO = time.strftime("%Y-%m-%d %H:%M:%S",timeArray)
            return timeISO

        title = request.POST['Title']
        start_Date = request.POST['Start']
        end_Date = request.POST['End']
        getSt_Id= re.sub("\D", "", title)
        # print(getSt_Id)
        # 工号有误则重定向到本页面
        # if models.Employee.objects.filter(staffId=getSt_Id).name !=
        if not models.Employee.objects.filter(staffId=getSt_Id):
            return HttpResponseRedirect('/personnel/employeeDistribute/')
        else:
            models.Distribute.objects.create(employee_id=models.Employee.objects.get(staffId=getSt_Id).id,
                                             eventType='work',
                                             start_work_hour=str(unixToISO(start_Date)),
                                             end_work_hour=str(unixToISO(end_Date)))
        return HttpResponse(str({"status": "提交成功"}).replace("'", '"'), content_type='application/json')

@csrf_exempt
def deleteEvent(request):
    if request.method == 'POST':
        models.Distribute.objects.filter(id=request.POST['id']).delete()
        return HttpResponse(str({"status_delete": "删除成功"}).replace("'", '"'), content_type='application/json')

@csrf_exempt
def employeePerform(request):
    if request.method == 'GET':


        LogList = models.performance.objects.all()  # 绩效记录表
        context_LogList = [{'name': models.Employee.objects.get(id=Perform_obj.employee_id).name,
                            'staffId': models.Employee.objects.get(id=Perform_obj.employee_id).staffId,
                            'department': models.Employee.objects.get(id=Perform_obj.employee_id).department,
                            'bonus': Perform_obj.bonus,
                            'penalty': Perform_obj.penalty,
                            'logTime': str(Perform_obj.logTime)[0:10],
                            'employee': Perform_obj.employee_id,
                            'reason': Perform_obj.reason
                            } for Perform_obj in LogList]
        return render(request, 'employeePerformance.html', {'context_LogList': context_LogList})
    elif request.method == 'POST':
        if models.Employee.objects.get(staffId=request.POST["Per_staffId"]).name == request.POST["Per_name"]:
            models.performance.objects.create(
                bonus=request.POST["Per_bonus"],
                penalty=request.POST["Per_penalty"],
                reason=request.POST["Per_reason"],
                logTime=request.POST["Per_logtime"],
                employee_id=models.Employee.objects.get(staffId=request.POST["Per_staffId"]).id)
            return HttpResponseRedirect('/personnel/employeePerform/')


@csrf_exempt
def employeeSalary(request):
    def sumAll(a, b, c):  # 求出该月份内的总工资
        return (a + b - c)
    def isNoneOrNot(value):
        if value == None:
            return Decimal(0.00)
        else:
            return value
    def BooleanDeal(value):
        if value == 0:
            return '否'
        else:
            return '是'
    def SumBonusOrPenalty(object):
        return models.performance.objects.filter(employee_id=object.employee_id,logTime__year=object.releaseDate.year,logTime__month=object.releaseDate.month)
    if request.method == 'GET':
        Salary = models.Salary.objects.all()
        context_Salary = [{'name':models.Employee.objects.get(id=Sal_obj.employee_id).name,
                           'staffId':models.Employee.objects.get(id=Sal_obj.employee_id).staffId,
                           'department':models.Employee.objects.get(id=Sal_obj.employee_id).department,
                           'position':models.Employee.objects.get(id=Sal_obj.employee_id).position,
                           'bonus': str(isNoneOrNot(SumBonusOrPenalty(Sal_obj).aggregate(Sum('bonus'))['bonus__sum'])),
                           'penalty':str(isNoneOrNot(SumBonusOrPenalty(Sal_obj).aggregate(Sum('penalty'))['penalty__sum'])),
                           'baseWage':str(Sal_obj.baseWage),
                           'salary': str(sumAll(Sal_obj.baseWage,
                                                isNoneOrNot(SumBonusOrPenalty(Sal_obj).aggregate(Sum('bonus'))['bonus__sum']),
                                                isNoneOrNot(SumBonusOrPenalty(Sal_obj).aggregate(Sum('penalty'))['penalty__sum']))),
                           'unit':'￥',
                           'releaseDate':str(Sal_obj.releaseDate)[0:10],
                           'checkStatus':BooleanDeal(Sal_obj.checkstatus)
                            } for Sal_obj in Salary]
        # print(context_Salary)
        return render(request,'employeeSalary.html',{'context_Salary': context_Salary})
    elif request.method == 'POST':
        if models.Employee.objects.get(staffId=request.POST['Sal_staffId']).name == request.POST['Sal_name']:
            bonus_add_sum = models.performance.objects.filter(employee_id=models.Employee.objects.get(staffId=request.POST['Sal_staffId']).id).aggregate(Sum('bonus'))['bonus__sum']
            penalty_minus_sum = models.performance.objects.filter(employee_id=models.Employee.objects.get(staffId=request.POST['Sal_staffId']).id).aggregate(Sum('penalty'))['penalty__sum']
            base = request.POST['Sal_baseWage']
            Emplo_id = models.Employee.objects.get(staffId=request.POST['Sal_staffId']).id
            release_d = request.POST['Sal_logtime']
            if not models.Salary.objects.filter(employee_id=Emplo_id,releaseDate__year=release_d[0:4],releaseDate__month=release_d[6:7]):
                models.Salary.objects.create(baseWage=base,
                                             employee_id=Emplo_id,
                                             releaseDate=release_d,
                                             salary=(float(base)+float(bonus_add_sum)-float(penalty_minus_sum)))
                print('aaaaa')
        return HttpResponseRedirect('/personnel/employeeSalary/')





