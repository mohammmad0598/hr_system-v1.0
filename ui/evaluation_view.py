# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                           QLabel, QTableWidget, QTableWidgetItem, QComboBox,
                           QDialog, QFormLayout, QSpinBox, QTextEdit,
                           QDialogButtonBox, QMessageBox)
from PyQt5.QtCore import Qt
from models.evaluation import EmployeeEvaluation

class EvaluationView(QWidget):
    def __init__(self):
        super().__init__()
        self.evaluation_manager = EmployeeEvaluation()
        self.setup_ui()
    
    def setup_ui(self):
        """تهيئة واجهة التقييم"""
        layout = QVBoxLayout()
        
        # تخطيط الفلترة
        filter_layout = QHBoxLayout()
        self.department_combo = QComboBox()
        self.period_combo = QComboBox()
        self.period_combo.addItems(['شهري', 'ربع سنوي', 'سنوي'])
        
        filter_layout.addWidget(QLabel("القسم:"))
        filter_layout.addWidget(self.department_combo)
        filter_layout.addWidget(QLabel("الفترة:"))
        filter_layout.addWidget(self.period_combo)
        filter_layout.addStretch()
        
        # أزرار التحكم
        buttons_layout = QHBoxLayout()
        self.add_button = QPushButton("تقييم جديد")
        self.view_button = QPushButton("عرض التفاصيل")
        self.report_button = QPushButton("تقرير")
        
        self.add_button.clicked.connect(self.add_evaluation)
        self.view_button.clicked.connect(self.view_details)
        self.report_button.clicked.connect(self.generate_report)
        
        buttons_layout.addWidget(self.add_button)
        buttons_layout.addWidget(self.view_button)
        buttons_layout.addWidget(self.report_button)
        
        # جدول التقييمات
        self.evaluations_table = QTableWidget()
        self.evaluations_table.setColumnCount(6)
        self.evaluations_table.setHorizontalHeaderLabels([
            "الموظف", "القسم", "حضور", "أداء", "سلوك", "المتوسط"
        ])
        
        layout.addLayout(filter_layout)
        layout.addLayout(buttons_layout)
        layout.addWidget(self.evaluations_table)
        self.setLayout(layout) 

    def add_evaluation(self):
        """إضافة تقييم جديد"""
        try:
            dialog = QDialog(self)
            dialog.setWindowTitle("تقييم جديد")
            layout = QFormLayout()

            # حقول الإدخال
            employee_id_input = QSpinBox()
            employee_id_input.setMinimum(1)
            
            attendance_score = QSpinBox()
            attendance_score.setRange(0, 100)
            
            performance_score = QSpinBox()
            performance_score.setRange(0, 100)
            
            behavior_score = QSpinBox()
            behavior_score.setRange(0, 100)
            
            notes_input = QTextEdit()
            notes_input.setMaximumHeight(100)
            
            period_input = QComboBox()
            period_input.addItems(['شهري', 'ربع سنوي', 'سنوي'])

            # إضافة الحقول للنموذج
            layout.addRow("رقم الموظف:", employee_id_input)
            layout.addRow("درجة الحضور:", attendance_score)
            layout.addRow("درجة الأداء:", performance_score)
            layout.addRow("درجة السلوك:", behavior_score)
            layout.addRow("الفترة:", period_input)
            layout.addRow("ملاحظات:", notes_input)

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
                evaluation_data = {
                    'employee_id': employee_id_input.value(),
                    'attendance_score': attendance_score.value(),
                    'performance_score': performance_score.value(),
                    'behavior_score': behavior_score.value(),
                    'period': period_input.currentText(),
                    'notes': notes_input.toPlainText()
                }

                if self.evaluation_manager.add_evaluation(evaluation_data):
                    QMessageBox.information(self, "نجاح", "تم إضافة التقييم بنجاح")
                    self.refresh_table()
                else:
                    QMessageBox.warning(self, "خطأ", "فشل في إضافة التقييم")

        except Exception as e:
            self.logger.error(f"خطأ في إضافة تقييم: {str(e)}")
            QMessageBox.critical(self, "خطأ", "حدث خطأ في إضافة التقييم")

    def view_details(self):
        """عرض تفاصيل تقييمات موظف"""
        try:
            current_row = self.evaluations_table.currentRow()
            if current_row < 0:
                QMessageBox.warning(self, "تنبيه", "الرجاء اختيار موظف أولاً")
                return

            employee_name = self.evaluations_table.item(current_row, 0).text()
            employee_id = int(self.evaluations_table.item(current_row, 0).text())

            evaluations = self.evaluation_manager.get_employee_evaluations(employee_id)
            
            dialog = QDialog(self)
            dialog.setWindowTitle(f"تقييمات الموظف: {employee_name}")
            dialog.setMinimumWidth(600)
            
            layout = QVBoxLayout()
            table = QTableWidget()
            table.setColumnCount(7)
            table.setHorizontalHeaderLabels([
                "التاريخ", "الفترة", "حضور", "أداء", "سلوك", "المتوسط", "ملاحظات"
            ])
            
            table.setRowCount(len(evaluations))
            for row, eval_data in enumerate(evaluations):
                table.setItem(row, 0, QTableWidgetItem(str(eval_data[5])))  # date
                table.setItem(row, 1, QTableWidgetItem(eval_data[2]))       # period
                table.setItem(row, 2, QTableWidgetItem(str(eval_data[3])))  # attendance
                table.setItem(row, 3, QTableWidgetItem(str(eval_data[4])))  # performance
                table.setItem(row, 4, QTableWidgetItem(str(eval_data[5])))  # behavior
                
                # حساب المتوسط
                avg = (eval_data[3] * 0.3 + eval_data[4] * 0.4 + eval_data[5] * 0.3)
                table.setItem(row, 5, QTableWidgetItem(f"{avg:.2f}"))
                
                table.setItem(row, 6, QTableWidgetItem(eval_data[7]))       # notes
            
            layout.addWidget(table)
            dialog.setLayout(layout)
            dialog.exec_()

        except Exception as e:
            self.logger.error(f"خطأ في عرض التفاصيل: {str(e)}")
            QMessageBox.critical(self, "خطأ", "حدث خطأ في عرض التفاصيل")

    def generate_report(self):
        """إنشاء تقرير التقييمات"""
        try:
            department = self.department_combo.currentText()
            period = self.period_combo.currentText()
            
            if not department:
                QMessageBox.warning(self, "تنبيه", "الرجاء اختيار القسم")
                return
            
            evaluations = self.evaluation_manager.get_department_evaluations(
                department, period
            )
            
            self.evaluations_table.setRowCount(len(evaluations))
            for row, eval_data in enumerate(evaluations):
                self.evaluations_table.setItem(row, 0, QTableWidgetItem(eval_data[0]))  # name
                self.evaluations_table.setItem(row, 1, QTableWidgetItem(eval_data[1]))  # department
                self.evaluations_table.setItem(row, 2, QTableWidgetItem(f"{eval_data[2]:.2f}"))  # attendance
                self.evaluations_table.setItem(row, 3, QTableWidgetItem(f"{eval_data[3]:.2f}"))  # performance
                self.evaluations_table.setItem(row, 4, QTableWidgetItem(f"{eval_data[4]:.2f}"))  # behavior
                
                # حساب المتوسط
                avg = (eval_data[2] * 0.3 + eval_data[3] * 0.4 + eval_data[4] * 0.3)
                self.evaluations_table.setItem(row, 5, QTableWidgetItem(f"{avg:.2f}"))

        except Exception as e:
            self.logger.error(f"خطأ في إنشاء التقرير: {str(e)}")
            QMessageBox.critical(self, "خطأ", "حدث خطأ في إنشاء التقرير")

    def refresh_table(self):
        """تحديث جدول التقييمات"""
        self.generate_report() 