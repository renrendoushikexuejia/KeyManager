from PyQt5.QtWidgets import QMainWindow,QCheckBox,QListWidgetItem
from PyQt5.QtCore import pyqtSignal
import win32gui
from Ui_keyAddForm import Ui_keyAddForm

class keyAdd( QMainWindow, Ui_keyAddForm): 
    signalToKeyManager = pyqtSignal(str, int)       # 参数str是密钥类型, int是密钥数量

    def __init__(self,parent =None):
        super( keyAdd,self).__init__(parent)
        self.setupUi(self)

        # 初始化cbKeyType, sbKeyCount
        self.cbKeyType.addItems(['ETH', 'BTC'])
        self.sbKeyCount.setValue(5)

        def mfOK():
            keyType = self.cbKeyType.currentText()
            keyCount = self.sbKeyCount.value()
            
            self.signalToKeyManager.emit( keyType, keyCount)
            self.close()

        #绑定槽函数
        self.btnOK.clicked.connect( mfOK)
