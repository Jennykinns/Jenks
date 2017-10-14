# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/Jenks/maya/scripts/Jenks/scripts/miscScripts/moveAttrUI.ui'
#
# Created: Mon Oct 17 20:22:15 2016
#      by: pyside2-uic  running on PySide2 2.0.0~alpha0
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(150, 36)
        self.horizontalLayout = QtWidgets.QHBoxLayout(MainWindow)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.up_Btn = QtWidgets.QPushButton(MainWindow)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.up_Btn.sizePolicy().hasHeightForWidth())
        self.up_Btn.setSizePolicy(sizePolicy)
        self.up_Btn.setObjectName("up_Btn")
        self.horizontalLayout.addWidget(self.up_Btn)
        self.down_Btn = QtWidgets.QPushButton(MainWindow)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.down_Btn.sizePolicy().hasHeightForWidth())
        self.down_Btn.setSizePolicy(sizePolicy)
        self.down_Btn.setObjectName("down_Btn")
        self.horizontalLayout.addWidget(self.down_Btn)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtWidgets.QApplication.translate("MainWindow", "-", None, -1))
        self.up_Btn.setText(QtWidgets.QApplication.translate("MainWindow", "Up", None, -1))
        self.down_Btn.setText(QtWidgets.QApplication.translate("MainWindow", "Down", None, -1))

