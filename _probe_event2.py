from device_service import DeviceRepository
from datetime import datetime, timedelta
r = DeviceRepository()
records,_ = r.list_records(decorate=False)
rec = records[0]
end = datetime.now()
start = end - timedelta(days=5)
params_list = [
    {'product_id': rec['product_id'], 'device_name': rec['onenet_device_name'], 'start': start.strftime('%Y-%m-%dT%H:%M:%S'), 'end': end.strftime('%Y-%m-%dT%H:%M:%S')},
    {'product_id': rec['product_id'], 'device_name': rec['onenet_device_name'], 'start': start.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3], 'end': end.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]},
    {'product_id': rec['product_id'], 'device_name': rec['onenet_device_name'], 'start_time': start.strftime('%Y-%m-%dT%H:%M:%S'), 'end_time': end.strftime('%Y-%m-%dT%H:%M:%S')},
    {'product_id': rec['product_id'], 'device_name': rec['onenet_device_name'], 'begin_time': start.strftime('%Y-%m-%dT%H:%M:%S'), 'end_time': end.strftime('%Y-%m-%dT%H:%M:%S')},
    {'product_id': rec['product_id'], 'device_name': rec['onenet_device_name'], 'page': 1, 'per_page': 20, 'start': start.strftime('%Y-%m-%dT%H:%M:%S'), 'end': end.strftime('%Y-%m-%dT%H:%M:%S')},
]
for params in params_list:
    try:
        data = r._query_onenet(rec, '/device/event-log', params)
        print('OK', params)
        print(data)
    except Exception as e:
        print('ERR', params, e)
