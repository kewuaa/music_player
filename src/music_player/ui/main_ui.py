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
        icon1 = QIcon()
        icon1.addFile(u":/pic/icons/home.png", QSize(), QIcon.Normal, QIcon.Off)
        self.home_pushButton.setIcon(icon1)

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
        icon2 = QIcon()
        icon2.addFile(u":/pic/icons/search.png", QSize(), QIcon.Normal, QIcon.Off)
        self.search_pushButton.setIcon(icon2)

        self.horizontalLayout.addWidget(self.search_pushButton)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_2)

        self.login_pushButton = QPushButton(self.widget)
        self.login_pushButton.setObjectName(u"login_pushButton")
        icon3 = QIcon()
        icon3.addFile(u":/pic/icons/login.png", QSize(), QIcon.Normal, QIcon.Off)
        self.login_pushButton.setIcon(icon3)

        self.horizontalLayout.addWidget(self.login_pushButton)


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
        self.progress_Slider = QSlider(self.widget_3)
        self.progress_Slider.setObjectName(u"progress_Slider")
        self.progress_Slider.setEnabled(False)
        self.progress_Slider.setMinimumSize(QSize(531, 18))
        self.progress_Slider.setOrientation(Qt.Horizontal)

        self.gridLayout_2.addWidget(self.progress_Slider, 0, 0, 1, 1)

        self.progress_label = QLabel(self.widget_3)
        self.progress_label.setObjectName(u"progress_label")
        self.progress_label.setMinimumSize(QSize(54, 16))
        self.progress_label.setAlignment(Qt.AlignCenter)

        self.gridLayout_2.addWidget(self.progress_label, 0, 1, 1, 1)

        self.widget_5 = QWidget(self.widget_3)
        self.widget_5.setObjectName(u"widget_5")
        self.widget_5.setMinimumSize(QSize(601, 31))
        self.horizontalLayout_2 = QHBoxLayout(self.widget_5)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_3)

        self.previous_song_pushButton = QPushButton(self.widget_5)
        self.previous_song_pushButton.setObjectName(u"previous_song_pushButton")
        icon4 = QIcon()
        icon4.addFile(u":/pic/icons/previous.png", QSize(), QIcon.Normal, QIcon.Off)
        self.previous_song_pushButton.setIcon(icon4)

        self.horizontalLayout_2.addWidget(self.previous_song_pushButton)

        self.toggle_play_state_pushButton = QPushButton(self.widget_5)
        self.toggle_play_state_pushButton.setObjectName(u"toggle_play_state_pushButton")
        icon5 = QIcon()
        icon5.addFile(u":/pic/icons/play.png", QSize(), QIcon.Normal, QIcon.Off)
        self.toggle_play_state_pushButton.setIcon(icon5)

        self.horizontalLayout_2.addWidget(self.toggle_play_state_pushButton)

        self.next_song_pushButton = QPushButton(self.widget_5)
        self.next_song_pushButton.setObjectName(u"next_song_pushButton")
        icon6 = QIcon()
        icon6.addFile(u":/pic/icons/next.png", QSize(), QIcon.Normal, QIcon.Off)
        self.next_song_pushButton.setIcon(icon6)

        self.horizontalLayout_2.addWidget(self.next_song_pushButton)

        self.stop_play_pushButton = QPushButton(self.widget_5)
        self.stop_play_pushButton.setObjectName(u"stop_play_pushButton")
        icon7 = QIcon()
        icon7.addFile(u":/pic/icons/stop.png", QSize(), QIcon.Normal, QIcon.Off)
        self.stop_play_pushButton.setIcon(icon7)

        self.horizontalLayout_2.addWidget(self.stop_play_pushButton)

        self.volume_pushButton = QPushButton(self.widget_5)
        self.volume_pushButton.setObjectName(u"volume_pushButton")
        icon8 = QIcon()
        icon8.addFile(u":/pic/icons/sound_on.png", QSize(), QIcon.Normal, QIcon.Off)
        self.volume_pushButton.setIcon(icon8)

        self.horizontalLayout_2.addWidget(self.volume_pushButton)

        self.volume_Slider = QSlider(self.widget_5)
        self.volume_Slider.setObjectName(u"volume_Slider")
        self.volume_Slider.setMaximum(100)
        self.volume_Slider.setPageStep(10)
        self.volume_Slider.setOrientation(Qt.Horizontal)
        self.volume_Slider.setTickPosition(QSlider.NoTicks)

        self.horizontalLayout_2.addWidget(self.volume_Slider)

        self.horizontalSpacer_4 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_4)


        self.gridLayout_2.addWidget(self.widget_5, 1, 0, 1, 2)


        self.gridLayout.addWidget(self.widget_3, 2, 0, 1, 2)


        self.retranslateUi(App)

        QMetaObject.connectSlotsByName(App)
    # setupUi

    def retranslateUi(self, App):
        App.setWindowTitle(QCoreApplication.translate("App", u"music_player", None))
#if QT_CONFIG(tooltip)
        self.home_pushButton.setToolTip(QCoreApplication.translate("App", u"<b>\u8fd4\u56de\u4e3b\u9875</b>", None))
#endif // QT_CONFIG(tooltip)
        self.home_pushButton.setText("")
#if QT_CONFIG(tooltip)
        self.api_comboBox.setToolTip(QCoreApplication.translate("App", u"<b>\u9009\u62e9API</b>", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.search_pushButton.setToolTip(QCoreApplication.translate("App", u"<b>\u641c\u7d22<b/>", None))
#endif // QT_CONFIG(tooltip)
        self.search_pushButton.setText("")
#if QT_CONFIG(tooltip)
        self.login_pushButton.setToolTip(QCoreApplication.translate("App", u"<b>\u767b\u5f55\u5f53\u524dAPI</b>", None))
#endif // QT_CONFIG(tooltip)
        self.login_pushButton.setText("")
        self.progress_label.setText(QCoreApplication.translate("App", u"00 / 00", None))
#if QT_CONFIG(tooltip)
        self.previous_song_pushButton.setToolTip(QCoreApplication.translate("App", u"<b>\u4e0a\u4e00\u66f2</b>", None))
#endif // QT_CONFIG(tooltip)
        self.previous_song_pushButton.setText("")
#if QT_CONFIG(tooltip)
        self.toggle_play_state_pushButton.setToolTip(QCoreApplication.translate("App", u"<b>\u64ad\u653e<b/>", None))
#endif // QT_CONFIG(tooltip)
        self.toggle_play_state_pushButton.setText("")
#if QT_CONFIG(tooltip)
        self.next_song_pushButton.setToolTip(QCoreApplication.translate("App", u"<b>\u4e0b\u4e00\u66f2<b/>", None))
#endif // QT_CONFIG(tooltip)
        self.next_song_pushButton.setText("")
#if QT_CONFIG(tooltip)
        self.stop_play_pushButton.setToolTip(QCoreApplication.translate("App", u"<b>\u505c\u6b62</b>", None))
#endif // QT_CONFIG(tooltip)
        self.stop_play_pushButton.setText("")
#if QT_CONFIG(tooltip)
        self.volume_pushButton.setToolTip(QCoreApplication.translate("App", u"<b>\u97f3\u91cf</b>", None))
#endif // QT_CONFIG(tooltip)
        self.volume_pushButton.setText("")
    # retranslateUi

