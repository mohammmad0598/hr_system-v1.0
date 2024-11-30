# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                           QLabel, QTableWidget, QTableWidgetItem, QComboBox,
                           QMessageBox)
from PyQt5.QtCore import Qt
from models.salary import SalaryManager
import logging

class SalaryView(QWidget):
    def __init__(self):
        super().__init__()
        self.salary_manager = SalaryManager()
        self.logger = logging.getLogger('SalaryView')
        self.setup_ui()
    
    def setup_ui(self):
        """تهيئة واجهة الرواتب"""
        layout = QVBoxLayout()
        
        # تخطيط الفلترة
        filter_layout = QHBoxLayout()
        self.month_combo = QComboBox()
        self.month_combo.addItems([str(i) for i in range(1, 13)])
        self.year_combo = QComboBox()
        self.year_combo.addItems(['2023', '2024', '2025'])
        self.department_combo = QComboBox()
        
        filter_layout.addWidget(QLabel("الشهر:"))
        filter_layout.addWidget(self.month_combo)
        filter_layout.addWidget(QLabel("السنة:"))
        filter_layout.addWidget(self.year_combo)
        filter_layout.addWidget(QLabel("القسم:"))
        filter_layout.addWidget(self.department_combo)
        filter_layout.addStretch()
        
        # أزرار التحكم
        buttons_layout = QHBoxLayout()
        self.calculate_button = QPushButton("احتساب الرواتب")
        self.approve_button = QPushButton("اعتماد")
        self.export_button = QPushButton("تصدير")
        
        self.calculate_button.clicked.connect(self.calculate_salaries)
        self.approve_button.clicked.connect(self.approve_salaries)
        self.export_button.clicked.connect(self.export_report)
        
        buttons_layout.addWidget(self.calculate_button)
        buttons_layout.addWidget(self.approve_button)
        buttons_layout.addWidget(self.export_button)
        
        # جدول الرواتب
        self.salary_table = QTableWidget()
        self.salary_table.setColumnCount(8)
        self.salary_table.setHorizontalHeaderLabels([
            "الرقم", "اسم الموظف", "الراتب الأساسي", "البدلات",
            "الخصومات", "صافي الراتب", "تاريخ الصرف", "الحالة"
        ])
        
        layout.addLayout(filter_layout)
        layout.addLayout(buttons_layout)
        layout.addWidget(self.salary_table)
        self.setLayout(layout)
        
        # تحديث القائمة المنسدلة للأقسام
        self.load_departments()
    
    def load_departments(self):
        """تحميل قائمة الأقسام"""
        try:
            departments = self.salary_manager.get_departments()
            self.department_combo.clear()
            self.department_combo.addItems(['الكل'] + departments)
        except Exception as e:
            self.logger.error(f"خطأ في تحميل الأقسام: {str(e)}")
    
    def calculate_salaries(self):
        """احتساب الرواتب"""
        try:
            month = int(self.month_combo.currentText())
            year = int(self.year_combo.currentText())
            department = self.department_combo.currentText()
            
            if department == 'الكل':
                department = None
                
            salaries = self.salary_manager.calculate_monthly_salaries(
                month=month,
                year=year,
                department=department
            )
            
            self.salary_table.setRowCount(len(salaries))
            for row, salary in enumerate(salaries):
                self.salary_table.setItem(row, 0, QTableWidgetItem(str(salary['employee_id'])))
                self.salary_table.setItem(row, 1, QTableWidgetItem(salary['name']))
                self.salary_table.setItem(row, 2, QTableWidgetItem(f"{salary['basic_salary']:.2f}"))
                self.salary_table.setItem(row, 3, QTableWidgetItem(f"{salary['allowances']:.2f}"))
                self.salary_table.setItem(row, 4, QTableWidgetItem(f"{salary['deductions']:.2f}"))
                self.salary_table.setItem(row, 5, QTableWidgetItem(f"{salary['net_salary']:.2f}"))
                self.salary_table.setItem(row, 6, QTableWidgetItem(str(salary['date'])))
                self.salary_table.setItem(row, 7, QTableWidgetItem(salary['status']))
                
        except Exception as e:
            self.logger.error(f"خطأ في احتساب الرواتب: {str(e)}")
            QMessageBox.critical(self, "خطأ", "حدث خطأ في احتساب الرواتب")
    
    def approve_salaries(self):
        """اعتماد الرواتب"""
        try:
            reply = QMessageBox.question(
                self, "تأكيد",
                "هل أنت متأكد من اعتماد الرواتب؟",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                month = int(self.month_combo.currentText())
                year = int(self.year_combo.currentText())
                
                if self.salary_manager.approve_salaries(month, year):
                    QMessageBox.information(self, "نجاح", "تم اعتماد الرواتب بنجاح")
                    self.calculate_salaries()  # تحديث الجدول
                else:
                    QMessageBox.warning(self, "خطأ", "فشل في اعتماد الرواتب")
                    
        except Exception as e:
            self.logger.error(f"خطأ في اعتماد الرواتب: {str(e)}")
            QMessageBox.critical(self, "خطأ", "حدث خطأ في اعتماد الرواتب")
    
    def export_report(self):
        """تصدير تقرير الرواتب"""
        try:
            month = int(self.month_combo.currentText())
            year = int(self.year_combo.currentText())
            
            if self.salary_manager.export_salary_report(month, year):
                QMessageBox.information(self, "نجاح", "تم تصدير التقرير بنجاح")
            else:
                QMessageBox.warning(self, "خطأ", "فشل في تصدير التقرير")
                
        except Exception as e:
            self.logger.error(f"خطأ في تصدير التقرير: {str(e)}")
            QMessageBox.critical(self, "خطأ", "حدث خطأ في تصدير التقرير")