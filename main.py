import wx
import wx.lib.agw.pygauge as PG
from pynrfjprog import LowLevel
from threading import Thread
import NordicMultipleDownload
import time

#EVT_RESULT_ID = wx.NewId()
EVT_RESULT_ID = 100
DOWNLOAD_EVT_OVER  = 51
DOWNLOAD_EVT_SERIAL_ERROR_HAPPEND = 52 + 1

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
            #for i in range(5):
                #time.sleep(1)
                #print("Thread Start")
        except:
            param = [DOWNLOAD_EVT_SERIAL_ERROR_HAPPEND, self.serial]
            wx.PostEvent(self.wxObject, ResultEvent(param))
            print("NordicMultipleDownload Error happend")
            raise
        print("DownloadThreadTask Successed")
        param = [DOWNLOAD_EVT_OVER,self.serial]
        wx.PostEvent(self.wxObject, ResultEvent(param))

def EVT_RESULT(win, func):
    """Define Result Event."""
    win.Connect(-1, -1, EVT_RESULT_ID, func)

class ResultEvent(wx.PyEvent):
    """Simple event to carry arbitrary result data."""

    def __init__(self, data):
        """Init Result Event."""
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_RESULT_ID)
        self.data = data

class DownloadFrame:
    def __init__(self,panel,sizer):
        self.panel = panel
        self.sizer = sizer
        self.MyUiLayout()

    def MyUiLayout(self):
        downloadSizer = wx.BoxSizer(wx.HORIZONTAL)
        # Process Bar
        self.processBar = PG.PyGauge(self.panel, size=(350, 30))
        self.processBar.SetBackgroundColour(wx.WHITE)
        self.processBar.SetBorderColor(wx.BLACK)
        self.processBar.SetBarColour(wx.GREEN)
        self.processBar.SetValue(0)
        downloadSizer.Add(self.processBar, 0, flag=wx.RIGHT | wx.LEFT, border=8)

        serial = wx.StaticText(self.panel, wx.ID_ANY, "Serial：")
        downloadSizer.Add(serial, 0, flag=wx.RIGHT | wx.LEFT, border=8)

        # Serial select
        self.serialSelect = wx.ComboBox(self.panel, wx.ID_ANY, size=(150, 30))
        downloadSizer.Add(self.serialSelect, 0, flag=wx.RIGHT | wx.LEFT, border=8)

        self.sizer.Add(downloadSizer, 0, flag=wx.TOP, border=30)
    def processStart(self):
        self.processBar.Update(100,3500)

    def processBarReusltSuccessed(self):
        self.processBar.Update(100 - self.processBar.GetValue(),50)
    def processBarReusltFailed(self):
        self.processBar.SetBarColour(wx.RED)
        self.processBar.Update(100 - self.processBar.GetValue(),50)

class MyFrame(wx.Frame):
    def __init__(self):
        super().__init__(parent=None,title='NordicMultilDownloadTool',size=(800,600))
        self.Center()
        self.panel = wx.Panel(self)
        self.mySizer = wx.BoxSizer(wx.VERTICAL)
        self.targetFileSelect()
        self.downloadBtnLayout()
        self.downloadOne = DownloadFrame(self.panel,self.mySizer)
        self.downloadTwo = DownloadFrame(self.panel, self.mySizer)
        self.downloadThree = DownloadFrame(self.panel, self.mySizer)
        self.downloadFour = DownloadFrame(self.panel, self.mySizer)
        self.downloadAll = [self.downloadOne,self.downloadTwo,self.downloadThree,self.downloadFour]
        self.panel.SetSizer(self.mySizer)
        self.UpdateDownloadFrame()
        EVT_RESULT(self, self.updateUI)
        self.Show()

    def UpdateDownloadFrame(self):
        for downloadTemp in self.downloadAll:
            downloadTemp.serialSelect.Clear()
            downloadTemp.processBar.SetValue(0)
            downloadTemp.processBar.Update(0.00001,50)
        with LowLevel.API(
                LowLevel.DeviceFamily.UNKNOWN) as api:  # Using with construction so there is no need to open or close the API class.
            snr = api.enum_emu_snr()
            print("Snr:", snr)
            if snr is not None:
                index = 0
                for snrB in snr:
                    self.downloadAll[index].serialSelect.SetValue(str(snrB))
                    index += 1
                print("Serial Number==", len(snr))
                return len(snr)
            else:
                self.btnDownload.Disable()
                return None

    def onBtnDownload(self,event):
        hexFilePath = self.text_ctrl.GetValue()
        self.downloadTaskRecord = 0
        print("hexFilePath==",hexFilePath)
        btn = event.GetEventObject()
        btn.Disable()
        serialAll = self.UpdateDownloadFrame()
        if not hexFilePath or not serialAll:
            btn.Enable()
            print("Input invalid,please check you input")
            wx.MessageBox(message="非法输入，请检测输入项！",
                          caption='错误提示',
                          style=wx.OK | wx.ICON_INFORMATION)
            return 0

        for downloadTemp in self.downloadAll:
            print("downloadTemp.serialSelect.GetValue()==",downloadTemp.serialSelect.GetValue())
            if downloadTemp.serialSelect.GetValue():
                self.downloadTaskRecord += 1
                downloadTemp.processBar.SetBarColour(wx.GREEN)
                downloadTemp.processBar.SetValue(0)
                downloadTemp.processStart()
                DownloadThreadTask(self, downloadTemp.serialSelect.GetValue(), hexFilePath)

    def downloadBtnLayout(self):
        downloadBtnSizer = wx.BoxSizer(wx.HORIZONTAL)

        self.btnDownload = wx.Button(self.panel, label='下载', id=wx.ID_ANY, size=(480, 50))
        self.btnDownload.Bind(wx.EVT_BUTTON, self.onBtnDownload)
        downloadBtnSizer.Add(self.btnDownload,0,flag=wx.RIGHT | wx.LEFT, border=8)
        self.mySizer.Add(downloadBtnSizer, 0, flag=wx.RIGHT | wx.LEFT | wx.TOP, border=20)

    def targetFileSelect(self):
        sizerTargetFile = wx.BoxSizer(wx.HORIZONTAL)


        etargetFile = wx.StaticText(self.panel,wx.ID_ANY,"目标文件：")
        sizerTargetFile.Add(etargetFile,0,flag=wx.RIGHT | wx.LEFT, border=8)

        #Edit text
        self.text_ctrl = wx.TextCtrl(self.panel, wx.ID_ANY, size=(400, 30))
        sizerTargetFile.Add(self.text_ctrl,flag=wx.RIGHT | wx.LEFT,border=0)

        #Button open file
        BtFileOpen = wx.Button(self.panel,label='OPEN',id=wx.ID_ANY,size=(50,30))
        sizerTargetFile.Add(BtFileOpen,0,flag=wx.RIGHT | wx.LEFT,border=20)
        BtFileOpen.Bind(wx.EVT_BUTTON, self.fileOpenHandle)

        self.mySizer.Add(sizerTargetFile, 0, flag=wx.TOP, border=10)

    def fileOpenHandle(self,event):
        value = self.text_ctrl.GetValue()
        dlg = wx.FileDialog(self, u"选择文件夹", "", "","Hex files (*.hex)|*.hex",wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        if dlg.ShowModal() == wx.ID_OK:
            print("ID_OK")
            hexFilePath = dlg.GetPath()  # 文件夹路径
            self.text_ctrl.SetValue(hexFilePath)
        dlg.Destroy()

    def updateUI(self,msg):
        param = msg.data
        print("param==",param)
        if DOWNLOAD_EVT_OVER == param[0]:
            print("Download OK",param[1])
            self.downloadTaskRecord -= 1
            for downloadTemp in self.downloadAll:
                if downloadTemp.serialSelect.GetValue() == param[1]:
                    downloadTemp.processBarReusltSuccessed()
        elif DOWNLOAD_EVT_SERIAL_ERROR_HAPPEND == param[0]:
            print("Download ERROR", param[1])
            self.downloadTaskRecord -= 1
            for downloadTemp in self.downloadAll:
                if downloadTemp.serialSelect.GetValue() == param[1]:
                    downloadTemp.processBarReusltFailed()

        if self.downloadTaskRecord <= 0:
            self.btnDownload.Enable()

if __name__ == '__main__':
    app = wx.App()
    fram = MyFrame()
    app.MainLoop()