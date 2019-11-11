from PyQt5 import QtCore, QtGui, QtWidgets
from parameters import *


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(300, 100)
        font = QtGui.QFont()
        font.setFamily(FONT)
        font.setPointSize(FONT_SIZE)
        Dialog.setFont(font)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(IMG_DIR_PATH + "logo-torre.png"),
                       QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Dialog.setWindowIcon(icon)
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setContentsMargins(20, 20, 20, 20)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label_2 = QtWidgets.QLabel(Dialog)
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.verticalLayout.addWidget(self.label_2)
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)

        self.movie = QtGui.QMovie(IMG_DIR_PATH + "upload_2.gif")
        self.movie.setScaledSize(QtCore.QSize(30, 30))
        self.label.setMovie(self.movie)
        self.movie.start()

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", " "))
        self.label_2.setText(_translate("Dialog", "Aggiornando..."))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())
