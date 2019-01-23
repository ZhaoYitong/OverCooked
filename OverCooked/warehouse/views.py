from django.shortcuts import render
from django.shortcuts import HttpResponse
from django.shortcuts import HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
import json
import decimal
from . import models
from personnel.models import Employee
import xlrd
from xlrd import xldate_as_tuple
import datetime


@csrf_exempt
def entry(request):
    if request.method == 'GET':
        context = {'storage': {stor_obj.material.name: {'id': stor_obj.material.id, 'num': stor_obj.num}
                               for stor_obj in models.Storage.objects.all()}}
        return render(request, 'entry.html', context)
    elif request.method == 'POST':
        content = json.loads(request.body.decode('utf-8'))
        entry_obj = models.Entry.objects.create(person=Employee.objects.get(account_id=request.user.id))
        for key, val in content.items():
            stora_obj = models.Storage.objects.get(material__name=key)
            stora_obj.num -= int(val)
            stora_obj.save()
            models.EntryDetail.objects.create(entry=entry_obj, material=models.Material.objects.get(name=key), num=int(val))
        return HttpResponse(str({"status": "success"}).replace("'", '"'), content_type='application/json')


@csrf_exempt
def inventory(request):
    if request.method == 'GET':
        context = {'storage': [{'id': stor_obj.id, 'name': stor_obj.material.name, 'num': stor_obj.num, 'date': str(stor_obj.date),
                                'gd': str(models.Material.objects.get(id=stor_obj.material_id).gd), 'material_id': stor_obj.material_id,
                                'md': str(stor_obj.md)} for stor_obj in models.Storage.objects.all()]}
        return render(request, 'inventory.html', context)
    elif request.method == 'POST':
        content = json.loads(request.body.decode('utf-8'))
        for storage_id, count in content.items():
            stora_obj = models.Storage.objects.get(id=storage_id)
            stora_obj.num = count
            stora_obj.save()
        return HttpResponse(str({"status": "success"}).replace("'", '"'), content_type='application/json')


@csrf_exempt
def scrap(request):
    if request.method == 'POST':
        stor_id = request.POST['stor_id']
        scrap_num = request.POST['scrap_num']
        reason = request.POST['reason']
        models.Junk.objects.create(storage_id=int(stor_id), num=int(scrap_num), reason=reason)
        stora_obj = models.Storage.objects.get(id=int(stor_id))
        stora_obj.num -= int(scrap_num)
        stora_obj.save()
        return HttpResponseRedirect('/warehouse/inventory/')


def query(request):
    if request.method == 'GET':
        context = {'storage': [
            {'id': stor_obj.id, 'name': stor_obj.material.name, 'num': stor_obj.num, 'date': str(stor_obj.date),
             'gd': str(models.Material.objects.get(id=stor_obj.material_id).gd), 'material_id': stor_obj.material_id,
             'md': str(stor_obj.md)} for stor_obj in models.Storage.objects.all()],
            'entry': [{'id': entry_obj.id, 'date': str(entry_obj.date), 'person': entry_obj.person.name,
                       'materials': ' '.join([ed.material.name + '*' + str(ed.num)
                                              for ed in models.EntryDetail.objects.filter(entry=entry_obj)])}
                      for entry_obj in models.Entry.objects.all()],
            'delivery': [{'id': delivery_obj.id, 'date': str(delivery_obj.date), 'person': delivery_obj.person.name,
                          'materials': ' '.join([dd.material.name + '*' + str(dd.num)
                                                for dd in models.DeliveryDetail.objects.filter(delivery=delivery_obj)])}
                         for delivery_obj in models.Delivery.objects.all()]
        }
        return render(request, 'query.html', context)


@csrf_exempt
def purchase(request):
    if request.method == 'GET':
        return render(request, 'purchase.html')
    elif request.method == 'POST':
        file_obj = request.FILES.get('file')
        sheet = xlrd.open_workbook(filename=None, file_contents=file_obj.read()).sheets()[0]
        content = {'materials': []}
        for i in range(sheet.nrows):
            if type(sheet.cell_value(i, 0)) == int or type(sheet.cell_value(i, 0)) == float:
                content['materials'].append({'name': sheet.cell_value(i, 1), 'num': int(sheet.cell_value(i, 3)),
                                             'price': str(decimal.Decimal(sheet.cell_value(i, 5))),
                                             'unit': sheet.cell_value(i, 4)})
            elif sheet.cell_value(i, 0).startswith('采购总金额'):
                content['price'] = str(decimal.Decimal(sheet.cell_value(i, 1)))
            elif sheet.cell_value(i, 0).startswith('支付方式'):
                content['method'] = sheet.cell_value(i, 1)
            elif sheet.cell_value(i, 0).startswith('签订日期'):
                content['date'] = datetime.datetime(*xldate_as_tuple(sheet.cell_value(i, 1), 0)).strftime('%Y-%m-%d %H:%M:%S')
            elif sheet.cell_value(i, 0).startswith('收货期限'):
                content['term'] = datetime.datetime(*xldate_as_tuple(sheet.cell_value(i, 1), 0)).strftime('%Y-%m-%d %H:%M:%S')
            elif sheet.cell_value(i, 0).startswith('供方'):
                sn = sheet.cell_value(i, 1)
                supp_obj = models.Supplier.objects.get(name=sn)
                content['supplier'] = {'name': sn, 'person': supp_obj.charger, 'phone': supp_obj.phone,
                                       'address': supp_obj.address}
        person = Employee.objects.get(account_id=request.user.id)
        content['buyer'] = {'name': '煮糊了', 'person': person.name, 'phone': person.phone,
                            'address': '上海市浦东新区南汇新城镇海港大道1550号59号楼'}
        result = str({"status": "success", "content": content}).replace("'", '"')
        return HttpResponse(result, content_type='application/json')


@csrf_exempt
def purchase_confirm(request):
    if request.method == 'POST':
        content = json.loads(request.body.decode('utf-8'))
        purchase_obj = models.Purchase.objects.create(
            supplier=models.Supplier.objects.get(name=content['supplier']['name']),
            person=Employee.objects.get(name=content['buyer']['person']), method=content['method'],
            price=decimal.Decimal(content['price']), date=content['date'], term=content['term'])
        for item in content['materials']:
            models.PurchaseDetail.objects.create(purchase=purchase_obj, left=int(item['num']),
                                                 material=models.Material.objects.get(name=item['name']),
                                                 num=int(item['num']), price=decimal.Decimal(item['price']))
        return HttpResponse(str({"status": "success"}).replace("'", '"'), content_type='application/json')


@csrf_exempt
def purchased(request):
    if request.method == 'GET':
        context = {'purchase': [{'id': pur_obj.id, 'date': pur_obj.date.strftime('%Y-%m-%d %H:%M:%S'),
                                 'term': pur_obj.term.strftime('%Y-%m-%d %H:%M:%S'), 'supplier': pur_obj.supplier.name,
                                 'person': pur_obj.person.name, 'price': str(pur_obj.price), 'paid': pur_obj.paid,
                                 'received': pur_obj.received} for pur_obj in models.Purchase.objects.all()]}
        return render(request, 'purchased.html', context)
    elif request.method == 'POST':
        req = json.loads(request.body.decode('utf-8'))
        if req['command'] == 'query':
            pd_qs = models.PurchaseDetail.objects.filter(purchase_id=req['id'])
            content = [{'material': pd_obj.material.name, 'num': pd_obj.num, 'price': str(pd_obj.price)} for pd_obj in pd_qs]
            return HttpResponse(str({"status": "success", "content": content}).replace("'", '"'),
                                content_type='application/json')
        elif req['command'] == 'delete':
            models.PurchaseDetail.objects.filter(purchase_id=req['id']).delete()
            models.Purchase.objects.get(id=req['id']).delete()
            return HttpResponse(str({"status": "success"}).replace("'", '"'),
                                content_type='application/json')


@csrf_exempt
def supplier(request):
    if request.method == 'GET':
        context = {'supplier': [{'id': sup_obj.id, 'name': sup_obj.name, 'charger': sup_obj.charger,
                                 'phone': sup_obj.phone, 'address': sup_obj.address}
                                for sup_obj in models.Supplier.objects.all()]}
        return render(request, 'supplier.html', context)
    elif request.method == 'POST':
        models.Supplier.objects.create(name=request.POST['name'], charger=request.POST['charger'],
                                       phone=request.POST['phone'], address=request.POST['address'])
        return HttpResponseRedirect('/warehouse/supplier/')


@csrf_exempt
def del_supplier(request):
    if request.method == 'POST':
        req = json.loads(request.body.decode('utf-8'))
        models.Supplier.objects.get(id=req['id']).delete()
        return HttpResponse(str({"status": "success"}).replace("'", '"'), content_type='application/json')


@csrf_exempt
def delivery(request):
    if request.method == 'GET':
        context = {'content': [{'id': pur_obj.id, 'date': pur_obj.date.strftime('%Y-%m-%d %H:%M:%S'),
                                'term': pur_obj.term.strftime('%Y-%m-%d %H:%M:%S'),
                                'material': [{'id': models.Material.objects.get(name=pd_obj.material.name).id,
                                              'name': pd_obj.material.name, 'num': pd_obj.num, 'left': pd_obj.left}
                                             for pd_obj in models.PurchaseDetail.objects.filter(purchase=pur_obj)]}
                               for pur_obj in models.Purchase.objects.filter(received=False)]}
        return render(request, 'delivery.html', context)
    elif request.method == 'POST':
        req = json.loads(request.body.decode('utf-8'))
        pur_obj = models.Purchase.objects.get(id=req['id'])
        delivery_obj = models.Delivery.objects.create(person=Employee.objects.get(account_id=request.user.id))
        for item in req['materials']:
            pd_obj = models.PurchaseDetail.objects.get(purchase=pur_obj, material_id=item['id'])
            pd_obj.left -= int(item['count'])
            pd_obj.save()
            stor_qs = models.Storage.objects.filter(material_id=item['id'])
            if len(stor_qs) == 0:
                models.Storage.objects.create(material_id=item['id'], num=int(item['count']), md=datetime.datetime.now())
            else:
                stor_obj = models.Storage.objects.get(material_id=item['id'])
                stor_obj.num += int(item['count'])
                stor_obj.save()
            models.DeliveryDetail.objects.create(delivery=delivery_obj, material_id=item['id'], num=int(item['count']))
        received = True
        for pd_obj in models.PurchaseDetail.objects.filter(purchase=pur_obj):
            if pd_obj.left > 0:
                received = False
        if received:
            pur_obj.received = True
            pur_obj.save()
        return HttpResponse(str({"status": "success"}).replace("'", '"'), content_type='application/json')

