import requests
import json
import time
import datetime
import os

student_id = os.environ.get('STUDENT_ID')
password = os.environ.get('PASSWORD')

url = 'https://iclass.buaa.edu.cn:8347/app/user/login.action'
para = {
    'password': password,
    'phone': student_id,
    'userLevel': '1',
    'verificationType': '2',
    'verificationUrl': ''
}

res = requests.get(url=url, params=para)
userData = json.loads(res.text)
userId = userData['result']['id']
sessionId = userData['result']['sessionId']

cnt = 0
today = datetime.datetime.today()
for i in range(120):
    if cnt == 7:
        break

    date = today + datetime.timedelta(days=i)
    dateStr = date.strftime('%Y%m%d')
    url = 'https://iclass.buaa.edu.cn:8347/app/course/get_stu_course_sched.action'
    para = {
        'dateStr': dateStr,
        'id': userId
    }
    headers = {
        'sessionId': sessionId,
    }
    res = requests.get(url=url, params=para, headers=headers)
    json_data = json.loads(res.text)
    if json_data['STATUS'] == '0':
        cnt = 0
        for item in json_data['result']:
            courseSchedId = item['id']
            params = {
                'id': userId
            }
            current_timestamp_milliseconds = int(time.time() * 1000)
            sign_url = f'http://iclass.buaa.edu.cn:8081/app/course/stu_scan_sign.action?courseSchedId={courseSchedId}&timestamp={current_timestamp_milliseconds}'
            r = requests.post(url=sign_url, params=params)
            classBeginTime = item['classBeginTime']
            classEndTime = item['classEndTime']
            date = classBeginTime[:10]
            begin = classBeginTime[11:16]
            end = classEndTime[11:16]
            if r.ok:
                data = json.loads(r.text)
                if data['STATUS'] == '1':
                    print(f"疑似这节课没开扫码签到:{date}\t{item['courseName']}\t{begin}-{end}")
                else:
                    print(f"已打卡：{date}\t{item['courseName']}\t{begin}-{end}")
            else:
                print(f"打卡失败：{date}\t{item['courseName']}\t{begin}-{end}")
    else:
        cnt += 1
