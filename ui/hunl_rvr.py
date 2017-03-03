# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'hunl_rvr.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_rvr(object):
    def setupUi(self, rvr):
        rvr.setObjectName("rvr")
        rvr.resize(500, 395)
        self.btn_board = QtWidgets.QPushButton(rvr)
        self.btn_board.setGeometry(QtCore.QRect(374, 42, 113, 32))
        self.btn_board.setObjectName("btn_board")
        self.board_lbl = QtWidgets.QLabel(rvr)
        self.board_lbl.setGeometry(QtCore.QRect(380, 20, 101, 21))
        self.board_lbl.setFrameShape(QtWidgets.QFrame.Box)
        self.board_lbl.setAlignment(QtCore.Qt.AlignCenter)
        self.board_lbl.setObjectName("board_lbl")
        self.slide_hero = QtWidgets.QSlider(rvr)
        self.slide_hero.setGeometry(QtCore.QRect(379, 178, 101, 22))
        self.slide_hero.setOrientation(QtCore.Qt.Horizontal)
        self.slide_hero.setObjectName("slide_hero")
        self.lcd_hero = QtWidgets.QLCDNumber(rvr)
        self.lcd_hero.setGeometry(QtCore.QRect(400, 128, 61, 51))
        self.lcd_hero.setDigitCount(2)
        self.lcd_hero.setProperty("intValue", 99)
        self.lcd_hero.setObjectName("lcd_hero")
        self.lcd_vill = QtWidgets.QLCDNumber(rvr)
        self.lcd_vill.setGeometry(QtCore.QRect(401, 258, 61, 51))
        self.lcd_vill.setDigitCount(2)
        self.lcd_vill.setProperty("intValue", 99)
        self.lcd_vill.setObjectName("lcd_vill")
        self.slide_vill = QtWidgets.QSlider(rvr)
        self.slide_vill.setGeometry(QtCore.QRect(380, 308, 101, 22))
        self.slide_vill.setOrientation(QtCore.Qt.Horizontal)
        self.slide_vill.setObjectName("slide_vill")
        self.board_lbl_2 = QtWidgets.QLabel(rvr)
        self.board_lbl_2.setGeometry(QtCore.QRect(380, 100, 101, 21))
        self.board_lbl_2.setFrameShape(QtWidgets.QFrame.Box)
        self.board_lbl_2.setAlignment(QtCore.Qt.AlignCenter)
        self.board_lbl_2.setObjectName("board_lbl_2")
        self.board_lbl_3 = QtWidgets.QLabel(rvr)
        self.board_lbl_3.setGeometry(QtCore.QRect(380, 230, 101, 21))
        self.board_lbl_3.setFrameShape(QtWidgets.QFrame.Box)
        self.board_lbl_3.setAlignment(QtCore.Qt.AlignCenter)
        self.board_lbl_3.setObjectName("board_lbl_3")
        self.btn_graph = QtWidgets.QPushButton(rvr)
        self.btn_graph.setGeometry(QtCore.QRect(373, 350, 113, 32))
        self.btn_graph.setObjectName("btn_graph")

        self.retranslateUi(rvr)
        QtCore.QMetaObject.connectSlotsByName(rvr)

    def retranslateUi(self, rvr):
        _translate = QtCore.QCoreApplication.translate
        rvr.setWindowTitle(_translate("rvr", "Equity: Range vs Range"))
        self.btn_board.setText(_translate("rvr", "Browse Board"))
        self.board_lbl.setText(_translate("rvr", "No Board!"))
        self.board_lbl_2.setText(_translate("rvr", "Hero Range"))
        self.board_lbl_3.setText(_translate("rvr", "Villain Range"))
        self.btn_graph.setText(_translate("rvr", "Create Graph"))

