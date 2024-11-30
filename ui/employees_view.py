# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                           QLabel, QTableWidget, QTableWidgetItem, QDialog, QFormLayout,
                           QLineEdit, QDialogButtonBox, QMessageBox)
from PyQt5.QtCore import Qt, QDate
from models.employee import Employee
import logging

class EmployeesView(QWidget):
    def __init__(self):
        super().__init__()
        self.employee_manager = Employee()
        self.logger = logging.getLogger('EmployeesView')
        self.setup_ui()
    
    def setup_ui(self):
        """تهيئة واجهة الموظفين"""
        layout = QVBoxLayout()
        
        # أزرار التحكم
        buttons_layout = QHBoxLayout()
        self.add_button = QPushButton("إضافة موظف")
        self.edit_button = QPushButton("تعديل")
        self.delete_button = QPushButton("حذف")
        
        # ربط الأزرار بالوظائف
        self.add_button.clicked.connect(self.add_employee)
        self.edit_button.clicked.connect(self.edit_employee)
        self.delete_button.clicked.connect(self.delete_employee)
        
        buttons_layout.addWidget(self.add_button)
        buttons_layout.addWidget(self.edit_button)
        buttons_layout.addWidget(self.delete_button)
        
        # جدول الموظفين
        self.employees_table = QTableWidget()
        self.employees_table.setColumnCount(6)
        self.employees_table.setHorizontalHeaderLabels([
            "الرقم", "الاسم", "القسم", "المنصب", 
            "تاريخ التعيين", "الراتب"
        ])
        
        layout.addLayout(buttons_layout)
        layout.addWidget(self.employees_table)
        self.setLayout(layout)
        
        # تحديث الجدول عند البداية
        self.refresh_table()

    def add_employee(self):
        """إضافة موظف جديد"""
        try:
            dialog = QDialog(self)
            dialog.setWindowTitle("إضافة موظف جديد")
            layout = QFormLayout()
            
            # حقول الإدخال
            name_input = QLineEdit()
            department_input = QLineEdit()
            position_input = QLineEdit()
            salary_input = QLineEdit()
            phone_input = QLineEdit()
            email_input = QLineEdit()
            
            layout.addRow("الاسم:", name_input)
            layout.addRow("القسم:", department_input)
            layout.addRow("المنصب:", position_input)
            layout.addRow("الراتب:", salary_input)
            layout.addRow("رقم الجوال:", phone_input)
            layout.addRow("البريد الإلكتروني:", email_input)
            
            # أزرار الحوار
            buttons = QDialogButtonBox(
                QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
                Qt.Horizontal
            )
            buttons.accepted.connect(dialog.accept)
            buttons.rejected.connect(dialog.reject)
            layout.addRow(buttons)
            
            dialog.setLayout(layout)
            
            if dialog.exec_() == QDialog.Accepted:
                # التحقق من الحقول المطلوبة
                if not name_input.text().strip():
                    QMessageBox.warning(self, "تنبيه", "الرجاء إدخال اسم الموظف")
                    return
                
                try:
                    salary = float(salary_input.text() or 0)
                except ValueError:
                    QMessageBox.warning(self, "تنبيه", "الرجاء إدخال راتب صحيح")
                    return
                
                # تجهيز بيانات الموظف
                employee_data = {
                    'name': name_input.text().strip(),
                    'department': department_input.text().strip(),
                    'position': position_input.text().strip(),
                    'salary': salary,
                    'phone': phone_input.text().strip(),
                    'email': email_input.text().strip(),
                    'join_date': QDate.currentDate().toPyDate()
                }
                
                # إضافة الموظف
                if self.employee_manager.add_employee(employee_data):
                    QMessageBox.information(self, "نجاح", "تم إضافة الموظف بنجاح")
                    self.refresh_table()
                else:
                    QMessageBox.warning(self, "خطأ", "فشل في إضافة الموظف")
                    
        except Exception as e:
            self.logger.error(f"خطأ في إضافة موظف: {str(e)}")
            QMessageBox.critical(self, "خطأ", "حدث خطأ في إضافة الموظف")

    def edit_employee(self):
        """تعديل بيانات الموظف"""
        try:
            current_row = self.employees_table.currentRow()
            if current_row < 0:
                QMessageBox.warning(self, "تنبيه", "الرجاء اختيار موظف أولاً")
                return
            
            employee_id = int(self.employees_table.item(current_row, 0).text())
            
            dialog = QDialog(self)
            dialog.setWindowTitle("تعديل بيانات الموظف")
            layout = QFormLayout()
            
            # حقول الإدخال مع البيانات الحالية
            name_input = QLineEdit(self.employees_table.item(current_row, 1).text())
            department_input = QLineEdit(self.employees_table.item(current_row, 2).text())
            position_input = QLineEdit(self.employees_table.item(current_row, 3).text())
            salary_input = QLineEdit(self.employees_table.item(current_row, 5).text())
            
            layout.addRow("الاسم:", name_input)
            layout.addRow("القسم:", department_input)
            layout.addRow("المنصب:", position_input)
            layout.addRow("الراتب:", salary_input)
            
            buttons = QDialogButtonBox(
                QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
                Qt.Horizontal
            )
            buttons.accepted.connect(dialog.accept)
            buttons.rejected.connect(dialog.reject)
            layout.addRow(buttons)
            
            dialog.setLayout(layout)
            
            if dialog.exec_() == QDialog.Accepted:
                employee_data = {
                    'id': employee_id,
                    'name': name_input.text(),
                    'department': department_input.text(),
                    'position': position_input.text(),
                    'salary': float(salary_input.text() or 0)
                }
                
                if self.employee_manager.update_employee(employee_data):
                    QMessageBox.information(self, "نجاح", "تم تحديث بيانات الموظف بنجاح")
                    self.refresh_table()
                else:
                    QMessageBox.warning(self, "خطأ", "فشل في تحديث بيانات الموظف")
                    
        except Exception as e:
            self.logger.error(f"خطأ في تعديل بيانات الموظف: {str(e)}")
            QMessageBox.critical(self, "خطأ", "حدث خطأ في تعديل بيانات الموظف")

    def delete_employee(self):
        """حذف موظف"""
        try:
            current_row = self.employees_table.currentRow()
            if current_row < 0:
                QMessageBox.warning(self, "تنبيه", "الرجاء اختيار موظف أولاً")
                return
            
            employee_id = int(self.employees_table.item(current_row, 0).text())
            employee_name = self.employees_table.item(current_row, 1).text()
            
            reply = QMessageBox.question(
                self, "تأكيد الحذف",
                f"هل أنت متأكد من حذف الموظف {employee_name}؟",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                if self.employee_manager.delete_employee(employee_id):
                    QMessageBox.information(self, "نجاح", "تم حذف الموظف بنجاح")
                    self.refresh_table()
                else:
                    QMessageBox.warning(self, "خطأ", "فشل في حذف الموظف")
                    
        except Exception as e:
            self.logger.error(f"خطأ في حذف الموظف: {str(e)}")
            QMessageBox.critical(self, "خطأ", "حدث خطأ في حذف الموظف")

    def refresh_table(self):
        """تحديث جدول الموظفين"""
        try:
            employees = self.employee_manager.get_all_employees()
            self.employees_table.setRowCount(len(employees))
            
            for row, emp in enumerate(employees):
                self.employees_table.setItem(row, 0, QTableWidgetItem(str(emp['id'])))
                self.employees_table.setItem(row, 1, QTableWidgetItem(emp['name']))
                self.employees_table.setItem(row, 2, QTableWidgetItem(emp['department']))
                self.employees_table.setItem(row, 3, QTableWidgetItem(emp['position']))
                self.employees_table.setItem(row, 4, QTableWidgetItem(str(emp['join_date'])))
                self.employees_table.setItem(row, 5, QTableWidgetItem(str(emp['salary'])))
                
        except Exception as e:
            self.logger.error(f"خطأ في تحديث جدول الموظفين: {str(e)}")
            QMessageBox.critical(self, "خطأ", "حدث خطأ في تحديث جدول الموظفين")