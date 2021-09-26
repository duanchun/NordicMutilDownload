import wx
import time
import string
from threading import Thread
from pynrfjprog import LowLevel
#import nordicEraseAll
import nordicDownloadHex
import NordicMultipleDownload

import wx.lib.agw.pyprogress as pg

TASK_RANGE = 50
# Define notification event for thread completion
EVT_RESULT_ID = wx.NewId()

DOWNLOAD_EVT_OVER  = 51

DOWNLOAD_EVT_SERIAL_ERROR_HAPPEND = 52 + 1


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

class downloadThread(Thread):
    """download thread  class"""
    def __init__(self,wxObject,serial,hexFilePath):
        Thread.__init__(self)
        self.wxObject = wxObject
        self.serial = serial
        self.hexFilePath = hexFilePath
        self.start()


    def run(self):
        """Run Worker Thread."""
        #nordicEraseAll.eraseAll()
        try:
            NordicMultipleDownload.run(self.serial,self.hexFilePath)
        except:
            param = [DOWNLOAD_EVT_SERIAL_ERROR_HAPPEND, self.serial]
            wx.PostEvent(self.wxObject, ResultEvent(param))
            print("NordicMultipleDownload Error happend")
            raise
        # This is the code executing in the new thread.
        #for i in range(50):
         #   time.sleep(1)
          #  wx.PostEvent(self.wxObject, ResultEvent(i))
        #time.sleep(5)
        param = [DOWNLOAD_EVT_OVER,self.serial]
        wx.PostEvent(self.wxObject, ResultEvent(param))

class MyFrame(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title='Hello World',size=(800,600))
        #elf.Move((200,100))
        self.Center()
        self.panel = wx.Panel(self)
        self.my_sizer = wx.BoxSizer(wx.VERTICAL)
        self.targetFileSelect()
        self.panel.SetSizer(self.my_sizer)
        self.initSerial()
        self.downloadProcessTimerInit()
        self.Show()

    def initSerial(self):
        with LowLevel.API(
                LowLevel.DeviceFamily.UNKNOWN) as api:  # Using with construction so there is no need to open or close the API class.
            snr = api.enum_emu_snr()
            print("Snr:", snr)
            index = 0
            if snr is not None:
                for snrB in snr:
                    self.serialSelect.AppendItems(str(snrB))
                    self.serialSelectTwo.AppendItems(str(snrB))
                #api.connect_to_emu_with_snr(snr[0])
                for snrB in snr:
                    print("index==",index)
                    if 0 == index:
                        self.serialSelect.SetValue(str(snrB))
                    elif 1 == index:
                        self.serialSelectTwo.SetValue(str(snrB))
                    index += 1

            else:
                self.btnDownload.Disable()

    def fileOpenHandle(self,event):
        value = self.text_ctrl.GetValue()
        dlg = wx.FileDialog(self, u"选择文件夹", "", "","Hex files (*.hex)|*.hex",wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        if dlg.ShowModal() == wx.ID_OK:
            print("ID_OK")
            self.hexFilePath = dlg.GetPath()  # 文件夹路径
            self.text_ctrl.SetValue(self.hexFilePath)
        dlg.Destroy()

    def targetFileSelect(self):
        self.sizerTargetFile = wx.BoxSizer(wx.HORIZONTAL)


        self.etargetFile = wx.StaticText(self.panel,wx.ID_ANY,"目标文件：")
        self.sizerTargetFile.Add(self.etargetFile,0,flag=wx.RIGHT | wx.LEFT, border=8)

        #Edit text
        self.text_ctrl = wx.TextCtrl(self.panel, wx.ID_ANY, size=(400, 20))
        self.sizerTargetFile.Add(self.text_ctrl,flag=wx.RIGHT | wx.LEFT,border=0)

        #Button open file
        BtFileOpen = wx.Button(self.panel,label='OPEN',id=wx.ID_ANY,size=(50,20))
        self.sizerTargetFile.Add(BtFileOpen,0,flag=wx.RIGHT | wx.LEFT,border=20)
        BtFileOpen.Bind(wx.EVT_BUTTON, self.fileOpenHandle)



        #****************************** Serial one start *******************************
        # Download
        self.downloadOne = wx.BoxSizer(wx.HORIZONTAL)
        # Process Bar
        self.processBarOne = pg.ProgressGauge(self.panel, size=(350,20))
        self.processBarOne.SetGaugeSteps(50)
        #self.processBarOne.SetFirstGradientColour(wx.Colour(1,0,0))
        #self.processBarOne.SetSecondGradientColour(wx.Colour(0,1,0))
        self.processBarOne.SetFirstGradientColour(wx.GREEN)
        self.processBarOne.SetSecondGradientColour(wx.BLUE)
        self.processBarOne.SetGaugeProportion(0.2)
        self.downloadOne.Add(self.processBarOne, 0, flag=wx.RIGHT | wx.LEFT, border=8)

        self.serial = wx.StaticText(self.panel, wx.ID_ANY, "Serial：")
        self.downloadOne.Add(self.serial, 0, flag=wx.RIGHT | wx.LEFT, border=8)

        #Serial select
        self.serialSelect = wx.ComboBox(self.panel, wx.ID_ANY,size=(150,20))
        self.downloadOne.Add(self.serialSelect, 0, flag=wx.RIGHT | wx.LEFT, border=8)

        # ****************************** Serial one end *******************************

        # ****************************** Serial two start *******************************
        # Download
        self.downloadTwo = wx.BoxSizer(wx.HORIZONTAL)
        # Process Bar
        self.processBarTwo = pg.ProgressGauge(self.panel, size=(350, 20))
        self.processBarTwo.SetGaugeSteps(50)
        # self.processBarTwo.SetFirstGradientColour(wx.Colour(1,0,0))
        # self.processBarTwo.SetSecondGradientColour(wx.Colour(0,1,0))
        self.processBarTwo.SetGaugeProportion(0.2)
        self.downloadTwo.Add(self.processBarTwo, 0, flag=wx.RIGHT | wx.LEFT, border=8)

        self.serial = wx.StaticText(self.panel, wx.ID_ANY, "Serial：")
        self.downloadTwo.Add(self.serial, 0, flag=wx.RIGHT | wx.LEFT, border=8)

        # Serial select
        self.serialSelectTwo = wx.ComboBox(self.panel, wx.ID_ANY,size=(150,20))
        self.downloadTwo.Add(self.serialSelectTwo, 0, flag=wx.RIGHT | wx.LEFT, border=8)

        # ****************************** Serial two end *******************************

        self.my_sizer.Add(self.sizerTargetFile, 0, flag=wx.TOP, border=10)

        # Download button
        self.btnDownload = wx.Button(self.panel, label='下载', id=wx.ID_ANY, size=(50, 20))
        self.btnDownload.Bind(wx.EVT_BUTTON, self.onBtnDownload)
        self.my_sizer.Add(self.btnDownload, 0, flag=wx.RIGHT | wx.LEFT | wx.TOP, border=20)
        # Set up event handler for any worker thread results
        EVT_RESULT(self, self.updateUI)

        self.my_sizer.Add(self.downloadOne, 0, flag=wx.TOP, border=20)
        self.my_sizer.Add(self.downloadTwo, 0, flag=wx.TOP, border=20)



    def onBtnDownload(self,event):
        self.hexFilePath = self.text_ctrl.GetValue()
        print("hexFilePath==",self.hexFilePath)
        btn = event.GetEventObject()
        btn.Disable()
        if not self.hexFilePath or not self.serialSelect.GetValue():
            btn.Enable()
            print("Input invalid,please check you input")
            wx.MessageBox(message="非法输入，请检测输入项！",
                          caption='错误提示',
                          style=wx.OK | wx.ICON_INFORMATION)
            return 0
        self.downloadTaskNumRecodFlag = 0
        self.GaugeProcessIndexOne = -1
        self.GaugeProcessIndexTwo = -1

        self.processBarOne.SetFirstGradientColour(wx.GREEN)
        self.processBarOne.SetSecondGradientColour(wx.BLUE)

        self.processBarTwo.SetFirstGradientColour(wx.GREEN)
        self.processBarTwo.SetSecondGradientColour(wx.BLUE)

        self.processBarOne.SetGaugeProportion(0.000001)
        self.processBarTwo.SetGaugeProportion(0.000001)

        #"""
        if self.serialSelect.GetValue():
            try:
                downloadThread(self,self.serialSelect.GetValue(),self.hexFilePath)
                self.downloadTaskNumRecodFlag += 1
                self.GaugeProcessIndexOne += 1
            except:
                print("Error")
        if self.serialSelectTwo.GetValue():
            try:
                downloadThread(self, self.serialSelectTwo.GetValue(), self.hexFilePath)
                self.downloadTaskNumRecodFlag += 1
                self.GaugeProcessIndexTwo += 1
            except:
                print("Error")
        #"""
        if 0 == self.downloadTaskNumRecodFlag:
            self.btnDownload.Enable()
        else:
            print("Start Timer")
            self.timer.Start(200)

    def downloadProcessTimerHandle(self, event):
        print("GaugeProcessIndexOne==",self.GaugeProcessIndexOne)
        print("GaugeProcessIndexTwo==", self.GaugeProcessIndexTwo)
        if -1 != self.GaugeProcessIndexOne:
            self.GaugeProcessIndexOne += 1
            if self.GaugeProcessIndexOne > TASK_RANGE:
                self.processBarOne.SetGaugeProportion(0.999999)
                self.processBarOne.Update
            else:
                print("Proportion==",self.GaugeProcessIndexOne/float(TASK_RANGE))
                self.processBarOne.SetGaugeProportion(self.GaugeProcessIndexOne/float(TASK_RANGE))
                self.processBarOne.Update()
        if -1 != self.GaugeProcessIndexTwo:
            if self.GaugeProcessIndexTwo > TASK_RANGE:
                self.processBarTwo.SetGaugeProportion(0.999999)
            else:
                self.processBarTwo.SetGaugeProportion(float(self.GaugeProcessIndexTwo) / TASK_RANGE)

        time.ctime()

    def downloadProcessTimerInit(self):
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.downloadProcessTimerHandle, self.timer)

    def updateUI(self,msg):
        param = msg.data
        print("param==",param)
        if DOWNLOAD_EVT_OVER == param[0]:
            self.downloadTaskNumRecodFlag -= 1
            if self.downloadTaskNumRecodFlag <= 0:
                self.btnDownload.Enable()
                if -1 != self.GaugeProcessIndexOne:
                    self.processBarOne.SetGaugeProportion(0.999999)
                    self.processBarOne.Update()
                if -1 != self.GaugeProcessIndexTwo:
                    self.processBarTwo.SetGaugeProportion(0.99999999)
                    self.processBarTwo.Update()

                self.timer.Stop()
        elif DOWNLOAD_EVT_SERIAL_ERROR_HAPPEND == param[0]:
            if self.serialSelect.GetValue() == param[1]:
                self.processBarOne.SetGaugeProportion(0.9999999)
                self.processBarOne.SetFirstGradientColour(wx.RED)
                self.processBarOne.SetSecondGradientColour(wx.RED)
                self.processBarOne.Update()
                self.GaugeProcessIndexOne = -1
                print("Seral One Error")

            if self.serialSelectTwo.GetValue() == param[1]:
                self.processBarTwo.SetGaugeProportion(float(self.GaugeProcessIndexOne) / TASK_RANGE)
                self.processBarTwo.SetFirstGradientColour(wx.RED)
                self.processBarTwo.SetSecondGradientColour(wx.RED)
                self.GaugeProcessIndexTwo = -1
                print("Seral Two Error")


if __name__ == '__main__':
    app = wx.App()
    frame = MyFrame()
    app.MainLoop()
