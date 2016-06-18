#!/usr/bin/env python
import os
import sys
from PyQt5 import QtGui, QtCore, QtWidgets
BASE_DIR = os.getcwd()


class About(QtWidgets.QWidget):

    def __init__(self):
        super(About, self).__init__()
        self.initUI()

    def initUI(self):
        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)

        about_file = open('about.html', 'r')
        about_content = about_file.read()
        content = QtWidgets.QLabel(about_content)
        content.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
        layout.addWidget(content)


class TrainDialog(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super(TrainDialog, self).__init__(parent)
        self.model_name = None
        self.train_len = None
        self.filename = None

        self.progress_log = QtWidgets.QTextEdit()
        self.model_name_edit = QtWidgets.QLineEdit()
        self.train_len_edit = QtWidgets.QLineEdit()
        self.progress = QtWidgets.QProgressBar(self)

        self.initUI()

    def initUI(self):
        model_name = QtWidgets.QLabel('Model Name')
        train_len = QtWidgets.QLabel('Train Size')
        filename = QtWidgets.QLabel('File Path')

        self.model_name_edit.setPlaceholderText("Write Model Name " +
                                                "Ex: Computer")
        self.train_len_edit.setPlaceholderText("Write Train Size Ex: 200")
        self.progress_log.setReadOnly(True)

        btn_filename = QtWidgets.QPushButton('Select', self)
        btn_submit = QtWidgets.QPushButton('Submit', self)
        btn_close = QtWidgets.QPushButton('Close', self)

        btn_filename.clicked.connect(self.getFilename)
        btn_submit.clicked.connect(self.submit)
        btn_close.clicked.connect(self.close)

        grid = QtWidgets.QGridLayout()
        grid.setSpacing(10)

        grid.addWidget(model_name, 1, 0)
        grid.addWidget(self.model_name_edit, 1, 1)

        grid.addWidget(train_len, 2, 0)
        grid.addWidget(self.train_len_edit, 2, 1)

        grid.addWidget(filename, 3, 0)
        grid.addWidget(btn_filename, 3, 1,)

        grid.addWidget(btn_close, 4, 0)
        grid.addWidget(btn_submit, 4, 1)
        grid.addWidget(self.progress, 5, 0, 1, 4)
        grid.addWidget(self.progress_log, 6, 0, 1, 4)
        self.setLayout(grid)

        self.setGeometry(300, 300, 350, 300)
        self.setWindowTitle('Train Model')
        self.show()

    def getFilename(self):
        self.filename, filetype = QtWidgets.QFileDialog.getOpenFileName(
                                  self, 'Open file',
                                  '/home')

    def submit(self):
        self.progress.setValue(10)
        self.model_name = self.model_name_edit.text()
        self.train_len = self.train_len_edit.text()

        # To print the outputs( from stdout) to UI non-Editable TextBox
        from io import StringIO  # Python3
        import sys
        old_stdout = sys.stdout
        result = StringIO()
        sys.stdout = result

        import os
        os.chdir('./classifier/')

        try:
            from openpyxl import load_workbook
            from classifier.model import EssayModel as esyModel
            wb = load_workbook(self.filename)
            ws = wb.active
            data = [[j.value for j in i] for i in ws]
            data = list(zip(*data))
            essay = data[2][1:]
            score = data[6][1:]
            train_len = int(self.train_len)  # training set size
            train_essay = essay[:train_len]
            train_score = score[:train_len]
            test_essay = essay[train_len:]
            train_essay = [i.split() for i in train_essay]
            test_essay = [i.split() for i in test_essay]
            self.progress.setValue(20)
            model = esyModel('./classifier/cspell/files/big.txt')
            self.progress.setValue(30)
            model.train(train_essay, train_score)
            if not os.path.exists(BASE_DIR+'/model/'):
                os.makedirs(BASE_DIR+'/model/')
            model.dump(BASE_DIR+'/model/'+self.model_name)
            self.progress.setValue(90)
            print("Model dumped\n")
            print("-------------------------Model-Info------" +
                  "-------------------")
            print("Model Name: "+self.model_name)
            print("Model Train File: "+self.filename)
            print("Model File: "+BASE_DIR+'/model/'+self.model_name)
            print("Train Size: "+self.train_len)
            print("-------------------------Model-Info-----" +
                  "--------------------")
        except Exception as e:
            print("-------------------------ERROR-----------" +
                  "-------------------")
            print(str(e))
            print("-------------------------ERROR-----------" +
                  "-------------------")

        os.chdir('../')

        sys.stdout = old_stdout
        result_log = result.getvalue()
        self.progress_log.setText(result_log)
        self.progress.setValue(100)


class CentralWidget(QtWidgets.QWidget):

    def __init__(self, file):
        super(CentralWidget, self).__init__()
        self.file = file
        self.text_essay = QtWidgets.QTextEdit()
        self.initUI(file)
        from classifier.model import load_from_file
        self.model = load_from_file(self.file)

    def initUI(self, file):
        grid = QtWidgets.QGridLayout()
        grid.setSpacing(10)
        self.setLayout(grid)

        btn_submit = QtWidgets.QPushButton('Submit')

        btn_submit.clicked.connect(self.submit)
        self.text_essay.setText("Write Essay Here")

        grid.addWidget(self.text_essay, 1, 0)
        grid.addWidget(btn_submit, 2, 0)

    def showDialog(self, mark):
        msgBox = QtWidgets.QMessageBox()
        msgBox.setText("Your Marks is "+str(mark))
        msgBox.exec()

    def submit(self):
        text = self.text_essay.toPlainText()
        t = self.model.predict([text.split()])[0]
        self.showDialog(t)


class Window(QtWidgets.QMainWindow):

    def __init__(self):
        super(Window, self).__init__()
        self.setGeometry(50, 50, 800, 600)
        self.setWindowTitle(" Automated Essay Grading ")
        self.setWindowIcon(QtGui.QIcon(BASE_DIR+'/icons/logo1.png'))
        self.tab = QtWidgets.QTabWidget(self)
        self.tab.setTabsClosable(True)
        self.tab.tabCloseRequested.connect(self.close_handler)
        self.tab.addTab(About(), "About")
        self.initUI()

    def initUI(self):
        btn_exit = QtWidgets.QAction(QtGui.QIcon(
                                     BASE_DIR+'/icons/close.png'),
                                     '&Quit', self)
        btn_loadModel = QtWidgets.QAction(QtGui.QIcon(
                                          BASE_DIR+'/icons/open.png'),
                                          '&Load Model', self)
        btn_trainModel = QtWidgets.QAction(QtGui.QIcon(
                                           BASE_DIR+'/icons/new.png'),
                                           '&Train Model', self)

        btn_exit.setShortcut('Ctrl+Q')
        btn_loadModel.setShortcut('Ctrl+L')
        btn_trainModel.setShortcut('Ctrl+T')

        btn_exit.setStatusTip('Exit Program')
        btn_loadModel.setStatusTip('Load Model To Evalute Essay')
        btn_trainModel.setStatusTip('Load training set to create Model')

        btn_exit.triggered.connect(QtCore.QCoreApplication.instance().quit)
        btn_loadModel.triggered.connect(self.loadModel)
        btn_trainModel.triggered.connect(self.trainModel)

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&FIle')
        fileMenu.addAction(btn_loadModel)
        fileMenu.addAction(btn_trainModel)
        fileMenu.addAction(btn_exit)

        toolbar = self.addToolBar('Exit')
        toolbar.addAction(btn_loadModel)
        toolbar.addAction(btn_trainModel)
        toolbar.addAction(btn_exit)

        self.setCentralWidget(self.tab)

        self.show()

    def close_handler(self, index):
        self.tab.removeTab(index)

    def loadModel(self):
        fname, ftype = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file',
                                                             BASE_DIR+'/model')
        if fname:
            centralWidget = CentralWidget(fname)
            self.tab.addTab(centralWidget,
                            os.path.splitext(os.path.basename(fname))[0])
            self.tab.setCurrentWidget(centralWidget)

    def trainModel(self):
        self.train = TrainDialog()
        self.train.show()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    GUI = Window()
    sys.exit(app.exec_())
