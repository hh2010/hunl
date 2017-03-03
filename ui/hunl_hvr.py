# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'hunl_hvr.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_hvr(object):
    def setupUi(self, hvr):
        hvr.setObjectName("hvr")
        hvr.resize(276, 134)
        self.btn_board = QtWidgets.QPushButton(hvr)
        self.btn_board.setGeometry(QtCore.QRect(10, 60, 113, 32))
        self.btn_board.setObjectName("btn_board")
        self.btn_calc = QtWidgets.QPushButton(hvr)
        self.btn_calc.setGeometry(QtCore.QRect(154, 90, 113, 32))
        self.btn_calc.setObjectName("btn_calc")
        self.hero_in = QtWidgets.QLineEdit(hvr)
        self.hero_in.setGeometry(QtCore.QRect(10, 30, 113, 21))
        self.hero_in.setAlignment(QtCore.Qt.AlignCenter)
        self.hero_in.setObjectName("hero_in")
        self.label = QtWidgets.QLabel(hvr)
        self.label.setGeometry(QtCore.QRect(9, 10, 111, 20))
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.board_lbl = QtWidgets.QLabel(hvr)
        self.board_lbl.setGeometry(QtCore.QRect(16, 94, 101, 21))
        self.board_lbl.setFrameShape(QtWidgets.QFrame.Box)
        self.board_lbl.setAlignment(QtCore.Qt.AlignCenter)
        self.board_lbl.setObjectName("board_lbl")
        self.eq_lbl = QtWidgets.QLabel(hvr)
        self.eq_lbl.setGeometry(QtCore.QRect(159, 20, 101, 61))
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.eq_lbl.setFont(font)
        self.eq_lbl.setFrameShape(QtWidgets.QFrame.Box)
        self.eq_lbl.setFrameShadow(QtWidgets.QFrame.Raised)
        self.eq_lbl.setLineWidth(2)
        self.eq_lbl.setAlignment(QtCore.Qt.AlignCenter)
        self.eq_lbl.setObjectName("eq_lbl")

        self.retranslateUi(hvr)
        QtCore.QMetaObject.connectSlotsByName(hvr)

    def retranslateUi(self, hvr):
        _translate = QtCore.QCoreApplication.translate
        hvr.setWindowTitle(_translate("hvr", "Equity: Hand vs Range"))
        self.btn_board.setText(_translate("hvr", "Browse Board"))
        self.btn_calc.setText(_translate("hvr", "Calculate"))
        self.hero_in.setText(_translate("hvr", "AhJd"))
        self.label.setText(_translate("hvr", "Hero Hand"))
        self.board_lbl.setText(_translate("hvr", "No Board!"))
        self.eq_lbl.setText(_translate("hvr", "Equity Value"))

