#!/usr/bin/env python
import os
import sys
import json
from PyQt5 import QtGui, QtCore, QtWidgets
from functools import partial
BASE_DIR = os.getcwd()


class EmittingStream(QtCore.QObject):

    textWritten = QtCore.pyqtSignal(str)

    def write(self, text):
        self.textWritten.emit(str(text))


class About(QtWidgets.QWidget):

    def __init__(self, parent):
        super(About, self).__init__()
        self.initUI(parent)

    def initUI(self, parent):
        # Recent File List
        Vrecent_box = QtWidgets.QVBoxLayout()
        Vrecent_box.setSpacing(10)

        # About extracted from file
        about_file = open('about.html', 'r')
        about_content = about_file.read()
        content = QtWidgets.QLabel(about_content)
        content.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)

        # Recent files list extraction
        recent_header = '<h4>Recent Essay Model</h4>'
        Vrecent_box.addWidget(QtWidgets.QLabel(recent_header))
        try:
            recent_models_json = open('recent.json', 'r')
            recent_models_dict = json.loads(recent_models_json.read())
            btn_recent = []
            Hrecent_box = []
            for key, value in sorted(recent_models_dict.items(), reverse=True):
                Hrecent_box.append(QtWidgets.QHBoxLayout())
                btn_recent.append(QtWidgets.QPushButton('Open', self))

                lb_recent = QtWidgets.QLabel(': '.join([key, value['name']]))
                btn_recent[-1].clicked.connect(partial(parent.loadModel,
                                               recent=key))

                Hrecent_box[-1].addWidget(lb_recent)
                Hrecent_box[-1].addWidget(btn_recent[-1])
                Vrecent_box.addLayout(Hrecent_box[-1])
        except FileNotFoundError:
            if os.path.isfile('recent.json') is False:
                recent_models_json = open('recent.json', 'w')
            Vrecent_box.addWidget(QtWidgets.QLabel('Empty'))

        # ScrollArea init
        scrollArea = QtWidgets.QScrollArea()
        scrollContent = QtWidgets.QWidget()

        scrollArea.setWidget(scrollContent)
        scrollContent.setLayout(Vrecent_box)

        scrollArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        scrollArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        scrollArea.setWidgetResizable(True)
        scrollArea.setBackgroundRole(QtGui.QPalette.Light)

        # Main Layout of the tab About
        grid = QtWidgets.QGridLayout()
        grid.setSpacing(10)
        self.setLayout(grid)

        grid.addWidget(content, 1, 0)
        grid.addWidget(scrollArea, 2, 0)


class TrainDialog(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super(TrainDialog, self).__init__(parent)
        self.model_name = None
        self.train_len = None
        self.filename = None

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
        self.setLayout(grid)

        self.setGeometry(300, 300, 350, 300)
        self.setWindowTitle('Train Model')
        self.show()

    def getFilename(self):
        self.filename, filetype = QtWidgets.QFileDialog.getOpenFileName(
                                  self, 'Open file',
                                  '/home')

    def submit(self):
        try:
            import os
            os.chdir('./classifier/')

            self.progress.setValue(10)
            self.model_name = self.model_name_edit.text()
            self.train_len = self.train_len_edit.text()

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
            os.chdir(BASE_DIR)

            with open('recent.json', 'r+') as recent_models_json:
                if os.stat('recent.json').st_size != 0:
                    recent_models_dict = json.loads(recent_models_json.read())
                else:
                    recent_models_dict = {}
                recent_models_dict[len(recent_models_dict)+1] = {
                        'name': self.model_name,
                        'train_file': self.filename,
                        'train_size': self.train_len,
                        'model_file': BASE_DIR+'/model/'+self.model_name
                        }
                recent_models_json.seek(0)
                recent_models_json.write(json.dumps(recent_models_dict))
                recent_models_json.truncate()

            self.progress.setValue(100)
        except Exception as e:
            os.chdir(BASE_DIR)
            print("-------------------------ERROR-----------" +
                  "-------------------")
            print(str(e))
            print("-------------------------ERROR-----------" +
                  "-------------------")


class CentralWidget(QtWidgets.QWidget):

    def __init__(self, file):
        super(CentralWidget, self).__init__()
        self.file = file

        self.text_essay = QtWidgets.QTextEdit()
        self.text_essay.setText("Write Essay Here")

        self.initUI(file)
        from classifier.model import load_from_file
        self.model = load_from_file(self.file)
        print("Model Load successfully : Model Location = "+self.file)

    def initUI(self, file):
        # Input Grid init
        input_grid = QtWidgets.QGridLayout()
        input_grid.setSpacing(10)

        btn_submit = QtWidgets.QPushButton('Submit')
        btn_submit.clicked.connect(self.submit)

        input_grid.addWidget(self.text_essay, 1, 0)
        input_grid.addWidget(btn_submit, 2, 0)

        # Info Grid init
        info_grid = QtWidgets.QGridLayout()
        info_grid.setSpacing(10)

        essay_location = QtWidgets.QLabel(self.file)

        info_grid.addWidget(essay_location, 1, 0)

        # Main Widget of the Essay
        grid = QtWidgets.QGridLayout()
        tab = QtWidgets.QTabWidget()

        self.setLayout(grid)
        grid.addWidget(tab)

        input_widget = QtWidgets.QWidget()
        info_widget = QtWidgets.QWidget()
        input_widget.setLayout(input_grid)
        info_widget.setLayout(info_grid)

        tab.addTab(input_widget, "Evaluate")
        tab.addTab(info_widget, "INFO")

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
        self.about = About(self)
        self.tab.addTab(self.about, "About")

        self.stdout_log = QtWidgets.QTextEdit()
        sys.stdout = EmittingStream(textWritten=self.normalOutputWritten)
        sys.stderr = EmittingStream(textWritten=self.normalOutputWritten)

        self.initUI()

    def initUI(self):
        # Toolbar buttons init
        btn_exit = QtWidgets.QAction(QtGui.QIcon(
                                     BASE_DIR+'/icons/close.png'),
                                     '&Quit', self)
        btn_loadModel = QtWidgets.QAction(QtGui.QIcon(
                                          BASE_DIR+'/icons/open.png'),
                                          '&Load Model', self)
        btn_trainModel = QtWidgets.QAction(QtGui.QIcon(
                                           BASE_DIR+'/icons/new.png'),
                                           '&Train Model', self)
        btn_fullscreen = QtWidgets.QAction(QtGui.QIcon(
                                           BASE_DIR +
                                           '/icons/full-screen-icon.png'),
                                           '&Fullscreen', self)

        # Toolbar buttons shortcuts
        btn_loadModel.setShortcut('Ctrl+L')
        btn_trainModel.setShortcut('Ctrl+T')
        btn_fullscreen.setShortcut('Ctrl+F')
        btn_exit.setShortcut('Ctrl+Q')

        # Toolbar buttons status
        btn_loadModel.setStatusTip('Load Model To Evalute Essay')
        btn_trainModel.setStatusTip('Load training set to create Model')
        btn_fullscreen.setStatusTip('Switch Fullscreen')
        btn_exit.setStatusTip('Exit Program')

        # Log TextEdit
        self.stdout_log.setReadOnly(True)
        self.stdout_log.setMaximumHeight(self.tab.sizeHint().
                                         height() * (1/1.5))

        # Toolbar buttons connet function
        btn_exit.triggered.connect(QtCore.QCoreApplication.instance().quit)
        btn_loadModel.triggered.connect(partial(self.loadModel, recent=None))
        btn_trainModel.triggered.connect(self.trainModel)
        btn_fullscreen.triggered.connect(self.toogle_fullscreen)

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&FIle')
        fileMenu.addAction(btn_trainModel)
        fileMenu.addAction(btn_loadModel)
        fileMenu.addAction(btn_fullscreen)
        fileMenu.addAction(btn_exit)

        toolbar = self.addToolBar('Exit')
        toolbar.addAction(btn_trainModel)
        toolbar.addAction(btn_loadModel)
        toolbar.addAction(btn_fullscreen)
        toolbar.addAction(btn_exit)

        grid = QtWidgets.QVBoxLayout()
        grid_widget = QtWidgets.QWidget()
        grid.setSpacing(10)
        grid.addWidget(self.tab)
        grid.addWidget(self.stdout_log)
        grid_widget.setLayout(grid)
        self.setCentralWidget(grid_widget)

        self.show()

    def toogle_fullscreen(self):
        if self.windowState() & QtCore.Qt.WindowFullScreen:
            self.showNormal()
        else:
            self.showFullScreen()

    def normalOutputWritten(self, text):
        """Append text to the QTextEdit."""
        # Maybe QTextEdit.append() works as well, but this is how I do it:
        cursor = self.stdout_log.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertText(text)
        self.stdout_log.setTextCursor(cursor)
        self.stdout_log.ensureCursorVisible()

    def close_handler(self, index):
        self.tab.removeTab(index)

    def loadModel(self, recent=None):
        if recent is None:
            fname, ftype = QtWidgets.QFileDialog.getOpenFileName(
                           self, 'Open file',
                           BASE_DIR+'/model')
        else:
            recent_models_json = open('recent.json', 'r')
            recent_models_dict = json.loads(recent_models_json.read())
            fname = recent_models_dict[recent]['model_file']

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
