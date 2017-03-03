# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'hunl.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(273, 101)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.bbtn = QtWidgets.QPushButton(self.centralwidget)
        self.bbtn.setGeometry(QtCore.QRect(20, 10, 113, 32))
        self.bbtn.setFocusPolicy(QtCore.Qt.NoFocus)
        self.bbtn.setObjectName("bbtn")
        self.hero_in = QtWidgets.QLineEdit(self.centralwidget)
        self.hero_in.setGeometry(QtCore.QRect(133, 14, 113, 20))
        self.hero_in.setObjectName("hero_in")
        self.eqbtn = QtWidgets.QPushButton(self.centralwidget)
        self.eqbtn.setGeometry(QtCore.QRect(20, 40, 231, 32))
        self.eqbtn.setFocusPolicy(QtCore.Qt.NoFocus)
        self.eqbtn.setObjectName("eqbtn")
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionTest = QtWidgets.QAction(MainWindow)
        self.actionTest.setObjectName("actionTest")

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "HH Equity Calculator"))
        self.bbtn.setText(_translate("MainWindow", "Board"))
        self.hero_in.setText(_translate("MainWindow", "Hero Hand"))
        self.eqbtn.setText(_translate("MainWindow", "Run"))
        self.actionTest.setText(_translate("MainWindow", "test"))

