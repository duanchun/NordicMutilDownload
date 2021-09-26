
import  sys

from  cx_Freeze  import  setup  ,  Executable

base  =   None
if  sys .  platform  ==   "win32"  :
    base  =   "Win32GUI"

setup  (
        name  =   "NordicMultiDownloadApp"  ,
        version  =   "0.1"  ,
        description  =   "Nordic SOC Multiption download tool"  ,
        executables  =   [  Executable  ( "nordicSigleDownload.py"  ,  base  =  base  )])