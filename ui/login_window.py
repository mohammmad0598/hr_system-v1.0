# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, 
                           QLineEdit, QPushButton, QMessageBox)
from PyQt5.QtCore import pyqtSignal, Qt
from models.user import User
import logging

class LoginWindow(QWidget):
    # إشارة نجاح تسجيل الدخول
    login_success = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.user_manager = User()
        self.logger = logging.getLogger('LoginWindow')
        self.setup_ui()
        
    def setup_ui(self):
        """تهيئة واجهة تسجيل الدخول"""
        try:
            self.setWindowTitle("تسجيل الدخول")
            self.setGeometry(450, 250, 400, 200)
            self.setWindowFlags(Qt.WindowStaysOnTopHint)
            
            layout = QVBoxLayout()
            layout.setContentsMargins(50, 20, 50, 20)
            
            # عنوان النافذة
            title_label = QLabel("نظام إدارة الموارد البشرية")
            title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
            title_label.setAlignment(Qt.AlignCenter)
            
            # حقول الإدخال
            self.username_input = QLineEdit()
            self.username_input.setPlaceholderText("اسم المستخدم")
            self.username_input.setStyleSheet("padding: 5px;")
            
            self.password_input = QLineEdit()
            self.password_input.setPlaceholderText("كلمة المرور")
            self.password_input.setEchoMode(QLineEdit.Password)
            self.password_input.setStyleSheet("padding: 5px;")
            
            # زر تسجيل الدخول
            self.login_button = QPushButton("تسجيل الدخول")
            self.login_button.setStyleSheet("""
                QPushButton {
                    background-color: #2ecc71;
                    color: white;
                    padding: 8px;
                    border: none;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #27ae60;
                }
            """)
            self.login_button.clicked.connect(self.handle_login)
            
            # إضافة العناصر للتخطيط
            layout.addWidget(title_label)
            layout.addSpacing(20)
            layout.addWidget(QLabel("اسم المستخدم:"))
            layout.addWidget(self.username_input)
            layout.addSpacing(10)
            layout.addWidget(QLabel("كلمة المرور:"))
            layout.addWidget(self.password_input)
            layout.addSpacing(20)
            layout.addWidget(self.login_button)
            
            self.setLayout(layout)
            
            # ربط مفتاح Enter بزر تسجيل الدخول
            self.password_input.returnPressed.connect(self.login_button.click)
            
        except Exception as e:
            self.logger.error(f"خطأ في تهيئة واجهة تسجيل الدخول: {str(e)}")
    
    def handle_login(self):
        """معالجة تسجيل الدخول"""
        try:
            username = self.username_input.text().strip()
            password = self.password_input.text().strip()
            
            if not username or not password:
                QMessageBox.warning(
                    self,
                    "تنبيه",
                    "الرجاء إدخال اسم المستخدم وكلمة المرور"
                )
                return
            
            if self.user_manager.verify_login(username, password):
                user_data = self.user_manager.get_user_data(username)
                if user_data:
                    self.login_success.emit(user_data)
                    self.logger.info(f"تم تسجيل دخول المستخدم: {username}")
                else:
                    QMessageBox.critical(
                        self,
                        "خطأ",
                        "حدث خطأ في جلب بيانات المستخدم"
                    )
            else:
                QMessageBox.warning(
                    self,
                    "خطأ",
                    "اسم المستخدم أو كلمة المرور غير صحيحة"
                )
                self.password_input.clear()
                self.password_input.setFocus()
                
        except Exception as e:
            self.logger.error(f"خطأ في معالجة تسجيل الدخول: {str(e)}")
            QMessageBox.critical(
                self,
                "خطأ",
                "حدث خطأ في عملية تسجيل الدخول"
            )