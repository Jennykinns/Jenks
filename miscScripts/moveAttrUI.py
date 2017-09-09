# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:/Users/Jenks/Documents/maya/scripts/Jenks/scripts/moveAttr/moveAttrUI.ui'
#
# Created: Fri Jul 01 22:21:43 2016
#      by: pyside-uic 0.2.14 running on PySide 1.2.0
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(150, 36)
        self.horizontalLayout = QtGui.QHBoxLayout(MainWindow)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.up_Btn = QtGui.QPushButton(MainWindow)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.up_Btn.sizePolicy().hasHeightForWidth())
        self.up_Btn.setSizePolicy(sizePolicy)
        self.up_Btn.setObjectName("up_Btn")
        self.horizontalLayout.addWidget(self.up_Btn)
        self.down_Btn = QtGui.QPushButton(MainWindow)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.down_Btn.sizePolicy().hasHeightForWidth())
        self.down_Btn.setSizePolicy(sizePolicy)
        self.down_Btn.setObjectName("down_Btn")
        self.horizontalLayout.addWidget(self.down_Btn)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "-", None, QtGui.QApplication.UnicodeUTF8))
        self.up_Btn.setText(QtGui.QApplication.translate("MainWindow", "Up", None, QtGui.QApplication.UnicodeUTF8))
        self.down_Btn.setText(QtGui.QApplication.translate("MainWindow", "Down", None, QtGui.QApplication.UnicodeUTF8))

