# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                           QLabel, QTableWidget, QTableWidgetItem, QDateEdit,
                           QInputDialog, QMessageBox)
from PyQt5.QtCore import Qt, QDate
from models.attendance import Attendance
import logging

class AttendanceView(QWidget):
    def __init__(self):
        super().__init__()
        self.attendance_manager = Attendance()
        self.logger = logging.getLogger('AttendanceView')
        self.setup_ui()
        
    def setup_ui(self):
        """تهيئة واجهة الحضور والانصراف"""
        try:
            layout = QVBoxLayout()

            # تخطيط التاريخ
            date_layout = QHBoxLayout()
            self.date_input = QDateEdit()
            self.date_input.setDate(QDate.currentDate())
            self.date_input.dateChanged.connect(self.update_attendance_table)
            date_layout.addWidget(QLabel("التاريخ:"))
            date_layout.addWidget(self.date_input)
            date_layout.addStretch()

            # أزرار التحكم
            buttons_layout = QHBoxLayout()
            self.check_in_button = QPushButton("تسجيل حضور")
            self.check_out_button = QPushButton("تسجيل انصراف")
            self.refresh_button = QPushButton("تحديث")
            
            self.check_in_button.clicked.connect(lambda: self.record_attendance('حضور'))
            self.check_out_button.clicked.connect(lambda: self.record_attendance('انصراف'))
            self.refresh_button.clicked.connect(self.update_attendance_table)
            
            buttons_layout.addWidget(self.check_in_button)
            buttons_layout.addWidget(self.check_out_button)
            buttons_layout.addWidget(self.refresh_button)

            # جدول الحضور
            self.attendance_table = QTableWidget()
            self.attendance_table.setColumnCount(7)
            self.attendance_table.setHorizontalHeaderLabels([
                "الرقم", "اسم الموظف", "التاريخ", "التاريخ الهجري",
                "وقت الحضور", "وقت الانصراف", "الحالة"
            ])

            layout.addLayout(date_layout)
            layout.addLayout(buttons_layout)
            layout.addWidget(self.attendance_table)

            self.setLayout(layout)
            self.update_attendance_table()

        except Exception as e:
            self.logger.error(f"خطأ في تهيئة واجهة الحضور: {str(e)}")

    def record_attendance(self, attendance_type: str):
        """تسجيل حضور أو انصراف"""
        try:
            employee_id, ok = QInputDialog.getInt(
                self, 
                f'تسجيل {attendance_type}',
                'أدخل رقم الموظف:',
                1, 1, 99999
            )
            
            if ok:
                if self.attendance_manager.record_attendance(employee_id, attendance_type):
                    QMessageBox.information(
                        self,
                        "نجاح",
                        f"تم تسجيل {attendance_type} بنجاح"
                    )
                    self.update_attendance_table()
                else:
                    QMessageBox.warning(
                        self,
                        "خطأ",
                        f"فشل في تسجيل {attendance_type}"
                    )
                    
        except Exception as e:
            self.logger.error(f"خطأ في تسجيل {attendance_type}: {str(e)}")
            QMessageBox.critical(
                self,
                "خطأ",
                f"حدث خطأ في تسجيل {attendance_type}"
            )

    def update_attendance_table(self):
        """تحديث جدول الحضور"""
        try:
            date = self.date_input.date().toPyDate()
            records = self.attendance_manager.get_daily_records(date)
            
            self.attendance_table.setRowCount(len(records))
            for row, record in enumerate(records):
                self.attendance_table.setItem(row, 0, QTableWidgetItem(str(record[0])))  # رقم الموظف
                self.attendance_table.setItem(row, 1, QTableWidgetItem(record[1]))       # اسم الموظف
                self.attendance_table.setItem(row, 2, QTableWidgetItem(str(record[2])))  # التاريخ
                self.attendance_table.setItem(row, 3, QTableWidgetItem(record[3]))       # التاريخ الهجري
                self.attendance_table.setItem(row, 4, QTableWidgetItem(str(record[4])))  # وقت الحضور
                self.attendance_table.setItem(row, 5, QTableWidgetItem(str(record[5])))  # وقت الانصراف
                self.attendance_table.setItem(row, 6, QTableWidgetItem(record[6]))       # الحالة

            # تعديل عرض الأعمدة
            self.attendance_table.resizeColumnsToContents()
            
        except Exception as e:
            self.logger.error(f"خطأ في تحديث جدول الحضور: {str(e)}")
            QMessageBox.critical(self, "خطأ", "حدث خطأ في تحديث جدول الحضور")