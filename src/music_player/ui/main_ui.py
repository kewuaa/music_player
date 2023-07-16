# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main.ui'
##
## Created by: Qt User Interface Compiler version 6.5.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QComboBox, QFrame, QGridLayout,
    QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QScrollArea, QSizePolicy, QSlider, QSpacerItem,
    QVBoxLayout, QWidget)
from . import icons_rc

class Ui_App(object):
    def setupUi(self, App):
        if not App.objectName():
            App.setObjectName(u"App")
        App.resize(752, 538)
        icon = QIcon()
        icon.addFile(u":/pic/icons/title.png", QSize(), QIcon.Normal, QIcon.Off)
        App.setWindowIcon(icon)
        self.gridLayout = QGridLayout(App)
        self.gridLayout.setObjectName(u"gridLayout")
        self.widget = QWidget(App)
        self.widget.setObjectName(u"widget")
        self.widget.setMinimumSize(QSize(637, 61))
        self.horizontalLayout = QHBoxLayout(self.widget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.home_pushButton = QPushButton(self.widget)
        self.home_pushButton.setObjectName(u"home_pushButton")

        self.horizontalLayout.addWidget(self.home_pushButton)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.api_comboBox = QComboBox(self.widget)
        self.api_comboBox.setObjectName(u"api_comboBox")

        self.horizontalLayout.addWidget(self.api_comboBox)

        self.search_lineEdit = QLineEdit(self.widget)
        self.search_lineEdit.setObjectName(u"search_lineEdit")

        self.horizontalLayout.addWidget(self.search_lineEdit)

        self.search_pushButton = QPushButton(self.widget)
        self.search_pushButton.setObjectName(u"search_pushButton")

        self.horizontalLayout.addWidget(self.search_pushButton)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_2)


        self.gridLayout.addWidget(self.widget, 0, 0, 1, 2)

        self.widget_2 = QWidget(App)
        self.widget_2.setObjectName(u"widget_2")
        self.widget_2.setMinimumSize(QSize(120, 341))

        self.gridLayout.addWidget(self.widget_2, 1, 0, 1, 1)

        self.widget_4 = QWidget(App)
        self.widget_4.setObjectName(u"widget_4")
        self.widget_4.setMinimumSize(QSize(511, 341))
        self.verticalLayout = QVBoxLayout(self.widget_4)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.scrollArea = QScrollArea(self.widget_4)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setFrameShadow(QFrame.Raised)
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 588, 343))
        self.verticalLayout_4 = QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.result_verticalLayout = QVBoxLayout()
        self.result_verticalLayout.setObjectName(u"result_verticalLayout")

        self.verticalLayout_4.addLayout(self.result_verticalLayout)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout.addWidget(self.scrollArea)


        self.gridLayout.addWidget(self.widget_4, 1, 1, 1, 1)

        self.widget_3 = QWidget(App)
        self.widget_3.setObjectName(u"widget_3")
        self.widget_3.setMinimumSize(QSize(631, 80))
        self.gridLayout_2 = QGridLayout(self.widget_3)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.horizontalSlider = QSlider(self.widget_3)
        self.horizontalSlider.setObjectName(u"horizontalSlider")
        self.horizontalSlider.setMinimumSize(QSize(531, 18))
        self.horizontalSlider.setOrientation(Qt.Horizontal)

        self.gridLayout_2.addWidget(self.horizontalSlider, 0, 0, 1, 1)

        self.label = QLabel(self.widget_3)
        self.label.setObjectName(u"label")
        self.label.setMinimumSize(QSize(54, 16))
        self.label.setAlignment(Qt.AlignCenter)

        self.gridLayout_2.addWidget(self.label, 0, 1, 1, 1)

        self.widget_5 = QWidget(self.widget_3)
        self.widget_5.setObjectName(u"widget_5")
        self.widget_5.setMinimumSize(QSize(601, 31))
        self.horizontalLayout_2 = QHBoxLayout(self.widget_5)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_3)

        self.pushButton_3 = QPushButton(self.widget_5)
        self.pushButton_3.setObjectName(u"pushButton_3")
        icon1 = QIcon()
        icon1.addFile(u":/pic/icons/previous.png", QSize(), QIcon.Normal, QIcon.Off)
        self.pushButton_3.setIcon(icon1)

        self.horizontalLayout_2.addWidget(self.pushButton_3)

        self.pushButton_4 = QPushButton(self.widget_5)
        self.pushButton_4.setObjectName(u"pushButton_4")
        icon2 = QIcon()
        icon2.addFile(u":/pic/icons/play.png", QSize(), QIcon.Normal, QIcon.Off)
        self.pushButton_4.setIcon(icon2)

        self.horizontalLayout_2.addWidget(self.pushButton_4)

        self.pushButton_5 = QPushButton(self.widget_5)
        self.pushButton_5.setObjectName(u"pushButton_5")
        icon3 = QIcon()
        icon3.addFile(u":/pic/icons/next.png", QSize(), QIcon.Normal, QIcon.Off)
        self.pushButton_5.setIcon(icon3)

        self.horizontalLayout_2.addWidget(self.pushButton_5)

        self.horizontalSpacer_4 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_4)


        self.gridLayout_2.addWidget(self.widget_5, 1, 0, 1, 2)


        self.gridLayout.addWidget(self.widget_3, 2, 0, 1, 2)


        self.retranslateUi(App)

        QMetaObject.connectSlotsByName(App)
    # setupUi

    def retranslateUi(self, App):
        App.setWindowTitle(QCoreApplication.translate("App", u"music_player", None))
        self.home_pushButton.setText(QCoreApplication.translate("App", u"home", None))
        self.search_pushButton.setText(QCoreApplication.translate("App", u"\u641c\u7d22", None))
        self.label.setText(QCoreApplication.translate("App", u"00 / 00", None))
        self.pushButton_3.setText("")
        self.pushButton_4.setText("")
        self.pushButton_5.setText("")
    # retranslateUi

