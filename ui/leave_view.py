# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                           QLabel, QTableWidget, QTableWidgetItem, QDialog,
                           QFormLayout, QLineEdit, QComboBox, QCalendarWidget,
                           QSpinBox, QTextEdit, QMessageBox, QFileDialog)
from PyQt5.QtCore import Qt, QDate
from models.leave import Leave
import logging
from datetime import datetime

class LeaveView(QWidget):
    def __init__(self, current_user=None):
        super().__init__()
        self.leave_manager = Leave()
        self.logger = logging.getLogger('LeaveView')
        self.current_user = current_user
        self.setup_ui()
        
    def setup_ui(self):
        """تهيئة واجهة الإجازات"""
        try:
            layout = QVBoxLayout()
            
            # أزرار التحكم
            buttons_layout = QHBoxLayout()
            request_button = QPushButton("طلب إجازة")
            approve_button = QPushButton("موافقة/رفض")
            balance_button = QPushButton("رصيد الإجازات")
            
            request_button.clicked.connect(self.request_leave)
            approve_button.clicked.connect(self.approve_leave)
            balance_button.clicked.connect(self.show_balance)
            
            buttons_layout.addWidget(request_button)
            buttons_layout.addWidget(approve_button)
            buttons_layout.addWidget(balance_button)
            buttons_layout.addStretch()
            
            # جدول الإجازات
            self.leaves_table = QTableWidget()
            self.leaves_table.setColumnCount(8)
            self.leaves_table.setHorizontalHeaderLabels([
                "الرقم", "الموظف", "النوع", "من تاريخ", "إلى تاريخ",
                "المدة", "الحالة", "تمت الموافقة من"
            ])
            
            layout.addLayout(buttons_layout)
            layout.addWidget(self.leaves_table)
            
            self.setLayout(layout)
            self.refresh_table()
            
            # تعطيل زر الموافقة لغير المدراء
            if self.current_user and self.current_user['role'] not in ['admin', 'hr']:
                approve_button.setEnabled(False)
            
        except Exception as e:
            self.logger.error(f"خطأ في تهيئة واجهة الإجازات: {str(e)}")
    
    def request_leave(self):
        """طلب إجازة جديدة"""
        try:
            dialog = QDialog(self)
            dialog.setWindowTitle("طلب إجازة جديدة")
            layout = QFormLayout()
            
            # نوع الإجازة
            leave_type = QComboBox()
            leave_type.addItems(['سنوية', 'مرضية', 'طارئة', 'بدون راتب'])
            
            # تاريخ البداية
            start_date = QCalendarWidget()
            start_date.setMinimumDate(QDate.currentDate())
            
            # تاريخ النهاية
            end_date = QCalendarWidget()
            end_date.setMinimumDate(QDate.currentDate())
            
            # المدة
            duration = QSpinBox()
            duration.setMinimum(1)
            duration.setMaximum(30)
            
            # السبب
            reason = QTextEdit()
            
            # المرفقات
            attachment_btn = QPushButton("إضافة مرفق")
            attachment_label = QLabel()
            
            def select_file():
                file_path, _ = QFileDialog.getOpenFileName(
                    dialog,
                    "اختر الملف المرفق",
                    "",
                    "All Files (*);;PDF Files (*.pdf)"
                )
                if file_path:
                    attachment_label.setText(file_path)
            
            attachment_btn.clicked.connect(select_file)
            
            layout.addRow("نوع الإجازة:", leave_type)
            layout.addRow("من تاريخ:", start_date)
            layout.addRow("إلى تاريخ:", end_date)
            layout.addRow("عدد الأيام:", duration)
            layout.addRow("السبب:", reason)
            layout.addRow("المرفقات:", attachment_btn)
            layout.addRow("", attachment_label)
            
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
                leave_data = {
                    'employee_id': self.current_user['employee_id'],
                    'type': leave_type.currentText(),
                    'start_date': start_date.selectedDate().toString('yyyy-MM-dd'),
                    'end_date': end_date.selectedDate().toString('yyyy-MM-dd'),
                    'duration': duration.value(),
                    'reason': reason.toPlainText(),
                    'attachment': attachment_label.text()
                }
                
                if self.leave_manager.request_leave(leave_data):
                    QMessageBox.information(self, "نجاح", "تم تقديم طلب الإجازة بنجاح")
                    self.refresh_table()
                else:
                    QMessageBox.warning(self, "خطأ", "فشل في تقديم طلب الإجازة")
                    
        except Exception as e:
            self.logger.error(f"خطأ في طلب إجازة: {str(e)}")
            QMessageBox.critical(self, "خطأ", "حدث خطأ في طلب الإجازة")
    
    def approve_leave(self):
        """الموافقة على طلب إجازة"""
        try:
            current_row = self.leaves_table.currentRow()
            if current_row < 0:
                QMessageBox.warning(self, "تنبيه", "الرجاء اختيار طلب إجازة")
                return
            
            leave_id = int(self.leaves_table.item(current_row, 0).text())
            employee_name = self.leaves_table.item(current_row, 1).text()
            
            dialog = QDialog(self)
            dialog.setWindowTitle("معالجة طلب الإجازة")
            layout = QFormLayout()
            
            status = QComboBox()
            status.addItems(['مقبول', 'مرفوض'])
            
            notes = QTextEdit()
            
            layout.addRow("الحالة:", status)
            layout.addRow("ملاحظات:", notes)
            
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
                if self.leave_manager.approve_leave(
                    leave_id,
                    self.current_user['employee_id'],
                    status.currentText()
                ):
                    QMessageBox.information(self, "نجاح", "تم معالجة طلب الإجازة بنجاح")
                    self.refresh_table()
                else:
                    QMessageBox.warning(self, "خطأ", "فشل في معالجة طلب الإجازة")
                    
        except Exception as e:
            self.logger.error(f"خطأ في معالجة طلب الإجازة: {str(e)}")
            QMessageBox.critical(self, "خطأ", "حدث خطأ في معالجة طلب الإجازة")
    
    def show_balance(self):
        """عرض رصيد الإجازات"""
        try:
            balance = self.leave_manager.get_leave_balance(self.current_user['employee_id'])
            if balance:
                QMessageBox.information(
                    self,
                    "رصيد الإجازات",
                    f"""
                    الإجازات السنوية: {balance['annual']} يوم
                    الإجازات المرضية: {balance['sick']} يوم
                    الإجازات الطارئة: {balance['emergency']} يوم
                    """
                )
            else:
                QMessageBox.warning(self, "خطأ", "فشل في جلب رصيد الإجازات")
                
        except Exception as e:
            self.logger.error(f"خطأ في عرض رصيد الإجازات: {str(e)}")
            QMessageBox.critical(self, "خطأ", "حدث خطأ في عرض رصيد الإجازات")
    
    def refresh_table(self):
        """تحديث جدول الإجازات"""
        try:
            if self.current_user['role'] in ['admin', 'hr']:
                # المدراء يرون جميع الطلبات
                leaves = self.leave_manager.get_all_leaves()
            else:
                # الموظفون يرون طلباتهم فقط
                leaves = self.leave_manager.get_employee_leaves(self.current_user['employee_id'])
            
            self.leaves_table.setRowCount(len(leaves))
            for row, leave in enumerate(leaves):
                self.leaves_table.setItem(row, 0, QTableWidgetItem(str(leave[0])))
                self.leaves_table.setItem(row, 1, QTableWidgetItem(leave['employee_name']))
                self.leaves_table.setItem(row, 2, QTableWidgetItem(leave['type']))
                self.leaves_table.setItem(row, 3, QTableWidgetItem(leave['start_date']))
                self.leaves_table.setItem(row, 4, QTableWidgetItem(leave['end_date']))
                self.leaves_table.setItem(row, 5, QTableWidgetItem(str(leave['duration'])))
                self.leaves_table.setItem(row, 6, QTableWidgetItem(leave['status']))
                self.leaves_table.setItem(row, 7, QTableWidgetItem(leave['approved_by_name'] or '-'))
            
            self.leaves_table.resizeColumnsToContents()
            
        except Exception as e:
            self.logger.error(f"خطأ في تحديث جدول الإجازات: {str(e)}") 