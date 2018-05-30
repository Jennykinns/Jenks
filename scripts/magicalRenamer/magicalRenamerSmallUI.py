# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/Jenks/maya/scripts/Jenks/scripts/magicalRenamer/magicalRenamerSmallUI.ui'
#
# Created: Sun Oct 15 16:14:00 2017
#      by: pyside2-uic  running on PySide2 2.0.0~alpha0
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(400, 40)
        MainWindow.setMinimumSize(QtCore.QSize(400, 40))
        MainWindow.setMaximumSize(QtCore.QSize(400, 40))
        MainWindow.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.gridLayout = QtWidgets.QGridLayout(MainWindow)
        self.gridLayout.setContentsMargins(2, 2, 2, 2)
        self.gridLayout.setVerticalSpacing(2)
        self.gridLayout.setObjectName("gridLayout")
        self.main_Grp = QtWidgets.QGroupBox(MainWindow)
        self.main_Grp.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.main_Grp.setTitle("")
        self.main_Grp.setObjectName("main_Grp")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.main_Grp)
        self.gridLayout_3.setContentsMargins(4, 2, 4, 2)
        self.gridLayout_3.setVerticalSpacing(4)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.mainGrid_Lay = QtWidgets.QGridLayout()
        self.mainGrid_Lay.setHorizontalSpacing(5)
        self.mainGrid_Lay.setVerticalSpacing(0)
        self.mainGrid_Lay.setObjectName("mainGrid_Lay")
        self.side_Cbox = QtWidgets.QComboBox(self.main_Grp)
        self.side_Cbox.setMinimumSize(QtCore.QSize(0, 20))
        self.side_Cbox.setMaximumSize(QtCore.QSize(45, 20))
        self.side_Cbox.setObjectName("side_Cbox")
        self.side_Cbox.addItem("")
        self.side_Cbox.addItem("")
        self.side_Cbox.addItem("")
        self.mainGrid_Lay.addWidget(self.side_Cbox, 0, 1, 1, 1)
        self.mini_Btn = QtWidgets.QPushButton(self.main_Grp)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.mini_Btn.sizePolicy().hasHeightForWidth())
        self.mini_Btn.setSizePolicy(sizePolicy)
        self.mini_Btn.setMinimumSize(QtCore.QSize(0, 0))
        self.mini_Btn.setMaximumSize(QtCore.QSize(15, 15))
        self.mini_Btn.setObjectName("mini_Btn")
        self.mainGrid_Lay.addWidget(self.mini_Btn, 0, 0, 1, 1)
        self.rename_Ledit = QtWidgets.QLineEdit(self.main_Grp)
        self.rename_Ledit.setMinimumSize(QtCore.QSize(0, 20))
        self.rename_Ledit.setMaximumSize(QtCore.QSize(16777215, 20))
        self.rename_Ledit.setObjectName("rename_Ledit")
        self.mainGrid_Lay.addWidget(self.rename_Ledit, 0, 2, 1, 2)
        self.rename_Btn = QtWidgets.QPushButton(self.main_Grp)
        self.rename_Btn.setMinimumSize(QtCore.QSize(0, 20))
        self.rename_Btn.setMaximumSize(QtCore.QSize(75, 20))
        self.rename_Btn.setDefault(False)
        self.rename_Btn.setObjectName("rename_Btn")
        self.mainGrid_Lay.addWidget(self.rename_Btn, 0, 4, 1, 1)
        self.gridLayout_3.addLayout(self.mainGrid_Lay, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.main_Grp, 2, 0, 1, 1)

        self.retranslateUi(MainWindow)
        QtCore.QObject.connect(self.rename_Ledit, QtCore.SIGNAL("returnPressed()"), self.rename_Btn.animateClick)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        MainWindow.setTabOrder(self.side_Cbox, self.rename_Ledit)
        MainWindow.setTabOrder(self.rename_Ledit, self.rename_Btn)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtWidgets.QApplication.translate("MainWindow", "Jenks\' Magical Renamer: Reloaded", None, -1))
        self.side_Cbox.setItemText(0, QtWidgets.QApplication.translate("MainWindow", "C", None, -1))
        self.side_Cbox.setItemText(1, QtWidgets.QApplication.translate("MainWindow", "L", None, -1))
        self.side_Cbox.setItemText(2, QtWidgets.QApplication.translate("MainWindow", "R", None, -1))
        self.mini_Btn.setText(QtWidgets.QApplication.translate("MainWindow", "v", None, -1))
        self.rename_Ledit.setPlaceholderText(QtWidgets.QApplication.translate("MainWindow", "Rename", None, -1))
        self.rename_Btn.setText(QtWidgets.QApplication.translate("MainWindow", "Rename", None, -1))

