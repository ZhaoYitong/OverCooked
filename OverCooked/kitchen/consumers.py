from channels.generic.websocket import WebsocketConsumer
import json
from datetime import datetime as dt
from foreground.models import Detail
from foreground.models import Food
from .models import Prepare


class DistributeConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

    def disconnect(self, close_code):
        pass

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        command = text_data_json['command']
        if command == 'get':
            t_start = dt.fromtimestamp(int(text_data_json['t_start']))
            t_end = dt.fromtimestamp(int(text_data_json['t_end']))
            state_filter = text_data_json['state_filter']
            details_qs = Detail.objects.filter(state__in=state_filter, order__date__range=[t_start, t_end])
            message = [{'order_id': detail.order_id, 'time': detail.order.date.timestamp(),
                        'food_name': detail.food.name, 'food_mark': detail.mark, 'state': detail.state,
                        'station': detail.station_id, 'detail_id': detail.id} for detail in details_qs]
            self.send(text_data=json.dumps({
                'message': message
            }, ensure_ascii=False))
        elif command == 'delete':
            for key, val in text_data_json['content'].items():
                if val:
                    Detail.objects.get(id=key).delete()

        elif command == 'update':
            for key, val in text_data_json['content'].items():
                detail_obj = Detail.objects.get(id=key)
                detail_obj.station_id = int(val)
                detail_obj.state = '已分配'
                detail_obj.save()


class PrepareConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

    def disconnect(self, close_code):
        pass

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        command = text_data_json['command']
        if command == 'get':
            prepare_qs = Prepare.objects.all()
            message = [{'prepare_id': prepare.id, 'food_name': prepare.food.name,
                        'date': prepare.date.strftime('%H:%M:%S'), 'total': prepare.total,
                        'num': prepare.num, 'used': prepare.used} for prepare in prepare_qs]
            self.send(text_data=json.dumps({
                'message': message
            }, ensure_ascii=False))
        elif command == 'delete':
            for key, val in text_data_json['content'].items():
                if val:
                    Prepare.objects.get(id=key).delete()

        elif command == 'update':
            prepare_qs = Prepare.objects.all()
            p_id = int(text_data_json['content']['prepare_id']) if text_data_json['content']['prepare_id'] else -1
            food_id = Food.objects.get(name=text_data_json['content']['food_name']).id
            total = int(text_data_json['content']['total']) if text_data_json['content']['total'] else 0
            num = int(text_data_json['content']['num']) if text_data_json['content']['num'] else 0
            used = int(text_data_json['content']['used']) if text_data_json['content']['used'] else 0
            if p_id in [prepare.id for prepare in prepare_qs]:
                prepare_obj = prepare_qs.get(id=p_id)
                prepare_obj.food_id = food_id
                prepare_obj.total = total
                prepare_obj.num = num
                prepare_obj.used = used
                prepare_obj.save()
            else:
                Prepare.objects.create(food_id=food_id, total=total, num=num, used=used)
