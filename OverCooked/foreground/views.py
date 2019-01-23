from django.shortcuts import render
from django.shortcuts import HttpResponse
from django.shortcuts import HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
import json
import decimal
from . import models
from kitchen.models import Prepare
from kitchen.gadistribute import GA


def check_order(order):
    fields = ['type', 'price', 'foods', 'marks', 'guest', 'phone', 'address']
    for field in fields:
        if field not in order.keys():
            return {"status": "failure", "msg": "incomplete order"}
    if order['type'] == '配送' and not (order['guest'] and order['phone'] and order['address']):
        return {"status": "failure", "msg": "incomplete order"}

    foods_ids = [food.id for food in models.Food.objects.all()]
    for food in order['foods']:
        if int(food) not in foods_ids:
            return {"status": "failure", "msg": "invalid food"}
        if not models.Food.objects.get(id=food).available:
            return {"status": "failure", "msg": "food unavailable"}
    if len(order['foods']) == 0 or len(order['foods']) != len(order['marks']):
        return {"status": "failure", "msg": "invalid mark"}
    return {"status": "success"}


@csrf_exempt
def ordering(request):
    if request.method == 'POST':
        order = json.loads(request.body.decode('utf-8'))
        print(order)
        result = check_order(order)
        if result['status'] == 'success':
            order_obj = models.Order.objects.create(type=order['type'], price=order['price'], guest=order['guest'],
                                                    phone=order['phone'], address=order['address'], state='未完成')
            result['id'] = order_obj.id
            detail_list = []
            for i in range(len(order['foods'])):
                food_state = '未分配'
                try:
                    prepare_obj = Prepare.objects.get(food_id=order['foods'][i])
                    if prepare_obj.num > 0:
                        prepare_obj.num -= 1
                        prepare_obj.used += 1
                        prepare_obj.save()
                        food_state = '已完成'
                except Exception:
                    pass
                detail_list.append(models.Detail(order=order_obj, food=models.Food.objects.get(id=order['foods'][i]),
                                                 mark=order['marks'][i], state=food_state))
            models.Detail.objects.bulk_create(detail_list)
            distr_ga = GA()
            distr_ga.calculate()
            distr_ga.save()
        return HttpResponse(str(result).replace("'", '"'), content_type='application/json')
    elif request.method == 'GET':
        context = dict()
        context['menu'] = {ft_obj.name: [{'id': fo_obj.id, 'name': fo_obj.name, 'price': str(fo_obj.price), 'img': fo_obj.image,
                                          'describe': fo_obj.describe}
                                         for fo_obj in models.Food.objects.filter(type=ft_obj.id, available=1)]
                           for ft_obj in models.FoodType.objects.all()}
        return render(request, 'ordering.html', context)


def ordered(request):
    if request.method == 'GET':
        return render(request, 'ordered.html')


@csrf_exempt
def food(request):
    if request.method == 'GET':
        context = dict()
        context['foods'] = [{'id': food_obj.id, 'name': food_obj.name, 'type': food_obj.type.name,
                             'describe': food_obj.describe, 'price': str(food_obj.price), 'image': food_obj.image,
                             'available': food_obj.available} for food_obj in models.Food.objects.all()]
        context['types'] = [{'id': type_obj.id, 'name': type_obj.name} for type_obj in models.FoodType.objects.all()]
        return render(request, 'food.html', context)
    elif request.method == 'POST':
        models.Food.objects.create(name=request.POST['name'], describe=request.POST['describe'],
                                   type_id=models.FoodType.objects.get(name=request.POST['type']).id,
                                   price=decimal.Decimal(request.POST['price']), image=request.POST['image'])
        return HttpResponseRedirect('/foreground/food/')


@csrf_exempt
def update_food(request):
    if request.method == 'POST':
        foods = json.loads(request.body.decode('utf-8'))
        for key, val in foods.items():
            food_obj = models.Food.objects.get(id=int(key))
            food_obj.name = val['name']
            food_obj.describe = val['describe']
            food_obj.price = decimal.Decimal(val['price'])
            food_obj.image = val['image']
            food_obj.available = True if val['available'] == 'True' else False
            food_obj.save()
        return HttpResponse(str({"status": "success"}).replace("'", '"'), content_type='application/json')


def sale(request):
    if request.method == 'GET':
        return render(request, 'sale.html')
