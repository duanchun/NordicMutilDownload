from threading import Thread
import NordicMultipleDownload
import wx
from main import DOWNLOAD_EVT_SERIAL_ERROR_HAPPEND,DOWNLOAD_EVT_OVER,ResultEvent


class DownloadThreadTask(Thread):
    """download thread  class"""
    def __init__(self,wxObject,serial,hexFilePath):
        Thread.__init__(self)
        self.wxObject = wxObject
        self.serial = serial
        self.hexFilePath = hexFilePath
        self.start()

    def run(self):
        """Run Worker Thread."""
        try:
            NordicMultipleDownload.run(self.serial,self.hexFilePath)
        except:
            param = [DOWNLOAD_EVT_SERIAL_ERROR_HAPPEND, self.serial]
            wx.PostEvent(self.wxObject, ResultEvent(param))
            print("NordicMultipleDownload Error happend")
            raise
        print("DownloadThreadTask Successed")
        param = [DOWNLOAD_EVT_OVER,self.serial]
        wx.PostEvent(self.wxObject, ResultEvent(param))