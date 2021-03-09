from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtSql import *
from PyQt5.QtCore import *
from GUI.windowDialogPrint import Ui_Dialog as Print_Dialog
from GUI.windowDialogCancel import Ui_Dialog as Cancel_Dialog
from GUI.windowLoading import Ui_Dialog as Loading
from GUI.functions import *
from parameters import *
from res.labels import *


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setEnabled(True)
        MainWindow.resize(1210, 780)
        font = QtGui.QFont()
        font.setFamily(FONT)
        font.setPointSize(FONT_SIZE)
        font.setBold(True)
        font.setWeight(50)
        MainWindow.setFont(font)
        MainWindow.setMouseTracking(False)
        MainWindow.setWindowTitle("Vassoi Torrescalla")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(IMG_DIR_PATH + "logo-torre.png"),
                       QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        MainWindow.setAnimated(True)
        MainWindow.setTabShape(QtWidgets.QTabWidget.Triangular)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.horizontalLayout.setContentsMargins(5, 5, 5, 5)
        self.gridWidget = QtWidgets.QWidget(self.centralwidget)
        self.gridWidget.setObjectName("gridWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.gridWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName("gridLayout")
        self.verticalWidget = QtWidgets.QWidget(self.gridWidget)
        self.verticalWidget.setObjectName("verticalWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalWidget)
        self.verticalLayout.setContentsMargins(5, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(self.verticalWidget)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.pushButton_2 = QtWidgets.QPushButton(self.verticalWidget)
        self.pushButton_2.setMinimumSize(QtCore.QSize(200, 80))
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_2.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.verticalLayout.addWidget(self.pushButton_2)
        self.pushButton = QtWidgets.QPushButton(self.verticalWidget)
        self.pushButton.setMinimumSize(QtCore.QSize(0, 80))
        self.pushButton.setObjectName("pushButton")
        self.pushButton.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        # self.pushButton_3 = QtWidgets.QPushButton(self.verticalWidget)
        # self.pushButton_3.setMinimumSize(QtCore.QSize(0, 80))
        # self.pushButton_3.setObjectName("pushButton_3")
        # self.pushButton_3.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        # self.verticalLayout.addWidget(self.pushButton_3)
        self.pushButton_4 = QtWidgets.QPushButton(self.verticalWidget)
        self.pushButton_4.setMinimumSize(QtCore.QSize(0, 80))
        self.pushButton_4.setObjectName("pushButton_4")
        self.pushButton_4.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.verticalLayout.addWidget(self.pushButton_4)
        spacerItem = QtWidgets.QSpacerItem(20, 80, QtWidgets.QSizePolicy.Minimum,
                                           QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.verticalLayout.addWidget(self.pushButton)

        self.label_4 = QtWidgets.QLabel(self.verticalWidget)
        self.label_4.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.label_4.setText("")
        self.label_4.setPixmap(QtGui.QPixmap(IMG_DIR_PATH + "logo-torre-small.png"))
        self.label_4.setScaledContents(False)
        self.label_4.setAlignment(QtCore.Qt.AlignCenter)
        self.label_4.setObjectName("label_4")
        self.verticalLayout.addWidget(self.label_4)
        self.gridLayout.addWidget(self.verticalWidget, 0, 1, 1, 1)
        self.verticalWidget_2 = QtWidgets.QWidget(self.gridWidget)
        self.verticalWidget_2.setObjectName("verticalWidget_2")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.verticalWidget_2)
        self.verticalLayout_3.setContentsMargins(0, 0, 3, 0)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.label_2 = QtWidgets.QLabel(self.verticalWidget_2)
        self.label_2.setObjectName("label_2")
        self.verticalLayout_3.addWidget(self.label_2)
        self.tableView_2 = QtWidgets.QTableView(self.verticalWidget_2)
        self.tableView_2.setObjectName("tableView_2")
        self.verticalLayout_3.addWidget(self.tableView_2)
        self.label_3 = QtWidgets.QLabel(self.verticalWidget_2)
        self.label_3.setObjectName("label_3")
        self.verticalLayout_3.addWidget(self.label_3)
        self.tableView = QtWidgets.QTableView(self.verticalWidget_2)
        self.tableView.setMaximumHeight(int(200))
        self.tableView.setObjectName("tableView")
        self.verticalLayout_3.addWidget(self.tableView)
        self.gridLayout.addWidget(self.verticalWidget_2, 0, 0, 1, 1)
        self.horizontalLayout.addWidget(self.gridWidget)
        MainWindow.setCentralWidget(self.centralwidget)
        self.label_status_bar = QtWidgets.QLabel()
        self.label_status_bar.setObjectName("label_label_status_bar")
        self.label_status_bar.setText(STATBAR_INIT_MES)
        self.statusBar = QtWidgets.QStatusBar(MainWindow)
        self.statusBar.setObjectName("statusBar")
        self.statusBar.addPermanentWidget(self.label_status_bar)
        MainWindow.setStatusBar(self.statusBar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        # Crea connessione QSql al database
        self.create_connection()

        # Pressione dei tre pulsanti a destra
        self.pushButton.clicked.connect(self.on_pushbutton1_clicked)
        self.pushButton_2.clicked.connect(self.on_pushbutton2_clicked)
        # self.pushButton_3.clicked.connect(self.on_pushbutton3_clicked)
        self.pushButton_4.clicked.connect(self.on_pushbutton4_clicked)

        # Refresha tabelle un secondo dopo l'avvio
        QTimer.singleShot(1000, self.init_table_segnati)
        QTimer.singleShot(1000, self.init_table_non_segnati)
        QTimer.singleShot(1000, self.set_clock)

        # Mutex vari
        self.mutex = QMutex()

        # Thread di refresh tabelle GUI
        refreshTableWorker = RefreshGUIWorker()
        refreshTableWorker.signals.refresh.connect(self.init_table_segnati)
        refreshTableWorker.signals.refresh.connect(self.init_table_non_segnati)
        refreshTableWorker.signals.refresh.connect(self.set_clock)
        refreshTableWorker.signals.internet_error.connect(lambda: self.statusBar.showMessage(STATBAR_NO_INTERNET_MES,
                                                                                             NO_INTERNET_TIMEOUT))

        # Inizializza pool di thread
        self.threadpool = QThreadPool()
        self.threadpool.start(refreshTableWorker)
        # print("Numero massimo di threads -> %d" % self.threadpool.maxThreadCount
        #       ())

    def init_table_segnati(self):
        if verify_db() is False:
            self.statusBar.showMessage(STATBAR_DB_CONN_ERROR_MES)
        else:
            self.QSql_db = QSqlDatabase.database("database tray")
            self.model = QSqlQueryModel()
            self.model.setQuery(SELECT_SIGNED_TRAYS_QUERY, self.QSql_db)
            self.tableView.setModel(self.model)
            self.tableView.setFont(QtGui.QFont(FONT, FONT_SIZE))
            self.tableView.setCornerButtonEnabled(False)
            self.tableView.setStyleSheet("QHeaderView {background-color: transparent;}")
            self.tableView.setStyleSheet("QScrollBar:vertical { width: 35px; }")
            self.tableView.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
            self.tableView.setFocusPolicy(Qt.NoFocus)
            # Print all buttons in list
            for i in range(0, self.model.rowCount()):
                if self.model.record(i).value("name") is not None:
                    self.tableView.setIndexWidget(self.model.index(i, 2),
                                                  self.PrintPushButton(self.model.record(i).value("name"),
                                                                       self.model.record(i).value("diet")))
                    self.tableView.setRowHeight(i, 50)
            self.model.setHeaderData(0, Qt.Horizontal, "Nome")
            self.model.setHeaderData(1, Qt.Horizontal, "Dieta")
            self.model.setHeaderData(2, Qt.Horizontal, "")
            self.model.setHeaderData(3, Qt.Horizontal, "")
            self.tableView.setColumnWidth(0, 455)
            self.tableView.setColumnWidth(1, 455)
            self.tableView.setColumnWidth(2, 90)
            self.tableView.hideColumn(3)
            self.tableView.hideColumn(4)
            self.QSql_db.close()

    def init_table_non_segnati(self):
        if verify_db() is False:
            self.statusBar.showMessage(STATBAR_DB_CONN_ERROR_MES)
        else:
            self.QSql_db = QSqlDatabase.database("database tray")
            self.model = QSqlQueryModel()
            self.model.setQuery(SELECT_NOT_SIGNED_TRAYS_QUERY, self.QSql_db)
            self.tableView_2.setModel(self.model)
            self.tableView_2.setFont(QtGui.QFont(FONT, FONT_SIZE))
            self.tableView_2.setCornerButtonEnabled(False)
            self.tableView_2.setStyleSheet("QHeaderView {background-color: transparent;}")
            self.tableView_2.setStyleSheet("QScrollBar:vertical { width: 35px; }")
            self.tableView_2.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
            self.tableView_2.setFocusPolicy(Qt.NoFocus)
            # Print all buttons in list
            for i in range(0, self.model.rowCount()):
                if self.model.record(i).value("name") is not None:
                    self.tableView_2.setIndexWidget(self.model.index(i, 2),
                                                    self.PrintPushButton(self.model.record(i).value("name"),
                                                                         self.model.record(i).value("diet")))
                    self.tableView_2.setRowHeight(i, 50)
            for i in range(0, self.model.rowCount()):
                if self.model.record(i).value("name") is not None:
                    self.tableView_2.setIndexWidget(self.model.index(i, 3),
                                                    self.CancelPushButton(self.model.record(i).value("name")))
                    self.tableView_2.setRowHeight(i, 50)
            #            ______________________________________________________
            #           /    Nome   |     Dieta     |      |      |            \
            #           |¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯|
            #           |______________________________________________________|
            #           |           |               |      |      |            |
            #           | Tizio     |  Vegetariano  |  🖨  |   ✘  |            |
            #           |___________|_______________|______|______|____________|
            #           |                                                      |
            #           \______________________________________________________/
            self.model.setHeaderData(0, Qt.Horizontal, "Nome")
            self.model.setHeaderData(1, Qt.Horizontal, "Dieta")
            self.model.setHeaderData(2, Qt.Horizontal, "")
            self.model.setHeaderData(3, Qt.Horizontal, "")
            self.tableView_2.setColumnWidth(0, 410)
            self.tableView_2.setColumnWidth(1, 410)
            self.tableView_2.setColumnWidth(2, 90)
            self.tableView_2.setColumnWidth(3, 90)
            self.tableView_2.hideColumn(4)
            self.tableView_2.hideColumn(5)
            self.QSql_db.close()

    def PrintPushButton(self, name, dieta):
        tablePushButtonPrint = QtWidgets.QPushButton()
        tablePushButtonPrint.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        tablePushButtonPrint.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(IMG_DIR_PATH + "printer.png"),
                       QtGui.QIcon.Normal, QtGui.QIcon.Off)
        tablePushButtonPrint.setIcon(icon)
        tablePushButtonPrint.clicked.connect(lambda: self.on_tablePushButtonPrint_clicked(name, dieta))
        return tablePushButtonPrint

    def CancelPushButton(self, name):
        tablePushButtonCancel = QtWidgets.QPushButton()
        tablePushButtonCancel.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        tablePushButtonCancel.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(IMG_DIR_PATH + "cancel.png"),
                       QtGui.QIcon.Normal, QtGui.QIcon.Off)
        tablePushButtonCancel.setIcon(icon)
        tablePushButtonCancel.clicked.connect(lambda: self.on_tablePushButtonCancel_clicked(name))
        return tablePushButtonCancel

    def on_tablePushButtonPrint_clicked(self, name, dieta):
        logger = get_logger('on_tablePushButtonPrint_clicked()')
        logger.info('richiesta stampa per ' + name)
        self.statusBar.showMessage(STATBAR_TRAY_PRINT_REQUEST_MES.format(name))
        print_queue = []
        print_queue.append((name, dieta))
        res = start_print_process(print_queue.copy())
        if res != 0:
            self.statusBar.showMessage(STATBAR_PRINT_SUCCESS_MES, STATUS_BAR_TIMEOUT)
            sign_tray(name)
            self.init_table_segnati()
            self.init_table_non_segnati()
        else:
            self.statusBar.showMessage(STATBAR_PRINT_ERROR_MES)

    def on_tablePushButtonCancel_clicked(self, name):
        logger = get_logger('on_tablePushButtonCancel_clicked()')
        Dialog = QtWidgets.QDialog()
        Dialog.setModal(True)
        ui = Cancel_Dialog()
        ui.setupUi(Dialog)
        Dialog.show()
        response = Dialog.exec_()
        if response == QtWidgets.QDialog.Accepted:
            logger.info(name + ' cancellato')
            self.statusBar.showMessage(STATBAR_TRAY_CANCEL_MES.format(name), STATUS_BAR_TIMEOUT)
            delete_tray_from_view(name)
            self.init_table_segnati()
            self.init_table_non_segnati()
        else:
            self.statusBar.showMessage(STATBAR_TRAY_CANCEL_ABORT_MES, STATUS_BAR_TIMEOUT)
            logger.info("cancellazione annullata")

    def on_pushbutton1_clicked(self):
        logger = get_logger('on_pushbutton1_clicked()')
        logger.info("Pressione tasto 'Stampa segnati'")
        Dialog = QtWidgets.QDialog()
        Dialog.setModal(True)
        ui = Print_Dialog()
        ui.setupUi(Dialog)
        Dialog.show()
        QTimer.singleShot(30000, Dialog.reject)
        response = Dialog.exec_()
        if response == QtWidgets.QDialog.Accepted:
            logger.info("Pressione tasto 'Ok' -> Richiesta di stampa")
            self.statusBar.showMessage(STATBAR_PRINT_REQUEST_MES)
            print_queue = create_signed_queue()
            res = start_print_process(print_queue.copy())
            if res != 0:
                self.statusBar.showMessage(STATBAR_PRINT_SUCCESS_MES, STATUS_BAR_TIMEOUT)

            else:
                logger.info("Pressione tasto 'Annulla' -> Annullamento...")
                self.statusBar.showMessage(STATBAR_PRINT_ERROR_MES)
        else:
            logger.info("Pressione tasto 'Annulla' -> Annullamento...")
            self.statusBar.showMessage(STATBAR_PRINT_ABORTED_MES, STATUS_BAR_TIMEOUT)

    def on_pushbutton2_clicked(self):
        logger = get_logger('on_pushbutton2_clicked()')
        logger.info("Pressione tasto 'Stampa non segnati'")
        Dialog = QtWidgets.QDialog()
        Dialog.setModal(True)
        ui = Print_Dialog()
        ui.setupUi(Dialog)
        Dialog.show()
        QTimer.singleShot(30000, Dialog.reject)
        response = Dialog.exec_()
        if response == QtWidgets.QDialog.Accepted:
            logger.info("Pressione tasto 'Ok' -> Richiesta di stampa")
            self.statusBar.showMessage(STATBAR_PRINT_REQUEST_MES)
            print_queue = create_not_signed_queue()
            res = start_print_process(print_queue.copy())
            if res != 0:
                for i in print_queue:
                    sign_tray(i[0])
                self.init_table_segnati()
                self.init_table_non_segnati()
                self.statusBar.showMessage(STATBAR_PRINT_SUCCESS_MES, STATUS_BAR_TIMEOUT)
            else:
                self.statusBar.showMessage(STATBAR_PRINT_ERROR_MES)
        else:
            logger.info("Pressione tasto 'Annulla' -> Annullamento...")
            self.statusBar.showMessage(STATBAR_PRINT_ABORTED_MES, STATUS_BAR_TIMEOUT)

    # def on_pushbutton3_clicked(self):
    #     logger = get_logger('on_pushbutton1_clicked()')
    #     logger.info("Pressione tasto 'Stampa tutti'")
    #     Dialog = QtWidgets.QDialog()
    #     Dialog.setModal(True)
    #     ui = Print_Dialog()
    #     ui.setupUi(Dialog)
    #     Dialog.show()
    #     QTimer.singleShot(30000, Dialog.reject)
    #     response = Dialog.exec_()
    #     if response == QtWidgets.QDialog.Accepted:
    #         logger.info("Pressione tasto 'Ok' -> Richiesta di stampa")
    #         self.statusBar.showMessage(STATBAR_PRINT_REQUEST_MES)
    #         signed_queue = create_signed_queue()
    #         not_signed_queue = create_not_signed_queue()
    #         if len(signed_queue) > 0:
    #             queue = signed_queue
    #             if len(not_signed_queue) > 0:
    #                 queue = queue + not_signed_queue
    #         elif len(not_signed_queue) > 0:
    #             queue = not_signed_queue
    #         else:
    #             queue = []
    #         if len(queue) > 0:
    #             res = start_print_process(queue.copy())
    #             if res != 0:
    #                 if len(not_signed_queue) > 0:
    #                     for i in not_signed_queue:
    #                         sign_tray(i[0])
    #                 self.statusBar.showMessage(STATBAR_PRINT_SUCCESS_MES, STATUS_BAR_TIMEOUT)
    #                 self.init_table_segnati()
    #                 self.init_table_non_segnati()
    #             else:
    #                 self.statusBar.showMessage(STATBAR_PRINT_ERROR_MES)
    #     else:
    #         logger.info("Pressione tasto 'Annulla' -> Annullamento...")
    #         self.statusBar.showMessage(STATBAR_PRINT_ABORTED_MES, STATUS_BAR_TIMEOUT)

    def on_pushbutton4_clicked(self):
        Dialog = QtWidgets.QDialog()
        Dialog.setModal(True)
        Dialog.setWindowFlags(Qt.SplashScreen)
        ui = Loading()
        ui.setupUi(Dialog)
        logger = get_logger('on_pushbutton4_clicked()')
        logger.info("Tasto 'Aggiorna' premuto -> Aggiornamento interfaccia...")
        worker = UpdateDBWorker(self.update_gui_thread, self.mutex)
        Dialog.show()
        worker.signals.done.connect(self.init_table_segnati)
        worker.signals.done.connect(self.init_table_non_segnati)
        worker.signals.done.connect(self.set_clock)
        worker.signals.done.connect(lambda: self.statusBar.showMessage(STATBAR_UPDATE_MES, STATUS_BAR_TIMEOUT))
        worker.signals.done.connect(lambda: logger.info('interfaccia aggiornata'))
        worker.signals.done.connect(lambda: Dialog.done(QtWidgets.QDialog.Accepted))
        self.threadpool.start(worker)

    def update_gui_thread(self):
        # print('thread started')
        db_update()
        # print("thread ended")

    def set_clock(self):
        self.QSql_db = QSqlDatabase.database("database tray")
        self.model = QSqlQueryModel()
        self.model.setQuery(SELECT_CLOCK_QUERY, self.QSql_db)
        self.label_status_bar.setText(STATBAR_LAST_UPDATE_TEMPLATE + str(self.model.record(0).value("last_update")))
        self.QSql_db.close()

    def QSql_db_connect(self, connection_name):
        self.QSql_db = QSqlDatabase.addDatabase("QSQLITE", connection_name)
        self.QSql_db.setDatabaseName(DB_FILE_PATH)
        if not self.QSql_db.open():
            raise Exception("Could not open the database")

    def create_connection(self):
        QSql_db = QSqlDatabase.addDatabase("QSQLITE", "database tray")
        QSql_db.setDatabaseName(DB_FILE_PATH)
        if not QSql_db.open():
            raise Exception("Could not open the database")

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        self.label.setText(_translate("MainWindow", "Comandi:"))
        self.pushButton.setText(_translate("MainWindow", "Ristampa"))
        self.pushButton_2.setText(_translate("MainWindow", "Stampa"))
        # self.pushButton_3.setText(_translate("MainWindow", "Stampa tutti"))
        self.pushButton_4.setText(_translate("MainWindow", "Aggiorna"))
        self.label_2.setText(_translate("MainWindow", "Vassoi da stampare:"))
        self.label_3.setText(_translate("MainWindow", "Vassoi stampati:"))


class UpdateDBWorker(QRunnable):
    def __init__(self, function, mutex, *args, **kwargs):
        super(UpdateDBWorker, self).__init__()
        self.function = function
        self.signals = MyWorkerSignals()
        self.args = args
        self.kwargs = kwargs
        self.mutex = mutex

    @pyqtSlot()
    def run(self):
        if self.mutex.tryLock():
            self.function(*self.args, **self.kwargs)
            self.signals.done.emit()
            self.mutex.unlock()


class RefreshGUIWorker(QRunnable):
    def __init__(self):
        super(RefreshGUIWorker, self).__init__()
        self.signals = MyWorkerSignals()

    @pyqtSlot()
    def run(self):
        logger = get_logger('RefreshGUIWorker thread')

        # Inizializza connessione al database
        QSql_db = QSqlDatabase.addDatabase("QSQLITE", "thread")
        QSql_db.setDatabaseName(DB_FILE_PATH)
        if not QSql_db.open():
            raise Exception("Could not open the database")

        # Inizializza tutte le tabelle
        tabellaNonSegnati = QSqlQueryModel()
        tabellaNonSegnati.setQuery(SELECT_NOT_SIGNED_TRAYS_QUERY, QSql_db)
        prevTabellaNonSegnati = QSqlQueryModel()
        prevTabellaNonSegnati.setQuery(SELECT_NOT_SIGNED_TRAYS_QUERY, QSql_db)
        tabellaSegnati = QSqlQueryModel()
        tabellaSegnati.setQuery(SELECT_SIGNED_TRAYS_QUERY, QSql_db)
        prevTabellaSegnati = QSqlQueryModel()
        prevTabellaSegnati.setQuery(SELECT_SIGNED_TRAYS_QUERY, QSql_db)

        # Main thread loop
        while 1:
            if verify_internet() is False:
                self.signals.internet_error.emit()
            if not QSql_db.open():
                raise Exception("Could not open the database")

            # Reinit tabelle
            tabellaNonSegnati.setQuery(SELECT_NOT_SIGNED_TRAYS_QUERY, QSql_db)
            tabellaSegnati.setQuery(SELECT_SIGNED_TRAYS_QUERY, QSql_db)

            # Creazione liste di segnati e non segnati
            lista_non_segnati = []
            for i in range(0, tabellaNonSegnati.rowCount()):
                lista_non_segnati.append(tabellaNonSegnati.record(i).value("name"))
            prev_lista_non_segnati = []
            for i in range(0, prevTabellaNonSegnati.rowCount()):
                prev_lista_non_segnati.append(prevTabellaNonSegnati.record(i).value("name"))
            lista_segnati = []
            for i in range(0, tabellaSegnati.rowCount()):
                lista_segnati.append(tabellaSegnati.record(i).value("name"))
            prev_lista_segnati = []
            for i in range(0, prevTabellaSegnati.rowCount()):
                prev_lista_segnati.append(prevTabellaSegnati.record(i).value("name"))

            # Controlla se esistono cambiamenti ed emetti un segnale
            if prev_lista_non_segnati != lista_non_segnati or prev_lista_segnati != lista_segnati:
                prevTabellaNonSegnati.setQuery(SELECT_NOT_SIGNED_TRAYS_QUERY, QSql_db)
                prevTabellaSegnati.setQuery(SELECT_SIGNED_TRAYS_QUERY, QSql_db)
                self.signals.refresh.emit()
                logger.info("Cambiamento trovato -> Refresh delle tabelle")

            QSql_db.close()
            time.sleep(5)


class MyWorkerSignals(QObject):
    done = pyqtSignal()
    refresh = pyqtSignal()
    internet_error = pyqtSignal()


def runGUI():
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    MainWindow.showFullScreen()
    sys.exit(app.exec_())


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    # MainWindow.showFullScreen()
    sys.exit(app.exec_())
