# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/Jenks/maya/scripts/Jenks/scripts/miscScripts/connectToMultipleAttrUI.ui'
#
# Created: Wed Sep 21 14:44:41 2016
#      by: pyside2-uic  running on PySide2 2.0.0~alpha0
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(400, 46)
        self.gridLayout = QtWidgets.QGridLayout(MainWindow)
        self.gridLayout.setObjectName("gridLayout")
        self.connect_btn = QtWidgets.QPushButton(MainWindow)
        self.connect_btn.setObjectName("connect_btn")
        self.gridLayout.addWidget(self.connect_btn, 0, 2, 1, 1)
        self.target_lEdit = QtWidgets.QLineEdit(MainWindow)
        self.target_lEdit.setObjectName("target_lEdit")
        self.gridLayout.addWidget(self.target_lEdit, 0, 0, 1, 1)
        self.result_lEdit = QtWidgets.QLineEdit(MainWindow)
        self.result_lEdit.setObjectName("result_lEdit")
        self.gridLayout.addWidget(self.result_lEdit, 0, 1, 1, 1)

        self.retranslateUi(MainWindow)
        QtCore.QObject.connect(self.result_lEdit, QtCore.SIGNAL("returnPressed()"), self.connect_btn.animateClick)
        QtCore.QObject.connect(self.target_lEdit, QtCore.SIGNAL("returnPressed()"), self.connect_btn.animateClick)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtWidgets.QApplication.translate("MainWindow", "Connect To Multiple Attributes", None, -1))
        self.connect_btn.setText(QtWidgets.QApplication.translate("MainWindow", "Connect", None, -1))
        self.target_lEdit.setPlaceholderText(QtWidgets.QApplication.translate("MainWindow", "Target Attribute", None, -1))
        self.result_lEdit.setPlaceholderText(QtWidgets.QApplication.translate("MainWindow", "Result Attribute", None, -1))

