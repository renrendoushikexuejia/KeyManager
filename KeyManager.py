# 2023年5月5日12:32:20  写一个私钥的管理软件
# 2023年5月13日21:25:49 基本完工
# pyinstaller -w -i E:\Code\KeyManager\key.ico keyManager.py   生成可执行文件的命令

# 保存私钥的json的数据格式如下:
# data = {
#     "项目名称projectName": "示例项目",
#     "创建时间projectCreationTime": "2022-01-01",
#     "备注projectNote": "这是一个示例项目",
#     "私钥数量keyCount": 10
#     "私钥字典keys": {
#         "私钥key1":{            
#             "私钥名称keyName": "示例私钥",
#             "私钥创建时间keyCreationTime": "2022-01-02",
#             "私钥备注keyNote": "这是一个示例私钥",
#             "keyUsed": True,
#             "keyDisabled,": False,
#             "私钥状态3": True,
#             "私钥序号keyNumber": 1,
#             "privateKey": "a1s6f81aw6f135f4a68test",
#             "publicKey":"awefnoaienfiaw",
#             "私钥对应的地址keyAddress": "示例地址",
#             "私钥助记词keyMnemonic": "示例助记词"
#         }
#         "私钥2":{            
#             "私钥名称keyName": "示例私钥",
#             "私钥创建时间keyCreationTime": "2022-01-02",
#             "私钥备注keyNote": "这是一个示例私钥",
#             "私钥状态1": True,
#             "私钥状态2": False,
#             "私钥状态3": True,
#             "私钥序号keyNumber": 1,
#             "privateKey": "a1s6f81aw6f135f4a68test",
#             "publicKey":"awefnoaienfiaw",
#             "私钥对应的地址keyAddress": "示例地址",
#             "私钥助记词keyMnemonic": "示例助记词"
#         }
#     }
# }


import sys,os,json,datetime
from PyQt5.QtWidgets import QMainWindow,QApplication,QMessageBox,QFileDialog,QInputDialog,QTreeWidgetItem
from PyQt5.QtCore import Qt
import pyperclip
from hdwallet import BIP44HDWallet
from hdwallet.utils import generate_mnemonic
# 生成私钥要导入对应的值,例如EthereumMainnet  BitcoinMainnet https://hdwallet.readthedocs.io/en/latest/cryptocurrencies.html
from hdwallet.cryptocurrencies import EthereumMainnet       
from hdwallet.cryptocurrencies import BitcoinMainnet
from hdwallet.derivations import BIP44Derivation
from Ui_KeyManagerForm import Ui_KeyManagerForm
from keyAddForm import keyAdd
 
# 定义全局常量
gDict = {}      # 用于存储当前打开的 .km文件转换成的字典

#定义全局函数

# 根据参数生成对应的私钥 公钥 地址 助记词
def generate_wallets(keyType: str, count: int):
    if keyType.lower() == 'eth':
        cryptocurrency = EthereumMainnet
    elif keyType.lower() == 'btc':
        cryptocurrency = BitcoinMainnet

    wallets = []
    for i in range(count):
        # Generate english mnemonic words
        mnemonic = generate_mnemonic(language="english", strength=128)
        # Secret passphrase/password for mnemonic
        passphrase = None
        # Initialize Ethereum 或者其它 mainnet BIP44HDWallet
        bip44_hdwallet = BIP44HDWallet(cryptocurrency=cryptocurrency)
        # Get Ethereum BIP44HDWallet from mnemonic
        bip44_hdwallet.from_mnemonic(mnemonic=mnemonic, language="english", passphrase=passphrase)
        # Clean default BIP44 derivation indexes/paths
        bip44_hdwallet.clean_derivation()
        # Derivation from Ethereum BIP44 derivation path
        bip44_derivation = BIP44Derivation(cryptocurrency=cryptocurrency, account=0, change=False, address=0)
        # Drive Ethereum BIP44HDWallet
        bip44_hdwallet.from_path(path=bip44_derivation)
        # Append wallet information to list
        wallets.append({
            "mnemonic": mnemonic,
            "private_key": bip44_hdwallet.private_key(),
            "public_key": bip44_hdwallet.public_key(),
            "address": bip44_hdwallet.address()
        })
    return wallets



class KeyManager( QMainWindow, Ui_KeyManagerForm): 

    def __init__(self,parent =None):
        super( KeyManager,self).__init__(parent)
        self.setupUi(self)

        # 打开配置文件，初始化界面数据
        if os.path.exists( "./keyManager.ini"):
            try:
                iniFileDir = os.getcwd() + "\\"+ "keyManager.ini"
                with open( iniFileDir, 'r', encoding="utf-8") as iniFile:
                    iniDict = json.loads( iniFile.read())
                if iniDict:
                    if 'filePath' in iniDict:
                        if iniDict['filePath']:
                            self.labelFilePath.setText(iniDict['filePath'])
                            self.mfRefresh(iniDict['filePath'])
                        

                    if 'folderPath' in iniDict:
                        if iniDict['folderPath']:
                            self.labelFolderPath.setText(iniDict['folderPath'])

            except:
                QMessageBox.about( self, "提示", "打开初始化文件keyManager.ini异常, 软件关闭时会自动重新创建keyManager.ini文件")
        
        # 设置twKey的表头
        self.twKey.setHeaderLabel('项目名称')
        # 初始化分类筛选QComboBox
        self.cbFilter.addItems(["选择筛选条件","是否已启用", "是否已废弃"])

        # 绑定槽函数
        self.btnHelp.clicked.connect(self.mfHelp)
        self.btnNewFile.clicked.connect(self.mfNewFile)
        self.btnOpenFile.clicked.connect(self.mfOpenFile)
        self.btnOpenFolder.clicked.connect(self.mfOpenFolder)
        self.twKey.itemClicked.connect(self.mfClickedTreeItem)
        self.twKey.itemDoubleClicked.connect(self.mfDoubleClickedTreeItem)
        self.cbkmFile.currentIndexChanged.connect(self.mfcbkmFileChanged)
        self.btnKeyAdd.clicked.connect(self.mfKeyAddWindow)
        self.cbFilter.currentIndexChanged.connect(self.mfcbFilterIndexChanged)

        # 绑定界面上的文本框和复选框
        self.cbKeyUsed.stateChanged.connect(self.mfcbKeyUsedStateChanged)
        self.cbKeyDisabled.stateChanged.connect(self.mfcbKeyDisabledStateChanged)
        self.leProjectName.editingFinished.connect(self.mfleProjectNameEditingFinished)
        self.leProjectCreationTime.editingFinished.connect(self.mfleProjectCreationTimeEditingFinished)
        self.pteProjectNote.textChanged.connect(self.mfpteProjectNoteTextChanged)
        self.leKeyName.editingFinished.connect(self.mfleKeyNameEditingFinished)
        self.leKeyNumber.editingFinished.connect(self.mfleKeyNumberEditingFinished)
        self.leKeyCreationTime.editingFinished.connect(self.mfleKeyCreationTimeEditingFinished)
        self.pteKeyNote.textChanged.connect(self.mfpteKeyNoteTextChanged)

    # 已启用复选框cbKeyUsed 状态改变
    def mfcbKeyUsedStateChanged(self):
        global gDict
        item = self.twKey.selectedItems()
        if item:
            key = item[0].text(0).split(' : ')[0]
            if self.cbKeyUsed.isChecked():
                gDict['keys'][key]['keyUsed'] = True
            else:
                gDict['keys'][key]['keyUsed'] = False

    # 废弃复选框cbKeyDisabled 状态改变
    def mfcbKeyDisabledStateChanged(self):
        global gDict
        item = self.twKey.selectedItems()
        if item:
            key = item[0].text(0).split(' : ')[0]
            if self.cbKeyDisabled.isChecked():
                gDict['keys'][key]['keyDisabled'] = True
            else:
                gDict['keys'][key]['keyDisabled'] = False

    # 项目名称文本框leProjectName内容改变
    def mfleProjectNameEditingFinished(self):
        global gDict
        gDict['projectName'] = self.leProjectName.text()

    # 项目创建时间文本框leProjectCreationTime内容改变
    def mfleProjectCreationTimeEditingFinished(self):
        global gDict
        gDict['projectCreationTime'] = self.leProjectCreationTime.text()

    # 项目备注文本框pteProjectNote内容改变
    def mfpteProjectNoteTextChanged(self):
        global gDict
        gDict['projectNote'] = self.pteProjectNote.toPlainText()

    # 密钥名称文本框leKeyName内容改变
    def mfleKeyNameEditingFinished(self):
        global gDict
        item = self.twKey.selectedItems()
        if item:
            key = item[0].text(0).split(' : ')[0]
            gDict['keys'][key]['keyName'] = self.leKeyName.text()
            self.mfSaveFile()
            self.mfRefresh(self.labelFilePath.text())            

    # 密钥序号文本框leKeyNumber内容改变
    def mfleKeyNumberEditingFinished(self):
        global gDict
        item = self.twKey.selectedItems()
        if item:
            key = item[0].text(0).split(' : ')[0]
            gDict['keys'][key]['keyNumber'] = self.leKeyNumber.text()

    # 密钥创建时间文本框leKeyCreationTime内容改变
    def mfleKeyCreationTimeEditingFinished(self):
        global gDict
        item = self.twKey.selectedItems()
        if item:
            key = item[0].text(0).split(' : ')[0]
            gDict['keys'][key]['keyCreationTime'] = self.leKeyCreationTime.text()

    # 密钥备注文本框pteKeyNote内容改变
    def mfpteKeyNoteTextChanged(self):
        global gDict
        item = self.twKey.selectedItems()
        if item:
            key = item[0].text(0).split(' : ')[0]
            gDict['keys'][key]['keyNote'] = self.pteKeyNote.toPlainText()

    # 按cbFilter的条件分类,刷新twKey
    def mfcbFilterIndexChanged(self):
        if self.cbFilter.currentIndex() != 0:
            if self.cbFilter.currentText() == "是否已启用":
                # print('是否已启用')
                self.mftwKeySort("是否已启用")
            elif self.cbFilter.currentText() == "是否已废弃":
                # print('是否已废弃')
                self.mftwKeySort("是否已废弃")

    # 按照参数分类密钥,刷新twKey
    def mftwKeySort(self, sortType):
        global gDict
        self.twKey.clear()
        topItemTrue = QTreeWidgetItem(self.twKey)       # 表示筛选条件为真
        topItemFalse = QTreeWidgetItem(self.twKey)
        if sortType == "是否已启用":
            topItemTrue.setText(0, "已启用")
            topItemFalse.setText(0, "未启用")
            self.twKey.addTopLevelItem(topItemTrue)
            self.twKey.addTopLevelItem(topItemFalse)
        elif sortType == "是否已废弃":
            topItemFalse.setText(0, "可使用")
            self.twKey.addTopLevelItem(topItemFalse)
            topItemTrue.setText(0, "已废弃")
            self.twKey.addTopLevelItem(topItemTrue)
            self.twKey.sortItems(0, 0)      # 对顶节点进行排序(column: int, order: SortOrder) 升序对应数值为0，降序对应数值为1。
            
            
            
        if gDict:
            for key in gDict['keys']:
                maskedPrivateKey = gDict['keys'][key]['privateKey'][:6] + '****' + gDict['keys'][key]['privateKey'][-6:]
                tempStr = key + ' : ' + gDict['keys'][key]['keyName'] + ' : ' + maskedPrivateKey
                tempItem = QTreeWidgetItem()
                tempItem.setText(0, tempStr)

                if sortType == "是否已启用":
                    if gDict['keys'][key]['keyUsed']:
                        topItemTrue.addChild(tempItem)
                    else:
                        topItemFalse.addChild(tempItem)

                elif sortType == "是否已废弃":
                    if gDict['keys'][key]['keyDisabled']:
                        topItemTrue.addChild(tempItem)
                    else:
                        topItemFalse.addChild(tempItem)

        self.twKey.expandAll()      # 展开所有节点


    # 使用帮助按钮  注意事项和免责声明
    def mfHelp(self):
        QMessageBox.about(self, '使用帮助', '1. 点击打开文件夹按钮会在下拉列表框里列出此文件夹下所有的 .km 后缀名文件')

    # 新建文件按钮
    def mfNewFile(self):
        global gDict
        gDict.clear()
        self.twKey.clear()

        try:
            desktopPath = os.path.join(os.path.expanduser("~"), "Desktop")
            tempFolderPath = QFileDialog.getExistingDirectory( self, '选择保存目录', desktopPath, QFileDialog.ShowDirsOnly)
            tempFileName, ok = QInputDialog.getText(self, '新建文件', '请输入新建文件名称:') 
            if ok and tempFolderPath and tempFileName and tempFolderPath != None:
                filePath = tempFolderPath + '/' + tempFileName + '.km'
                if os.path.exists(filePath):
                    QMessageBox.about( self, '提示', '文件名称重复,为了保证数据安全,本软件禁止保存重名文件')
                    return
                f = open( filePath, 'x')
                # 初始化文件中的内容
                gDict = {'projectName':tempFileName, 'projectCreationTime':datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'keyCount': 0,  'projectNote':'新创建的项目,尚未开始操作', 'keys':{}}
                tempJson = json.dumps(gDict, indent=4)
                f.write(tempJson)
                f.close()
            else:
                QMessageBox.about( self, '提示', '文件名或路径错误')
                return

            self.labelFilePath.setText(filePath)
            self.mfRefresh( filePath)
            self.mfKeyAddWindow()

        except:
            QMessageBox.about( self, '提示', '文件创建失败')
            return
        

    # 打开文件按钮, 点击按钮打开文件对话框,获得文件路径,传递给mfRefresh()刷新界面
    def mfOpenFile(self):
        desktopPath = os.path.join(os.path.expanduser("~"), "Desktop")
        # try:
        tempFilePath, uselessFilt = QFileDialog.getOpenFileName( self, '打开keyManager文件', desktopPath, 'keyManager(*.km)', 'keyManager(*.km)')
        if tempFilePath != '':
            self.labelFilePath.setText(tempFilePath)
            # print( '1',tempFilePath)
            self.mfRefresh(tempFilePath)
            # print( '2',tempFilePath)
        else:
            QMessageBox.about( self, "提示", "请选择后缀名为 .km 的文件。")
        # except:
        #     QMessageBox.about( self, "提示", "选择keyManager文件失败,请重新选择。")

    # 打开文件夹按钮,点击打开文件夹按钮,弹出打开文件夹对话框,获得文件夹路径后,搜索所有.km后缀名的文件,并把文件名添加到cbFolderPathList中
    def mfOpenFolder(self):
        self.cbkmFile.clear()
        try:
            desktopPath = os.path.join(os.path.expanduser("~"), "Desktop")
            tempFolderPath = QFileDialog.getExistingDirectory( self, '选择目录', desktopPath, QFileDialog.ShowDirsOnly)

            kmFiles = []

            for root, dirs, files in os.walk(tempFolderPath):
                for file in files:
                    if file.endswith(".km"):
                        full_path = os.path.join(root, file)
                        relative_path = os.path.relpath(full_path, tempFolderPath)
                        kmFiles.append(relative_path)
            
            # print(kmFiles)
            tempItem = "搜索到 " + str(len(kmFiles)) + " 个文件"
            self.cbkmFile.addItem( tempItem)
            self.cbkmFile.addItems(kmFiles)
            self.labelFolderPath.setText(tempFolderPath)
        except:
            QMessageBox.about( self, '提示', '搜索.km文件失败')
            return

    # 下拉列表框self.cbkmFile选择的项改变
    def mfcbkmFileChanged(self):
        rootPath = self.labelFolderPath.text()
        relativePath = self.cbkmFile.currentText()
        # print(rootPath, relativePath)
        filePath = os.path.join(rootPath, relativePath)
        # print(filePath)

        if filePath[-3:] != '.km':
            return
        
        if os.path.exists(filePath):
            self.labelFilePath.setText(filePath)
            self.mfRefresh(filePath)
        else:
            QMessageBox.information(self, "提示", filePath + " 文件不存在")


    # 保存按钮,点击保存,把全局字典gDict转换为json格式,保存在当前打开的文件self.labelFilePath.text()中
    def mfSaveFile(self):
        global gDict
        saveFilePath = self.labelFilePath.text()
        saveJson = json.dumps( gDict, indent=4)
        try:
            saveFile = open( saveFilePath, "w",  encoding="utf-8")
            saveFile.write( saveJson)
            saveFile.close()
        except:
            QMessageBox.about( self, "提示", "保存keyManager数据文件.km失败")

    # 单击twKey中的项   把地址复制到剪贴板,并在界面右边显示被点击项的信息
    def mfClickedTreeItem(self, item, column):
        global gDict
        key = item.text(0).split(' : ')[0]
        if key[0] == 'k':       # 'k'是指'key'的第一个字符. item可能是"已启用" "未启用" "已废弃"这些顶层分类的名字,所以要判断key的值
            pyperclip.copy(gDict['keys'][key]['keyAddress'])
            self.mfDisplayItemInfo(item)

    # 双击twKey中的项   把私钥复制到剪贴板,并在界面右边显示被点击项的信息
    def mfDoubleClickedTreeItem(self, item, column):
        global gDict
        key = item.text(0).split(' : ')[0]
        pyperclip.copy(gDict['keys'][key]['privateKey'])
        self.mfDisplayItemInfo(item)

    # 传递一个twKey中的项,在界面右边显示被点击项的信息
    def mfDisplayItemInfo(self, item):
        global gDict
        key = item.text(0).split(' : ')[0]
        # 更新界面右侧的文本框
        self.leProjectName.setText(gDict['projectName'])
        self.leProjectCreationTime.setText(gDict['projectCreationTime'])
        self.leKeyCount.setText(str(len(gDict['keys'])))
        self.pteProjectNote.setPlainText( gDict['projectNote'])
        self.leKeyName.setText(gDict['keys'][key]['keyName'])
        self.leKeyNumber.setText(str(gDict['keys'][key]['keyNumber']))
        self.leKeyCreationTime.setText(gDict['keys'][key]['keyCreationTime'])
        self.pteKeyNote.setPlainText(gDict['keys'][key]['keyNote'])
        self.ptePrivateKey.setPlainText(gDict['keys'][key]['privateKey'])
        self.ptePublicKey.setPlainText(gDict['keys'][key]['publicKey'])
        self.pteKeyAddress.setPlainText(gDict['keys'][key]['keyAddress'])
        self.pteKeyMnemonic.setPlainText(gDict['keys'][key]['keyMnemonic'])

        if gDict['keys'][key]['keyUsed'] == True:
            self.cbKeyUsed.setChecked(True)
        else:
            self.cbKeyUsed.setChecked(False)
        
        if gDict['keys'][key]['keyDisabled'] == True:
            self.cbKeyDisabled.setChecked(True)
        else:
            self.cbKeyDisabled.setChecked(False)


    # 新增密钥,更新全局字典gDict和刷新twKey
    def mfKeyAddWindow(self):
        self.windowKeyAdd = keyAdd()
        self.windowKeyAdd.show()

        self.windowKeyAdd.signalToKeyManager.connect(self.mfKeyAdd)

    # 根据windowKeyAdd发送过来的参数,创建密钥,并调用mfRefresh刷新界面
    def mfKeyAdd(self, keyType, keyCount):
        # print(keyType, keyCount)
        global gDict
        
        walletsList = generate_wallets(keyType, keyCount)
        for i in walletsList:
            keyNumber = gDict['keyCount'] + 1
            gDict['keyCount'] += 1
            gDict['keys'][f"key{keyNumber}"] = {"keyName": f"key{keyNumber}", 
                                                "keyCreationTime": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 
                                                "keyNote": "There are no key note",
                                                "keyNumber": keyNumber, 
                                                "keyUsed": False,
                                                "keyDisabled": False,
                                                "privateKey": i["private_key"], 
                                                "publicKey": i["public_key"], 
                                                "keyAddress": i["address"], 
                                                "keyMnemonic": i["mnemonic"]
                                                }
            
        # 先保存到文件中,再调用mfRefresh()更新界面
        self.mfSaveFile()
        self.mfRefresh(self.labelFilePath.text())

    # 根据传递的文件路径,刷新lwKey和界面   
    def mfRefresh(self, kmPath):
        global gDict
        self.twKey.clear()
        if not os.path.exists( kmPath):
            QMessageBox.about( self, '提示', '文件名或路径错误,可能是保存的密钥文件.km已被移除')
            self.labelFilePath.setText("选择文件")
            self.labelFolderPath.setText("选择文件夹")
            return
        
        # try:
        with open( kmPath, 'r', encoding="utf-8") as kmFile:
            gDict = json.loads( kmFile.read())
        if gDict:
            # root = QTreeWidgetItem(self.twKey)
            # root.setText(0, gDict['project_name'])
            self.twKey.setHeaderLabel(gDict['projectName'])

            for key in gDict['keys']:
                maskedPrivateKey = gDict['keys'][key]['privateKey'][:6] + '****' + gDict['keys'][key]['privateKey'][-6:]
                tempStr = key + ' : ' + gDict['keys'][key]['keyName'] + ' : ' + maskedPrivateKey
                tempItem = QTreeWidgetItem()
                # tempItem.setCheckState(0, Qt.Checked)
                tempItem.setText(0, tempStr)
                self.twKey.addTopLevelItem( tempItem)

                # print( tempStr)




            # print(gDict['project_name'])

        # except:
        #     QMessageBox.about( self, "提示", "打开.km文件异常, 请检查文件是否正确并重新打开")

        
#主程序入口
if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWin = KeyManager()
    myWin.show()

    appExit = app.exec_()
    #退出程序之前，保存界面上的设置
    myWin.mfSaveFile()      # 保存打开的km文件
    tempDict = { 'filePath':myWin.labelFilePath.text(), 'folderPath':myWin.labelFolderPath.text() }
    saveIniJson = json.dumps( tempDict, indent=4)
    try:
        saveIniFile = open( "./keyManager.ini", "w",  encoding="utf-8")
        saveIniFile.write( saveIniJson)
        saveIniFile.close()
    except:
        QMessageBox.about( myWin, "提示", "保存配置文件keyManager.ini失败")

    sys.exit( appExit)
