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
from PySide6.QtWidgets import (QApplication, QComboBox, QGridLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QSizePolicy,
    QSlider, QSpacerItem, QVBoxLayout, QWidget)
from . import icons_rc

class Ui_App(object):
    def setupUi(self, App):
        if not App.objectName():
            App.setObjectName(u"App")
        App.resize(655, 538)
        icon = QIcon()
        icon.addFile(u":/pic/icons/title.png", QSize(), QIcon.Normal, QIcon.Off)
        App.setWindowIcon(icon)
        self.gridLayout = QGridLayout(App)
        self.gridLayout.setObjectName(u"gridLayout")
        self.main_widget = QWidget(App)
        self.main_widget.setObjectName(u"main_widget")
        self.main_widget.setMinimumSize(QSize(511, 341))

        self.gridLayout.addWidget(self.main_widget, 1, 1, 1, 1)

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
        icon1 = QIcon()
        icon1.addFile(u":/pic/icons/previous.png", QSize(), QIcon.Normal, QIcon.Off)
        self.previous_song_pushButton.setIcon(icon1)

        self.horizontalLayout_2.addWidget(self.previous_song_pushButton)

        self.toggle_play_state_pushButton = QPushButton(self.widget_5)
        self.toggle_play_state_pushButton.setObjectName(u"toggle_play_state_pushButton")
        icon2 = QIcon()
        icon2.addFile(u":/pic/icons/play.png", QSize(), QIcon.Normal, QIcon.Off)
        self.toggle_play_state_pushButton.setIcon(icon2)

        self.horizontalLayout_2.addWidget(self.toggle_play_state_pushButton)

        self.next_song_pushButton = QPushButton(self.widget_5)
        self.next_song_pushButton.setObjectName(u"next_song_pushButton")
        icon3 = QIcon()
        icon3.addFile(u":/pic/icons/next.png", QSize(), QIcon.Normal, QIcon.Off)
        self.next_song_pushButton.setIcon(icon3)

        self.horizontalLayout_2.addWidget(self.next_song_pushButton)

        self.stop_play_pushButton = QPushButton(self.widget_5)
        self.stop_play_pushButton.setObjectName(u"stop_play_pushButton")
        icon4 = QIcon()
        icon4.addFile(u":/pic/icons/stop.png", QSize(), QIcon.Normal, QIcon.Off)
        self.stop_play_pushButton.setIcon(icon4)

        self.horizontalLayout_2.addWidget(self.stop_play_pushButton)

        self.play_mode_comboBox = QComboBox(self.widget_5)
        icon5 = QIcon()
        icon5.addFile(u":/pic/icons/single_play.png", QSize(), QIcon.Normal, QIcon.Off)
        self.play_mode_comboBox.addItem(icon5, "")
        icon6 = QIcon()
        icon6.addFile(u":/pic/icons/loop_play.png", QSize(), QIcon.Normal, QIcon.Off)
        self.play_mode_comboBox.addItem(icon6, "")
        icon7 = QIcon()
        icon7.addFile(u":/pic/icons/random_play.png", QSize(), QIcon.Normal, QIcon.Off)
        self.play_mode_comboBox.addItem(icon7, "")
        self.play_mode_comboBox.setObjectName(u"play_mode_comboBox")
        self.play_mode_comboBox.setEditable(False)
        self.play_mode_comboBox.setSizeAdjustPolicy(QComboBox.AdjustToContentsOnFirstShow)
        self.play_mode_comboBox.setIconSize(QSize(13, 13))
        self.play_mode_comboBox.setDuplicatesEnabled(False)

        self.horizontalLayout_2.addWidget(self.play_mode_comboBox)

        self.playback_rate_comboBox = QComboBox(self.widget_5)
        self.playback_rate_comboBox.addItem("")
        self.playback_rate_comboBox.addItem("")
        self.playback_rate_comboBox.addItem("")
        self.playback_rate_comboBox.addItem("")
        self.playback_rate_comboBox.addItem("")
        self.playback_rate_comboBox.addItem("")
        self.playback_rate_comboBox.addItem("")
        self.playback_rate_comboBox.addItem("")
        self.playback_rate_comboBox.addItem("")
        self.playback_rate_comboBox.setObjectName(u"playback_rate_comboBox")

        self.horizontalLayout_2.addWidget(self.playback_rate_comboBox)

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

        self.widget = QWidget(App)
        self.widget.setObjectName(u"widget")
        self.widget.setMinimumSize(QSize(637, 61))
        self.horizontalLayout = QHBoxLayout(self.widget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.home_pushButton = QPushButton(self.widget)
        self.home_pushButton.setObjectName(u"home_pushButton")
        icon9 = QIcon()
        icon9.addFile(u":/pic/icons/home.png", QSize(), QIcon.Normal, QIcon.Off)
        self.home_pushButton.setIcon(icon9)

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
        icon10 = QIcon()
        icon10.addFile(u":/pic/icons/search.png", QSize(), QIcon.Normal, QIcon.Off)
        self.search_pushButton.setIcon(icon10)

        self.horizontalLayout.addWidget(self.search_pushButton)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_2)

        self.login_pushButton = QPushButton(self.widget)
        self.login_pushButton.setObjectName(u"login_pushButton")
        icon11 = QIcon()
        icon11.addFile(u":/pic/icons/login.png", QSize(), QIcon.Normal, QIcon.Off)
        self.login_pushButton.setIcon(icon11)

        self.horizontalLayout.addWidget(self.login_pushButton)


        self.gridLayout.addWidget(self.widget, 0, 0, 1, 2)

        self.widget_2 = QWidget(App)
        self.widget_2.setObjectName(u"widget_2")
        self.widget_2.setMinimumSize(QSize(120, 341))
        self.verticalLayout = QVBoxLayout(self.widget_2)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.switch_to_search_page_pushButton = QPushButton(self.widget_2)
        self.switch_to_search_page_pushButton.setObjectName(u"switch_to_search_page_pushButton")

        self.verticalLayout.addWidget(self.switch_to_search_page_pushButton)

        self.switch_to_list_page_pushButton = QPushButton(self.widget_2)
        self.switch_to_list_page_pushButton.setObjectName(u"switch_to_list_page_pushButton")

        self.verticalLayout.addWidget(self.switch_to_list_page_pushButton)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)


        self.gridLayout.addWidget(self.widget_2, 1, 0, 1, 1)


        self.retranslateUi(App)

        self.playback_rate_comboBox.setCurrentIndex(2)


        QMetaObject.connectSlotsByName(App)
    # setupUi

    def retranslateUi(self, App):
        App.setWindowTitle(QCoreApplication.translate("App", u"music_player", None))
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
        self.play_mode_comboBox.setItemText(0, QCoreApplication.translate("App", u"\u5355\u66f2", None))
        self.play_mode_comboBox.setItemText(1, QCoreApplication.translate("App", u"\u987a\u5e8f", None))
        self.play_mode_comboBox.setItemText(2, QCoreApplication.translate("App", u"\u968f\u673a", None))

#if QT_CONFIG(tooltip)
        self.play_mode_comboBox.setToolTip(QCoreApplication.translate("App", u"<b>\u64ad\u653e\u6a21\u5f0f</b>", None))
#endif // QT_CONFIG(tooltip)
        self.playback_rate_comboBox.setItemText(0, QCoreApplication.translate("App", u"0.5", None))
        self.playback_rate_comboBox.setItemText(1, QCoreApplication.translate("App", u"0.75", None))
        self.playback_rate_comboBox.setItemText(2, QCoreApplication.translate("App", u"1.0", None))
        self.playback_rate_comboBox.setItemText(3, QCoreApplication.translate("App", u"1.25", None))
        self.playback_rate_comboBox.setItemText(4, QCoreApplication.translate("App", u"1.5", None))
        self.playback_rate_comboBox.setItemText(5, QCoreApplication.translate("App", u"1.75", None))
        self.playback_rate_comboBox.setItemText(6, QCoreApplication.translate("App", u"2.0", None))
        self.playback_rate_comboBox.setItemText(7, QCoreApplication.translate("App", u"2.5", None))
        self.playback_rate_comboBox.setItemText(8, QCoreApplication.translate("App", u"3.0", None))

#if QT_CONFIG(tooltip)
        self.playback_rate_comboBox.setToolTip(QCoreApplication.translate("App", u"<b>\u64ad\u653e\u901f\u7387</b>", None))
#endif // QT_CONFIG(tooltip)
        self.playback_rate_comboBox.setCurrentText(QCoreApplication.translate("App", u"1.0", None))
#if QT_CONFIG(tooltip)
        self.volume_pushButton.setToolTip(QCoreApplication.translate("App", u"<b>\u97f3\u91cf</b>", None))
#endif // QT_CONFIG(tooltip)
        self.volume_pushButton.setText("")
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
        self.switch_to_search_page_pushButton.setText(QCoreApplication.translate("App", u"\u641c\u7d22\u9875", None))
        self.switch_to_list_page_pushButton.setText(QCoreApplication.translate("App", u"\u64ad\u653e\u5217\u8868", None))
    # retranslateUi

