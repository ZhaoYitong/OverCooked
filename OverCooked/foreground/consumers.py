from channels.generic.websocket import WebsocketConsumer
import json
from datetime import datetime as dt
from datetime import timedelta
from foreground.models import Order
from foreground.models import Detail
from foreground.models import Food


class OrderConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

    def disconnect(self, close_code):
        pass

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        command = text_data_json['command']
        if command == 'get':
            message = []
            for order in Order.objects.filter(state='未完成'):
                message.append({"order_id": order.id, "type": order.type, "price": str(order.price), "guest": order.guest,
                                "phone": order.phone, "address": order.address,
                                "date": order.date.strftime('%Y-%m-%d %H:%M:%S'),
                                "foods": [food.name for food in order.foods.all()]})
            self.send(text_data=json.dumps({
                'message': message
            }, ensure_ascii=False))
        elif command == 'delete':
            Order.objects.get(id=int(text_data_json['content'])).delete()


class StaticsConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

    def disconnect(self, close_code):
        pass

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        command = text_data_json['command']
        if command == 'trend':
            t_start = dt.fromtimestamp(int(text_data_json['t_start']))
            t_end = dt.fromtimestamp(int(text_data_json['t_end']))
            cycle = text_data_json['cycle']
            data = StaticsConsumer._gen_trend_data(t_start, t_end, cycle)
            self.send(text_data=json.dumps({
                'content': 'trend',
                'data': data
            }, ensure_ascii=False))
        elif command == 'table':
            t_start = dt.fromtimestamp(int(text_data_json['t_start']))
            t_end = dt.fromtimestamp(int(text_data_json['t_end']))
            data = [{'id': food.id, 'name': food.name, 'score': food.score,
                     'sales': len(Detail.objects.filter(food_id=food.id, order__date__range=[t_start, t_end]))}
                    for food in Food.objects.all()]
            self.send(text_data=json.dumps({
                'content': 'table',
                'data': data
            }, ensure_ascii=False))

    @classmethod
    def _gen_trend_data(cls, t_start, t_end, cycle):
        tmap = {'年': 365, '月': 30, '周': 7, '日': 1, '小时': 0.0416667}
        data = {'offline': {'label': '线下', 'data': [], 'color': 1},
                'online': {'label': '线上', 'data': [], 'color': 2},
                'total': {'label': '全部', 'data': [], 'color': 3}}
        t_temp = t_start
        while t_temp <= t_end:
            x = str(t_temp)
            if cycle == '年':
                x = t_temp.year
                f_s = dt(year=t_temp.year, month=1, day=1, hour=0, minute=0, second=0)
            elif cycle == '月':
                x = t_temp.month
                f_s = dt(year=t_temp.year, month=t_temp.month, day=1, hour=0, minute=0, second=0)
            elif cycle == '周':
                x = t_temp.day
                f_s = dt(year=t_temp.year, month=t_temp.month, day=t_temp.day, hour=0, minute=0, second=0)
            elif cycle == '日':
                x = t_temp.day
                f_s = dt(year=t_temp.year, month=t_temp.month, day=t_temp.day, hour=0, minute=0, second=0)
            elif cycle == '小时':
                x = t_temp.hour
                f_s = dt(year=t_temp.year, month=t_temp.month, day=t_temp.day, hour=t_temp.hour, minute=0, second=0)
            f_e = f_s + timedelta(days=tmap[cycle])
            y_offline = len(Detail.objects.filter(order__type__in=['堂吃', '外带'], order__date__range=[f_s, f_e]))
            y_online = len(Detail.objects.filter(order__type__in=['配送'], order__date__range=[f_s, f_e]))
            data['offline']['data'].append([x, y_offline])
            data['online']['data'].append([x, y_online])
            data['total']['data'].append([x, y_offline + y_online])
            t_temp = t_temp + timedelta(days=tmap[cycle])
        return data
