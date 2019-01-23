from django.shortcuts import render
from django.shortcuts import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
from foreground.models import Order
from foreground.models import Food
from foreground.models import Detail
from .gadistribute import GA


def distribution(request):
    if request.method == 'GET':
        return render(request, 'distribution.html')


def prepare(request):
    if request.method == 'GET':
        food_qs = Food.objects.filter(available=True)
        context = dict()
        context['foods'] = [{'id': food.id, 'name': food.name} for food in food_qs]
        return render(request, 'prepare.html', context)


@csrf_exempt
def finish(request):
    if request.method == 'POST':
        detail = json.loads(request.body.decode('utf-8'))
        detail_obj = Detail.objects.get(id=int(detail['id']))
        detail_obj.state = '已完成'
        detail_obj.save()
        for order_obj in Order.objects.filter(state='未完成'):
            detail_qs = Detail.objects.filter(order_id=order_obj.id)
            finished = True
            for detail_obj in detail_qs:
                if detail_obj.state != '已完成':
                    finished = False
            if finished:
                order_obj.state = '已完成'
                order_obj.save()
        distr_ga = GA()
        distr_ga.calculate()
        distr_ga.save()
        return HttpResponse('{"status": "success"}', content_type='application/json')

