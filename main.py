import lib.hunl_fn as hunl
from ui.hunl_design import Ui_MainWindow
import sys
import matplotlib
from PyQt5.QtWidgets import (QMainWindow, QTextEdit, QWidget, QDialog,
    QAction, QFileDialog, QApplication, QPushButton, QLineEdit, QMessageBox)
from PyQt5 import QtWidgets
from PyQt5.QtGui import QIcon
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

### Set up our HUNL functions

def printRange(hand, board, top):
    vill = hunl.Range()
    vill.setToTop(top, board)
    eq = hunl.getEquityVsRange(hand, vill, hunl.EquityArray(board))
    return eq

### This is the code to set up GUI interface ###

class nl(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(nl, self).__init__()
        self.setupUi(self)
        self.main()

    def main(self):
        ## The button to choose the board to run equity calc
        self.bbtn.clicked.connect(self.showDialog)

        ## The button to run equity calc
        # self.eqbtn.clicked.connect(self.prange)
        self.eqbtn.clicked.connect(self.showEq)

    def showEq(self):
        eq = rvr(self)
        eq.show()

    def showDialog(self):
        fname = QFileDialog.getOpenFileName(self, 'Open file', '~/eqarray')
        fn = fname[0].split('.')[0]
        cds = fn[fn.rfind('/')+1:]
        self.board = self.parseboard(cds)
        self.board_lbl = cds

    def parseboard(self, board):
        board_lst = [board[i:i+2] for i in range(0, len(board), 2)]
        board_lst = board_lst + (["__"] * (5-len(board_lst)))
        board_lst = hunl.pe_string2card(board_lst)
        return board_lst

    def parsehand(self, hand):
        hand_lst = [hand[i:i+2] for i in range(0, len(hand), 2)]
        hand_lst = hunl.pe_string2card(hand_lst)
        return hand_lst

    def prange(self):
        if len(self.hero_in.text()) != 4:
            msg = "Invalid hand specified!"
            QMessageBox.warning(self, "Error!", msg, QMessageBox.Ok)
            return
        if self.board == "":
            msg_board = "ERROR: No board set!"
            QMessageBox.warning(self, "Error!", msg_board, QMessageBox.Ok)
            return
        hand = self.parsehand(self.hero_in.text())
        eq = "{0:.1f}%".format(100*printRange(hand, self.board, 1.0))
        if eq == "-100.0%":
            msg_conf = "ERROR: Hand conflicts with board"
            QMessageBox.warning(self, "Error!", msg_conf, QMessageBox.Ok)
            return
        QMessageBox.information(self, "Result", eq, QMessageBox.Ok)

# This is our Matplotlib canvas for equity charts

class rvr(QMainWindow):

    def __init__(self, parent):
        super(rvr, self).__init__(parent)
        self.setParent(parent)
        self.left = 10
        self.top = 10
        self.title = 'Range vs Range Equity Distributions'
        self.width = 640
        self.height = 400
        self.board = parent.board

        self.eqUI()

    def eqUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        m = PlotCanvas(self, width=4, height=4)
        m.move(0,0)

class PlotCanvas(FigureCanvas):

    def __init__(self, parent=None, width=4, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QtWidgets.QSizePolicy.Expanding,
                                   QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        self.board = parent.board
        self.eqplot(self.board)

    def eqplot(self, board):
        self.xs, self.ys = hunl.plotEqDistn(hunl.Range(1.0), hunl.Range(0.8), self.board)
        ax = self.figure.add_subplot(111)
        ax.plot(self.xs, self.ys)
        ax.x
        self.draw()

# Initialize the application

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('./ui/ace.png'))
    ex = nl()
    ex.show()
    sys.exit(app.exec_())
