# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/Jenks/maya/scripts/Jenks/scripts/ikSplineCreator/ikSplineCreatorUI.ui'
#
# Created: Fri Dec 16 16:26:58 2016
#      by: pyside2-uic  running on PySide2 2.0.0~alpha0
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(300, 137)
        self.gridLayout = QtWidgets.QGridLayout(MainWindow)
        self.gridLayout.setContentsMargins(10, 10, 10, 10)
        self.gridLayout.setHorizontalSpacing(5)
        self.gridLayout.setVerticalSpacing(6)
        self.gridLayout.setObjectName("gridLayout")
        self.create_btn = QtWidgets.QPushButton(MainWindow)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.create_btn.sizePolicy().hasHeightForWidth())
        self.create_btn.setSizePolicy(sizePolicy)
        self.create_btn.setMinimumSize(QtCore.QSize(0, 40))
        self.create_btn.setObjectName("create_btn")
        self.gridLayout.addWidget(self.create_btn, 2, 1, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 2, 0, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 2, 2, 1, 1)
        self.main_grp = QtWidgets.QGroupBox(MainWindow)
        self.main_grp.setTitle("")
        self.main_grp.setObjectName("main_grp")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.main_grp)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.set_btn = QtWidgets.QPushButton(self.main_grp)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.set_btn.sizePolicy().hasHeightForWidth())
        self.set_btn.setSizePolicy(sizePolicy)
        self.set_btn.setMinimumSize(QtCore.QSize(0, 18))
        self.set_btn.setMaximumSize(QtCore.QSize(50, 16777215))
        self.set_btn.setObjectName("set_btn")
        self.gridLayout_2.addWidget(self.set_btn, 1, 0, 1, 1)
        self.ikName_lab = QtWidgets.QLabel(self.main_grp)
        self.ikName_lab.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.ikName_lab.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.ikName_lab.setObjectName("ikName_lab")
        self.gridLayout_2.addWidget(self.ikName_lab, 0, 0, 1, 2)
        self.ikName_ledit = QtWidgets.QLineEdit(self.main_grp)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ikName_ledit.sizePolicy().hasHeightForWidth())
        self.ikName_ledit.setSizePolicy(sizePolicy)
        self.ikName_ledit.setMinimumSize(QtCore.QSize(0, 18))
        self.ikName_ledit.setObjectName("ikName_ledit")
        self.gridLayout_2.addWidget(self.ikName_ledit, 0, 2, 1, 1)
        self.ctrlName_ledit = QtWidgets.QLineEdit(self.main_grp)
        self.ctrlName_ledit.setObjectName("ctrlName_ledit")
        self.gridLayout_2.addWidget(self.ctrlName_ledit, 1, 1, 1, 2)
        self.gridLayout.addWidget(self.main_grp, 1, 0, 1, 3)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtWidgets.QApplication.translate("MainWindow", "IK Spline Creator", None, -1))
        self.create_btn.setText(QtWidgets.QApplication.translate("MainWindow", "Create Spline IK", None, -1))
        self.set_btn.setText(QtWidgets.QApplication.translate("MainWindow", "Set", None, -1))
        self.ikName_lab.setText(QtWidgets.QApplication.translate("MainWindow", "IK Name", None, -1))
        self.ikName_ledit.setPlaceholderText(QtWidgets.QApplication.translate("MainWindow", "e.g. splineIK", None, -1))
        self.ctrlName_ledit.setPlaceholderText(QtWidgets.QApplication.translate("MainWindow", "Control Name", None, -1))

