import binascii
import nfc
import csv
import datetime
import signal
import pickle
import requests
import time
import os
import json
import requests
import RPi.GPIO as GPIO

signal.signal(signal.SIGINT, signal.SIG_DFL)
GPIO.setmode(GPIO.BCM)
LED_GREEN = 24
LED_BLUE = 23
GPIO.setup(LED_GREEN, GPIO.OUT)
GPIO.setup(LED_BLUE, GPIO.OUT)
GPIO.output(LED_GREEN,GPIO.LOW)
GPIO.output(LED_BLUE,GPIO.LOW)
member = {}
with open('member.pkl','rb') as f:
    member = pickle.load(f)
webhook_url  = "Webhook URL"
main_content = {'content': ''}
headers      = {'Content-Type': 'application/json'}

def set_led_value(value:int) -> None:
    if value > 100:
        GPIO.output(LED_BLUE,GPIO.HIGH)
    else:
        GPIO.output(LED_BLUE,GPIO.LOW)

class MyCardReader(object):
    def on_connect(self, tag):
        self.idm = binascii.hexlify(tag._nfcid).decode()
        with open('./data/data.csv',newline='',mode='a') as f:
            writer = csv.writer(f)
            writer.writerow([datetime.datetime.now(),self.idm])
        if self.idm not in member:
            GPIO.output(LED_GREEN,GPIO.HIGH)
            member[self.idm] = requests.get("http://localhost:8000/member").text
            with open("member.pkl","wb") as f:
                pickle.dump(member, f)
            time.sleep(0.05)
            GPIO.output(LED_GREEN,GPIO.LOW)
        else:
            set_led_value(255)
            file = './data/'+datetime.datetime.now().strftime('%Y-%m-%d')+'.json'
            data = {}
            if not(os.path.exists(file)):
                with open(file,mode='w') as f:
                    f.write('')
            else:
                with open(file) as f:
                    data=json.load(f)
            if member[self.idm] not in data:
                data[member[self.idm]] = {'in':str(datetime.datetime.now().strftime('%H:%M')),'out':''}
                main_content['content'] = datetime.datetime.now().strftime('%H:%M')+"に"+member[self.idm] + "が入室しました"
                requests.post(webhook_url, json.dumps(main_content), headers=headers)
            else:
                data[member[self.idm]]['out'] = str(datetime.datetime.now().strftime('%H:%M'))
                main_content['content'] = datetime.datetime.now().strftime('%H:%M')+"に"+member[self.idm] + "が退室しました"
                requests.post(webhook_url, json.dumps(main_content), headers=headers)
            with open(file,mode='w',encoding='utf-8') as f:
                json.dump(data,f,indent=4,ensure_ascii=False)
            file = './data/'+datetime.datetime.now().strftime('%Y-%m-%d')+'.csv'
            if not(os.path.exists(file)):
                with open(file,mode='w') as f:
                    f.write('')
            with open(file,newline='',mode='a') as f:
                writer = csv.writer(f)
                writer.writerow([member[self.idm],datetime.datetime.now().strftime('%H:%M')])
        time.sleep(0.05)
        set_led_value(0)
        print(member[self.idm])
        return True
 
    def read_id(self):
        clf = nfc.ContactlessFrontend('usb')
        try:
            clf.connect(rdwr={'on-connect': self.on_connect})
        finally:
            clf.close()
 
if __name__ == '__main__':
    set_led_value(0)
    cr = MyCardReader()
    while True:
        cr.read_id()