from django.shortcuts import render
from django.shortcuts import HttpResponse,HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
import json,datetime
from foreground.models import Order
from financial.models import Total
from warehouse.models import Purchase
from personnel.models import Salary,Employee
from decimal import Decimal
from datetime import datetime as dt
from django.db.models import Sum

@csrf_exempt
def financialStatement(request):
    """收支统计"""
    if request.method == 'GET':
        chart_startD = '2018-01-01' # 初始日期
        chart_endD = '2018-12-31' # 返回当前日期
        start = datetime.datetime.strptime(chart_startD, '%Y-%m-%d')
        end = datetime.datetime.strptime(chart_endD, '%Y-%m-%d')
        step = datetime.timedelta(days=1)
        arr = []
        while start <= end:
            arr.append(start.date())
            start += step
        # list  type

        # all_arr = dict()
        # all_arr['sal'] = []
        # all_arr['pur'] = []
        # all_arr['ord'] = []
        # all_arr['sum'] = []
        # print(arr[1].year)
        # print(arr[1].month)
        # print(arr[1].day)

        # def filterFunc(flowType):
        #     return Total.objects.filter(flowType=flowType,date__year=d.year,date__month=d.month,date__day=d.day)
        def arrAppend(flowT,arrName):
            def filterFunc(flowType):
                return Total.objects.filter(flowType=flowType, date__year=d.year, date__month=d.month,
                                            date__day=d.day)
            for d in arr:
                if len(filterFunc(flowT)) == 0:
                    arrName.append({'date': d.isoformat(), 'fund': str(0)})
                else:
                    if len(filterFunc(flowT)) == 1:
                        arrName.append({'date': d.isoformat(), 'fund': str(Total.objects.get(flowType=flowT, date__year=d.year,
                                                                                    date__month=d.month,
                                                                                    date__day=d.day).flow)})
                    else:
                        arrName.append(
                            {'date': d.isoformat(), 'fund':str(filterFunc(flowT).aggregate(Sum('flow')['flow__sum']))})
            return arrName

        all_arr_sal = []
        all_arr_pur = []
        all_arr_ord = []
        arrAppend('采购支出',all_arr_pur)
        arrAppend('员工工资',all_arr_sal)
        arrAppend('营业收入',all_arr_ord)
        print(type(all_arr_ord))

        # print(all_arr_ord)
        print(all_arr_sal)

        # for d in arr:
        #     if len(filterFunc('采购支出')) == 0:
        #         all_arr['pur'].append({'date':d,'fund':0})
        #     else:
        #         if len(filterFunc('采购支出')) == 1:
        #             all_arr['pur'].append({'date': d, 'fund':Total.objects.get(flowType='采购支出', date__year=d.year,
        #                                                                            date__month=d.month,
        #                                                                            date__day=d.day).flow})
        #         else:
        #             all_arr['pur'].append({'date': d, 'fund':filterFunc('采购支出').aggregate(Sum('flow')['flow__sum'])})
        # print(type(all_arr['pur'][1]['fund']))


        tot_qs = Total.objects.all()
        context = {'content': [{'id': tot_obj.id, 'flowType': tot_obj.flowType, 'fromId': tot_obj.fromId,
                                'flow': str(tot_obj.flow), 'date': tot_obj.date.strftime('%Y-%m-%d'),
                                'marks': tot_obj.marks}
                               for tot_obj in tot_qs]}
        # print(context)
        print(type(context))
        return render(request, 'financialStatement.html', context,
                      {"all_arr_sal":json.dumps(all_arr_sal),
                       "all_arr_pur":json.dumps(all_arr_pur),
                       "all_arr_ord":json.dumps(all_arr_ord)}
                      )
    elif request.method == 'POST':
        req = json.loads(request.body.decode('utf-8'))
        if req['command'] == 'query':
            t_start = dt.fromtimestamp(int(req['t_start']))
            t_end = dt.fromtimestamp(int(req['t_end']))
            tot_qs = Total.objects.filter(date__range=[t_start, t_end])
            data = [{'id': tot_obj.id, 'flowType': tot_obj.flowType, 'fromId': tot_obj.fromId, 'marks': tot_obj.marks,
                    'flow': str(tot_obj.flow), 'date': tot_obj.date.strftime('%Y-%m-%d')} for tot_obj in tot_qs]
            return HttpResponse(str({"content": "table", "data": data}).replace("'", '"'),
                                content_type='application/json')

@csrf_exempt
def financialSalary(request):
    def BooleanDeal(value):
        if value == 0:
            return '否'
        else:
            return '是'
    """员工工资打款"""
    if request.method == 'GET':
        sal = Salary.objects.filter(checkstatus=False)
        context_sal = [{
            'id': obj.id, #工资未发放记录 标识
            'salary': obj.salary,
            'releaseDate':str(obj.releaseDate)[0:10],
            'name':Employee.objects.get(id=obj.employee_id).name,
            'Bankcard':Employee.objects.get(id=obj.employee_id).bankCard,
            'staffId':Employee.objects.get(id=obj.employee_id).staffId,
            'payStatus':BooleanDeal(obj.checkstatus)
        } for obj in sal]
        # print(context_sal)
        return render(request, 'financialSalary.html',{'context_sal':context_sal})
    elif request.method == 'POST':
        # 该数据在所属表格下的 主键 id
        getId = request.POST['sal_staff_id']
        flowType = request.POST['flowType']
        flow = request.POST['flow']
        Total.objects.create(
            flowType=flowType,
            fromId=int(getId),
            flow=Decimal(flow)
        )
        gget = Salary.objects.get(id=getId)
        gget.checkstatus = True
        gget.save()

        return HttpResponse(str({"status": "success"}).replace("'", '"'), content_type='application/json')

@csrf_exempt
def procurementList_Cost(request):
    """采购付款"""
    if request.method == 'GET':
        pur_qs = Purchase.objects.filter(paid=0)
        context = {'content': [{'id': pur_obj.id, 'date': pur_obj.date.strftime('%Y-%m-%d %H:%M:%S'),
                                'price': str(pur_obj.price), 'paid': pur_obj.paid, 'received': pur_obj.received,
                                'person': pur_obj.person.name, 'supplier': pur_obj.supplier.name,
                                'method': pur_obj.method} for pur_obj in pur_qs]}
        return render(request, 'procurement.html', context)
    elif request.method == 'POST':
        req = json.loads(request.body.decode('utf-8'))
        if req['command'] == 'update':
            pur_obj = Purchase.objects.get(id=int(req['id']))
            pur_obj.paid = True
            pur_obj.save()
            Total.objects.create(flowType='采购支出', fromId=int(req['id']), flow=Decimal(pur_obj.price))
            return HttpResponse(str({"status": "success"}).replace("'", '"'), content_type='application/json')

@csrf_exempt
def daily(request):
    """营业账单日结算"""
    if request.method == 'GET':
        today = dt.today()
        order_qs = Order.objects.filter(state='已完成', date__range=[dt(today.year, today.month, today.day, 5), dt(today.year, today.month, today.day, 23)])
        context = {'date': str(today), 'content': [{'order_id': order_obj.id, 'type': order_obj.type,
                                                    'price': order_obj.price, 'checked': order_obj.checked,
                                                    'date': order_obj.date.strftime('%Y-%m-%d %H:%M:%S')}
                                                   for order_obj in order_qs]}
        context['sum'] = sum([order['price'] for order in context['content']])
        return render(request, 'financialDaily.html', context)
    elif request.method == 'POST':
        req = json.loads(request.body.decode('utf-8'))
        if req['command'] == 'query':
            date = dt.fromtimestamp(int(req['date']))
            order_qs = Order.objects.filter(state='已完成', checked=False,
                                            date__range=[dt(date.year, date.month, date.day, 5),
                                                         dt(date.year, date.month, date.day, 23)])
            data = [{'order_id': order_obj.id, 'type': order_obj.type, 'price': str(order_obj.price),
                     'date': order_obj.date.strftime('%Y-%m-%d %H:%M:%S'), 'checked': str(order_obj.checked)}
                    for order_obj in order_qs]
            return HttpResponse(str({"content": "table", "date": str(date), "data": data}).replace("'", '"'),
                                content_type='application/json')
        elif req['command'] == 'insert':
            order_ids = req['ids']
            receipts = 0
            for order_id in order_ids:
                if not Order.objects.get(id=order_id).checked:
                    order_obj = Order.objects.get(id=order_id)
                    receipts += order_obj.price
                    order_obj.checked = True
                    order_obj.save()
            if receipts > 0:
                Total.objects.create(flowType='营业收入', flow=receipts, marks=','.join([str(oid) for oid in order_ids]))
            return HttpResponse(str({"status": "success"}).replace("'", '"'), content_type='application/json')

