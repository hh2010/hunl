#!/usr/bin/env python
# -*- coding: utf-8 -*-

import lib.hunl_fn as hunl
from lib.hunl_fn import Range, plotEqDistn
from ui.hunl_main import Ui_main
from ui.hunl_hvr import Ui_hvr
from ui.hunl_rvr import Ui_rvr
import sys
import matplotlib
from PyQt5.QtWidgets import (QMainWindow, QTextEdit, QWidget, QDialog,
    QAction, QFileDialog, QApplication, QPushButton, QLineEdit, QMessageBox)
from PyQt5 import QtWidgets
from PyQt5.QtGui import QIcon
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

### Set up our HUNL functions ###

def printRange(hand, board, top):
    vill = hunl.Range()
    vill.setToTop(top, board)
    eq = hunl.getEquityVsRange(hand, vill, hunl.EquityArray(board))
    return eq

def parseboard(board):
    board_lst = [board[i:i+2] for i in range(0, len(board), 2)]
    board_lst = board_lst + (["__"] * (5-len(board_lst)))
    board_lst = hunl.pe_string2card(board_lst)
    return board_lst

def parseboard_str(board):
    board_lst = [board[i:i+2] for i in range(0, len(board), 2)]
    board_lst = board_lst + (["__"] * (5-len(board_lst)))
    board = " ".join(board_lst)
    return board

def parsehand(hand):
    hand_lst = [hand[i:i+2] for i in range(0, len(hand), 2)]
    hand_lst = hunl.pe_string2card(hand_lst)
    return hand_lst

### GUI: Main Window ###

class nl(QMainWindow, Ui_main):
    def __init__(self):
        super(nl, self).__init__()
        self.setupUi(self)
        self.main()

    def main(self):
        self.hvr_btn.clicked.connect(self.show_hvr)
        self.rvr_btn.clicked.connect(self.show_rvr)
        self.tb_btn.clicked.connect(self.show_tb)
        self.fp_btn.clicked.connect(self.show_fp)
        self.show()

    def show_hvr(self):
        _hvr = hvr(self)
        _hvr.show()

    def show_rvr(self):
        _rvr = rvr(self)
        _rvr.show()

    def show_tb(self):
        msg_tb = "Tree builder not implemented yet!"
        QMessageBox.warning(self, "Error!", msg_tb, QMessageBox.Ok)

    def show_fp(self):
        msg_fp = "Fictitious play not implemented yet!"
        QMessageBox.warning(self, "Error!", msg_fp, QMessageBox.Ok)

### GUI: HVR Window ###

class hvr(QMainWindow, Ui_hvr):

    def __init__(self, parent):
        super(hvr, self).__init__(parent)
        self.setParent(parent)
        self.setupUi(self)
        self.board = parseboard("")
        self.board_lbl.setText(parseboard_str(""))
        self.main()

    def main(self):
        self.btn_board.clicked.connect(self.showDialog)
        self.btn_calc.clicked.connect(self.prange)

    def prange(self):
        if len(self.hero_in.text()) != 4:
            msg = "Invalid hand specified!"
            QMessageBox.warning(self, "Error!", msg, QMessageBox.Ok)
            return
        if self.board == "":
            msg_board = "ERROR: No board set!"
            QMessageBox.warning(self, "Error!", msg_board, QMessageBox.Ok)
            return
        hand = parsehand(self.hero_in.text())
        eq = "{0:.1f}%".format(100*printRange(hand, self.board, 1.0))
        if eq == "-100.0%":
            msg_conf = "ERROR: Hand conflicts with board"
            QMessageBox.warning(self, "Error!", msg_conf, QMessageBox.Ok)
            return
        self.eq_lbl.setText(eq)

    def showDialog(self):
        fname = QFileDialog.getOpenFileName(self, 'Open file', '~/eqarray')
        fn = fname[0].split('.')[0]
        cds = fn[fn.rfind('/')+1:]
        self.board = parseboard(cds)
        self.board_lbl.setText(parseboard_str(cds))

## GUI: Range vs Range Window ###

class rvr(QMainWindow, Ui_rvr):

    def __init__(self, parent):
        super(rvr, self).__init__(parent)
        self.setParent(parent)
        self.setupUi(self)
        self.board = parseboard("")
        self.board_lbl.setText(parseboard_str(""))
        self.main()

    def main(self):
        m = PlotCanvas(self, width=3.5, height=3.75)
        m.move(5,5)
        self.slide_hero.valueChanged.connect(self.lcd_hero.display)
        self.slide_vill.valueChanged.connect(self.lcd_vill.display)
        self.btn_board.clicked.connect(self.showDialog)
        self.btn_graph.clicked.connect(lambda: m.eqplot(self.lcd_hero.value()/100, self.lcd_vill.value()/100, self.board))

    def showDialog(self):
        fname = QFileDialog.getOpenFileName(self, 'Open file', '~/eqarray')
        fn = fname[0].split('.')[0]
        cds = fn[fn.rfind('/')+1:]
        self.board = parseboard(cds)
        self.board_lbl.setText(parseboard_str(cds))

class PlotCanvas(FigureCanvas):

    def __init__(self, parent=None, width=4, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.ax = fig.add_subplot(111)

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QtWidgets.QSizePolicy.Expanding,
                                   QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        self.board = parent.board
        self.lcd_hero_val = parent.lcd_hero.value()/100
        self.lcd_vill_val = parent.lcd_vill.value()/100
        self.eqplot(self.lcd_hero_val, self.lcd_vill_val, self.board)

    def eqplot(self, r1, r2, board):
        rng1 = Range(1.0)
        rng2 = Range(1.0)
        rng1.setToTop(r1, self.board)
        rng2.setToTop(r2, self.board)
        self.ax.cla()
        self.xs, self.ys = plotEqDistn(rng1, rng2, board)
        self.ax.plot(self.xs, self.ys)
        self.draw()


        # self.ax.plt.xlabel('Hero Hand Combos')
        # self.ax.plt.ylabel('Hero Equity %')

# Initialize the application
if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('./ui/ace.png'))
    hh = nl()
    sys.exit(app.exec_())
