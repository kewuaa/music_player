# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'login.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QDialog, QDialogButtonBox,
    QFrame, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QSizePolicy, QTabWidget, QVBoxLayout,
    QWidget)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(400, 300)
        self.buttonBox = QDialogButtonBox(Dialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setGeometry(QRect(10, 240, 371, 32))
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)
        self.tabWidget = QTabWidget(Dialog)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabWidget.setEnabled(True)
        self.tabWidget.setGeometry(QRect(10, 19, 371, 211))
        self.tabWidget.setTabShape(QTabWidget.Rounded)
        self.QR_tab = QWidget()
        self.QR_tab.setObjectName(u"QR_tab")
        self.QR_label = QLabel(self.QR_tab)
        self.QR_label.setObjectName(u"QR_label")
        self.QR_label.setGeometry(QRect(90, 10, 191, 171))
        self.QR_label.setFrameShape(QFrame.WinPanel)
        self.QR_label.setFrameShadow(QFrame.Plain)
        self.tabWidget.addTab(self.QR_tab, "")
        self.SMS_tab = QWidget()
        self.SMS_tab.setObjectName(u"SMS_tab")
        self.verticalLayoutWidget = QWidget(self.SMS_tab)
        self.verticalLayoutWidget.setObjectName(u"verticalLayoutWidget")
        self.verticalLayoutWidget.setGeometry(QRect(-1, -1, 371, 191))
        self.verticalLayout_2 = QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.frame = QFrame(self.verticalLayoutWidget)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_3 = QHBoxLayout(self.frame)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.label = QLabel(self.frame)
        self.label.setObjectName(u"label")

        self.horizontalLayout_3.addWidget(self.label)

        self.cellphone_lineEdit = QLineEdit(self.frame)
        self.cellphone_lineEdit.setObjectName(u"cellphone_lineEdit")

        self.horizontalLayout_3.addWidget(self.cellphone_lineEdit)


        self.verticalLayout_2.addWidget(self.frame)

        self.sms_captcha_frame = QFrame(self.verticalLayoutWidget)
        self.sms_captcha_frame.setObjectName(u"sms_captcha_frame")
        self.sms_captcha_frame.setEnabled(True)
        self.sms_captcha_frame.setFrameShape(QFrame.StyledPanel)
        self.sms_captcha_frame.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_4 = QHBoxLayout(self.sms_captcha_frame)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.label_2 = QLabel(self.sms_captcha_frame)
        self.label_2.setObjectName(u"label_2")

        self.horizontalLayout_4.addWidget(self.label_2)

        self.sms_captcha_lineEdit = QLineEdit(self.sms_captcha_frame)
        self.sms_captcha_lineEdit.setObjectName(u"sms_captcha_lineEdit")

        self.horizontalLayout_4.addWidget(self.sms_captcha_lineEdit)

        self.sms_captcha_label = QLabel(self.sms_captcha_frame)
        self.sms_captcha_label.setObjectName(u"sms_captcha_label")
        self.sms_captcha_label.setMinimumSize(QSize(100, 0))
        self.sms_captcha_label.setAlignment(Qt.AlignCenter)

        self.horizontalLayout_4.addWidget(self.sms_captcha_label)

        self.refresh_sms_captcha_pushButton = QPushButton(self.sms_captcha_frame)
        self.refresh_sms_captcha_pushButton.setObjectName(u"refresh_sms_captcha_pushButton")

        self.horizontalLayout_4.addWidget(self.refresh_sms_captcha_pushButton)


        self.verticalLayout_2.addWidget(self.sms_captcha_frame)

        self.frame_2 = QFrame(self.verticalLayoutWidget)
        self.frame_2.setObjectName(u"frame_2")
        self.frame_2.setFrameShape(QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_5 = QHBoxLayout(self.frame_2)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.label_3 = QLabel(self.frame_2)
        self.label_3.setObjectName(u"label_3")

        self.horizontalLayout_5.addWidget(self.label_3)

        self.verify_code_lineEdit = QLineEdit(self.frame_2)
        self.verify_code_lineEdit.setObjectName(u"verify_code_lineEdit")

        self.horizontalLayout_5.addWidget(self.verify_code_lineEdit)

        self.send_sms_pushButton = QPushButton(self.frame_2)
        self.send_sms_pushButton.setObjectName(u"send_sms_pushButton")

        self.horizontalLayout_5.addWidget(self.send_sms_pushButton)


        self.verticalLayout_2.addWidget(self.frame_2)

        self.tabWidget.addTab(self.SMS_tab, "")
        self.PWD_tab = QWidget()
        self.PWD_tab.setObjectName(u"PWD_tab")
        self.verticalLayoutWidget_2 = QWidget(self.PWD_tab)
        self.verticalLayoutWidget_2.setObjectName(u"verticalLayoutWidget_2")
        self.verticalLayoutWidget_2.setGeometry(QRect(-1, -1, 371, 191))
        self.verticalLayout_3 = QVBoxLayout(self.verticalLayoutWidget_2)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.frame_4 = QFrame(self.verticalLayoutWidget_2)
        self.frame_4.setObjectName(u"frame_4")
        self.frame_4.setFrameShape(QFrame.StyledPanel)
        self.frame_4.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_6 = QHBoxLayout(self.frame_4)
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.label_4 = QLabel(self.frame_4)
        self.label_4.setObjectName(u"label_4")

        self.horizontalLayout_6.addWidget(self.label_4)

        self.login_id_lineEdit = QLineEdit(self.frame_4)
        self.login_id_lineEdit.setObjectName(u"login_id_lineEdit")

        self.horizontalLayout_6.addWidget(self.login_id_lineEdit)


        self.verticalLayout_3.addWidget(self.frame_4)

        self.pwd_captcha_frame = QFrame(self.verticalLayoutWidget_2)
        self.pwd_captcha_frame.setObjectName(u"pwd_captcha_frame")
        self.pwd_captcha_frame.setFrameShape(QFrame.StyledPanel)
        self.pwd_captcha_frame.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_7 = QHBoxLayout(self.pwd_captcha_frame)
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.label_5 = QLabel(self.pwd_captcha_frame)
        self.label_5.setObjectName(u"label_5")

        self.horizontalLayout_7.addWidget(self.label_5)

        self.pwd_captcha_lineEdit = QLineEdit(self.pwd_captcha_frame)
        self.pwd_captcha_lineEdit.setObjectName(u"pwd_captcha_lineEdit")

        self.horizontalLayout_7.addWidget(self.pwd_captcha_lineEdit)

        self.pwd_captcha_label = QLabel(self.pwd_captcha_frame)
        self.pwd_captcha_label.setObjectName(u"pwd_captcha_label")
        self.pwd_captcha_label.setMinimumSize(QSize(100, 0))
        self.pwd_captcha_label.setAlignment(Qt.AlignCenter)

        self.horizontalLayout_7.addWidget(self.pwd_captcha_label)

        self.refresh_pwd_captcha_pushButton = QPushButton(self.pwd_captcha_frame)
        self.refresh_pwd_captcha_pushButton.setObjectName(u"refresh_pwd_captcha_pushButton")

        self.horizontalLayout_7.addWidget(self.refresh_pwd_captcha_pushButton)


        self.verticalLayout_3.addWidget(self.pwd_captcha_frame)

        self.frame_5 = QFrame(self.verticalLayoutWidget_2)
        self.frame_5.setObjectName(u"frame_5")
        self.frame_5.setFrameShape(QFrame.StyledPanel)
        self.frame_5.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_8 = QHBoxLayout(self.frame_5)
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.label_7 = QLabel(self.frame_5)
        self.label_7.setObjectName(u"label_7")

        self.horizontalLayout_8.addWidget(self.label_7)

        self.password_lineEdit = QLineEdit(self.frame_5)
        self.password_lineEdit.setObjectName(u"password_lineEdit")

        self.horizontalLayout_8.addWidget(self.password_lineEdit)


        self.verticalLayout_3.addWidget(self.frame_5)

        self.tabWidget.addTab(self.PWD_tab, "")

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Dialog", None))
        self.QR_label.setText("")
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.QR_tab), QCoreApplication.translate("Dialog", u"\u626b\u7801\u767b\u5f55", None))
        self.label.setText(QCoreApplication.translate("Dialog", u" \u7535\u8bdd\u53f7\u7801  ", None))
        self.label_2.setText(QCoreApplication.translate("Dialog", u"\u56fe\u5f62\u9a8c\u8bc1\u7801", None))
        self.sms_captcha_label.setText(QCoreApplication.translate("Dialog", u"----------", None))
        self.refresh_sms_captcha_pushButton.setText(QCoreApplication.translate("Dialog", u"\u5237\u65b0", None))
        self.label_3.setText(QCoreApplication.translate("Dialog", u"\u77ed\u4fe1\u9a8c\u8bc1\u7801", None))
        self.send_sms_pushButton.setText(QCoreApplication.translate("Dialog", u"\u53d1\u9001\u77ed\u4fe1", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.SMS_tab), QCoreApplication.translate("Dialog", u"\u77ed\u4fe1\u767b\u5f55", None))
        self.label_4.setText(QCoreApplication.translate("Dialog", u"     \u8d26\u53f7     ", None))
        self.label_5.setText(QCoreApplication.translate("Dialog", u"\u56fe\u5f62\u9a8c\u8bc1\u7801", None))
        self.pwd_captcha_label.setText(QCoreApplication.translate("Dialog", u"----------", None))
        self.refresh_pwd_captcha_pushButton.setText(QCoreApplication.translate("Dialog", u"\u5237\u65b0", None))
        self.label_7.setText(QCoreApplication.translate("Dialog", u"     \u5bc6\u7801     ", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.PWD_tab), QCoreApplication.translate("Dialog", u"\u8d26\u53f7\u5bc6\u7801\u767b\u5f55", None))
    # retranslateUi

