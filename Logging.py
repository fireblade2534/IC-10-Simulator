import threading
import datetime
import time
import queue
import inspect
import os
from colorama import Fore
from colorama import Style
#import colorama
class CRITICAL:
    Number=40
    Word="CRITICAL"

class ERROR:
    Number=30
    Word="ERROR"

class WARNING:
    Number=20
    Word="WARNING"

class INFO:
    Number=10
    Word="INFO"

class DEBUG:
    Number=0
    Word="DEBUG"

class Logging:

    def _LoggingThread(self):
            while True:
            
                LogItem=self.LogQueue.get()
                with open(os.path.join(self.LogPath,self.LogFileName),"a") as F:
                    #print(f"HMM {LogItem}")
                    F.write(LogItem + "\n")
                

    def __init__(self,LogToFile=True,LogToConsole=True,LogPath="logs/",AutoGenerateFileName=True,ManualFileName="ProcessLog",LogConsoleLevel=INFO,LogFileLevel=DEBUG,LogMessagePrefix="[%B %d,%Y %H:%M:%S:%f]") -> None:
        self.LogToFile=LogToFile
        self.LogToConsole=LogToConsole
        self.LogPath=LogPath
        self.AutoGenerateFileName=AutoGenerateFileName
        self.LogFileName=ManualFileName + ".txt"
        if self.AutoGenerateFileName:
            self.LogFileName=f"{ManualFileName}:" + datetime.datetime.now().strftime("%m-%d-%Y-%H:%M:%S:%f") + ".txt"
        self.LogConsoleLevel=LogConsoleLevel
        self.LogFileLevel=LogFileLevel
        self.LogMessagePrefix=LogMessagePrefix
        self.LogQueue=queue.Queue()
        if self.LogToFile:
            self.LogThreadReffrence=threading.Thread(target=self._LoggingThread,args=(),daemon=True)
            self.LogThreadReffrence.start()

    def _AddToLogging(self,Message,LogLevel,Color,Caller):
        if Caller == None:
            Caller=inspect.stack()[2]
        FormattedMessage=f"{Color}{datetime.datetime.now().strftime(self.LogMessagePrefix)} {LogLevel.Word} [{Caller.filename.split('/')[-1]}/{Caller.function}:{Caller.lineno}] : {Message}{Style.RESET_ALL}" 
        if self.LogToConsole:
            if LogLevel.Number >= self.LogConsoleLevel.Number:
                print(FormattedMessage)
        if self.LogToFile:
            if LogLevel.Number >= self.LogFileLevel.Number:
                self.LogQueue.put(FormattedMessage)

    def Critical(self,Message:str,Caller=None):
        self._AddToLogging(Message=Message,LogLevel=CRITICAL,Color=Fore.RED + Style.BRIGHT,Caller=Caller)

    def Error(self,Message:str,Caller=None):
        self._AddToLogging(Message=Message,LogLevel=ERROR,Color=Fore.RED,Caller=Caller)

    def Warning(self,Message:str,Caller=None):
        self._AddToLogging(Message=Message,LogLevel=WARNING,Color=Fore.YELLOW,Caller=Caller)
        
    def Info(self,Message:str,Caller=None):
        self._AddToLogging(Message=Message,LogLevel=INFO,Color=Fore.WHITE,Caller=Caller)

    def Debug(self,Message:str,Caller=None):
        self._AddToLogging(Message=Message,LogLevel=DEBUG,Color=Fore.WHITE + Style.DIM,Caller=Caller)