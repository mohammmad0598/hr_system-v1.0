# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                           QLabel, QTableWidget, QTableWidgetItem, QFormLayout,
                           QLineEdit, QComboBox, QMessageBox)
from PyQt5.QtCore import Qt
from models.user import User
from models.employee import Employee
import logging

class UserManagementDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.user_manager = User()
        self.employee_manager = Employee()
        self.logger = logging.getLogger('UserManagement')
        self.setup_ui()
        
    def setup_ui(self):
        """تهيئة واجهة إدارة المستخدمين"""
        try:
            self.setWindowTitle("إدارة المستخدمين")
            self.setMinimumWidth(800)
            layout = QVBoxLayout()
            
            # أزرار التحكم
            buttons_layout = QHBoxLayout()
            add_button = QPushButton("إضافة مستخدم")
            delete_button = QPushButton("حذف مستخدم")
            change_password_button = QPushButton("تغيير كلمة المرور")
            
            add_button.clicked.connect(self.add_user)
            delete_button.clicked.connect(self.delete_user)
            change_password_button.clicked.connect(self.change_password)
            
            buttons_layout.addWidget(add_button)
            buttons_layout.addWidget(delete_button)
            buttons_layout.addWidget(change_password_button)
            buttons_layout.addStretch()
            
            # جدول المستخدمين
            self.users_table = QTableWidget()
            self.users_table.setColumnCount(5)
            self.users_table.setHorizontalHeaderLabels([
                "الرقم", "اسم المستخدم", "الصلاحية", "الموظف المرتبط", "الحالة"
            ])
            
            layout.addLayout(buttons_layout)
            layout.addWidget(self.users_table)
            
            self.setLayout(layout)
            self.refresh_table()
            
        except Exception as e:
            self.logger.error(f"خطأ في تهيئة واجهة إدارة المستخدمين: {str(e)}")
    
    def add_user(self):
        """إضافة مستخدم جديد"""
        try:
            dialog = QDialog(self)
            dialog.setWindowTitle("إضافة مستخدم جديد")
            layout = QFormLayout()
            
            username_input = QLineEdit()
            password_input = QLineEdit()
            password_input.setEchoMode(QLineEdit.Password)
            
            role_input = QComboBox()
            role_input.addItems(['admin', 'hr', 'manager', 'employee'])
            
            # قائمة الموظفين
            employee_input = QComboBox()
            employees = self.employee_manager.get_all_employees()
            employee_input.addItem("- بدون ربط -", None)
            for emp in employees:
                employee_input.addItem(f"{emp['name']} ({emp['id']})", emp['id'])
            
            layout.addRow("اسم المستخدم:", username_input)
            layout.addRow("كلمة المرور:", password_input)
            layout.addRow("الصلاحية:", role_input)
            layout.addRow("الموظف المرتبط:", employee_input)
            
            buttons = QHBoxLayout()
            save_btn = QPushButton("حفظ")
            cancel_btn = QPushButton("إلغاء")
            
            save_btn.clicked.connect(dialog.accept)
            cancel_btn.clicked.connect(dialog.reject)
            
            buttons.addWidget(save_btn)
            buttons.addWidget(cancel_btn)
            layout.addRow(buttons)
            
            dialog.setLayout(layout)
            
            if dialog.exec_() == QDialog.Accepted:
                if not username_input.text() or not password_input.text():
                    QMessageBox.warning(self, "تنبيه", "الرجاء إدخال اسم المستخدم وكلمة المرور")
                    return
                
                user_data = {
                    'username': username_input.text(),
                    'password': password_input.text(),
                    'role': role_input.currentText(),
                    'employee_id': employee_input.currentData()
                }
                
                if self.user_manager.add_user(user_data):
                    QMessageBox.information(self, "نجاح", "تم إضافة المستخدم بنجاح")
                    self.refresh_table()
                else:
                    QMessageBox.warning(self, "خطأ", "فشل في إضافة المستخدم")
                    
        except Exception as e:
            self.logger.error(f"خطأ في إضافة مستخدم: {str(e)}")
            QMessageBox.critical(self, "خطأ", "حدث خطأ في إضافة المستخدم")
    
    def delete_user(self):
        """حذف مستخدم"""
        try:
            current_row = self.users_table.currentRow()
            if current_row < 0:
                QMessageBox.warning(self, "تنبيه", "الرجاء اختيار مستخدم")
                return
            
            user_id = int(self.users_table.item(current_row, 0).text())
            username = self.users_table.item(current_row, 1).text()
            
            reply = QMessageBox.question(
                self, "تأكيد الحذف",
                f"هل أنت متأكد من حذف المستخدم {username}؟",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                if self.user_manager.delete_user(user_id):
                    QMessageBox.information(self, "نجاح", "تم حذف المستخدم بنجاح")
                    self.refresh_table()
                else:
                    QMessageBox.warning(self, "خطأ", "فشل في حذف المستخدم")
                    
        except Exception as e:
            self.logger.error(f"خطأ في حذف مستخدم: {str(e)}")
            QMessageBox.critical(self, "خطأ", "حدث خطأ في حذف المستخدم")
    
    def change_password(self):
        """تغيير كلمة المرور"""
        try:
            current_row = self.users_table.currentRow()
            if current_row < 0:
                QMessageBox.warning(self, "تنبيه", "الرجاء اختيار مستخدم")
                return
            
            user_id = int(self.users_table.item(current_row, 0).text())
            
            dialog = QDialog(self)
            dialog.setWindowTitle("تغيير كلمة المرور")
            layout = QFormLayout()
            
            new_password = QLineEdit()
            new_password.setEchoMode(QLineEdit.Password)
            confirm_password = QLineEdit()
            confirm_password.setEchoMode(QLineEdit.Password)
            
            layout.addRow("كلمة المرور الجديدة:", new_password)
            layout.addRow("تأكيد كلمة المرور:", confirm_password)
            
            buttons = QHBoxLayout()
            save_btn = QPushButton("حفظ")
            cancel_btn = QPushButton("إلغاء")
            
            save_btn.clicked.connect(dialog.accept)
            cancel_btn.clicked.connect(dialog.reject)
            
            buttons.addWidget(save_btn)
            buttons.addWidget(cancel_btn)
            layout.addRow(buttons)
            
            dialog.setLayout(layout)
            
            if dialog.exec_() == QDialog.Accepted:
                if new_password.text() != confirm_password.text():
                    QMessageBox.warning(self, "خطأ", "كلمتا المرور غير متطابقتين")
                    return
                
                if self.user_manager.update_password(user_id, new_password.text()):
                    QMessageBox.information(self, "نجاح", "تم تغيير كلمة المرور بنجاح")
                else:
                    QMessageBox.warning(self, "خطأ", "فشل في تغيير كلمة المرور")
                    
        except Exception as e:
            self.logger.error(f"خطأ في تغيير كلمة المرور: {str(e)}")
            QMessageBox.critical(self, "خطأ", "حدث خطأ في تغيير كلمة المرور")
    
    def refresh_table(self):
        """تحديث جدول المستخدمين"""
        try:
            users = self.user_manager.get_all_users()
            self.users_table.setRowCount(len(users))
            
            for row, user in enumerate(users):
                self.users_table.setItem(row, 0, QTableWidgetItem(str(user['id'])))
                self.users_table.setItem(row, 1, QTableWidgetItem(user['username']))
                self.users_table.setItem(row, 2, QTableWidgetItem(user['role']))
                self.users_table.setItem(row, 3, QTableWidgetItem(user['employee_name'] or '-'))
                self.users_table.setItem(row, 4, QTableWidgetItem('نشط'))
            
            self.users_table.resizeColumnsToContents()
                
        except Exception as e:
            self.logger.error(f"خطأ في تحديث جدول المستخدمين: {str(e)}") 