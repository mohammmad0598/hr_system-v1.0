# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                           QStackedWidget, QPushButton, QLabel, QMessageBox,
                           QMenuBar, QMenu, QAction)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from ui.employees_view import EmployeesView
from ui.attendance_view import AttendanceView
from ui.evaluation_view import EvaluationView
from ui.salary_view import SalaryView
from ui.user_management import UserManagementDialog
from ui.leave_view import LeaveView
import logging

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger('MainWindow')
        self.current_user = None
        self.setup_ui()
        self.setup_menu()
        
    def setup_ui(self):
        """تهيئة الواجهة الرئيسية"""
        try:
            self.setWindowTitle("نظام إدارة الموارد البشرية")
            self.setGeometry(100, 100, 1200, 700)
            
            # الواجهة المركزية
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            
            # التخطيط الرئيسي
            main_layout = QVBoxLayout()
            central_widget.setLayout(main_layout)
            
            # شعار الشركة
            logo_label = QLabel()
            logo_path = "resources/images/logo.png"
            try:
                pixmap = QPixmap(logo_path)
                logo_label.setPixmap(pixmap.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                logo_label.setAlignment(Qt.AlignCenter)
            except:
                self.logger.warning("لم يتم العثور على شعار الشركة")
            
            # تخطيط المحتوى
            content_layout = QHBoxLayout()
            
            # القائمة الجانبية
            sidebar = QWidget()
            sidebar.setMaximumWidth(200)
            sidebar.setStyleSheet("""
                QWidget {
                    background-color: #2c3e50;
                    color: white;
                }
                QPushButton {
                    text-align: right;
                    padding: 10px;
                    border: none;
                    background-color: transparent;
                }
                QPushButton:hover {
                    background-color: #34495e;
                }
            """)
            
            sidebar_layout = QVBoxLayout()
            sidebar_layout.setSpacing(0)
            sidebar_layout.setContentsMargins(0, 0, 0, 0)
            
            # معلومات المستخدم
            self.user_info = QLabel()
            self.user_info.setStyleSheet("padding: 10px;")
            sidebar_layout.addWidget(self.user_info)
            
            # أزرار القائمة
            self.employees_btn = QPushButton("الموظفين")
            self.attendance_btn = QPushButton("الحضور والانصراف")
            self.evaluation_btn = QPushButton("التقييمات")
            self.salary_btn = QPushButton("الرواتب")
            self.leaves_btn = QPushButton("الإجازات")
            
            sidebar_layout.addWidget(self.employees_btn)
            sidebar_layout.addWidget(self.attendance_btn)
            sidebar_layout.addWidget(self.evaluation_btn)
            sidebar_layout.addWidget(self.salary_btn)
            sidebar_layout.addWidget(self.leaves_btn)
            
            # ربط الأزرار بالوظائف
            self.employees_btn.clicked.connect(lambda: self.switch_view(0))
            self.attendance_btn.clicked.connect(lambda: self.switch_view(1))
            self.evaluation_btn.clicked.connect(lambda: self.switch_view(2))
            self.salary_btn.clicked.connect(lambda: self.switch_view(3))
            self.leaves_btn.clicked.connect(lambda: self.switch_view(4))
            
            sidebar_layout.addStretch()
            sidebar.setLayout(sidebar_layout)
            
            # مكدس الواجهات
            self.stack = QStackedWidget()
            self.employees_view = EmployeesView()
            self.attendance_view = AttendanceView()
            self.evaluation_view = EvaluationView()
            self.salary_view = SalaryView()
            self.leaves_view = LeaveView(self.current_user)
            
            self.stack.addWidget(self.employees_view)
            self.stack.addWidget(self.attendance_view)
            self.stack.addWidget(self.evaluation_view)
            self.stack.addWidget(self.salary_view)
            self.stack.addWidget(self.leaves_view)
            
            # إضافة العناصر للتخطيط
            content_layout.addWidget(sidebar)
            content_layout.addWidget(self.stack)
            
            main_layout.addWidget(logo_label)
            main_layout.addLayout(content_layout)
            
        except Exception as e:
            self.logger.error(f"خطأ في تهيئة الواجهة الرئيسية: {str(e)}")

    def setup_menu(self):
        """إعداد القائمة العلوية"""
        try:
            menubar = self.menuBar()
            
            # قائمة النظام
            system_menu = menubar.addMenu("النظام")
            
            # إدارة المستخدمين
            user_management_action = QAction("إدارة المستخدمين", self)
            user_management_action.triggered.connect(self.show_user_management)
            system_menu.addAction(user_management_action)
            
            # تغيير كلمة المرور
            change_password_action = QAction("تغيير كلمة المرور", self)
            change_password_action.triggered.connect(self.change_password)
            system_menu.addAction(change_password_action)
            
            system_menu.addSeparator()
            
            # تسجيل الخروج
            logout_action = QAction("تسجيل الخروج", self)
            logout_action.triggered.connect(self.close)
            system_menu.addAction(logout_action)
            
        except Exception as e:
            self.logger.error(f"خطأ في إعداد القائمة: {str(e)}")

    def show_user_management(self):
        """عرض نافذة إدارة المستخدمين"""
        try:
            if self.current_user and self.current_user['role'] == 'admin':
                dialog = UserManagementDialog(self)
                dialog.exec_()
            else:
                QMessageBox.warning(self, "تنبيه", "غير مصرح لك بالوصول لهذه الصفحة")
        except Exception as e:
            self.logger.error(f"خطأ في فتح نافذة إدارة المستخدمين: {str(e)}")

    def change_password(self):
        """تغيير كلمة المرور للمستخدم الحالي"""
        try:
            if self.current_user:
                dialog = UserManagementDialog(self)
                dialog.change_password()
        except Exception as e:
            self.logger.error(f"خطأ في تغيير كلمة المرور: {str(e)}")

    def initialize_user(self, user_data: dict):
        """تهيئة بيانات المستخدم"""
        try:
            self.current_user = user_data
            self.user_info.setText(f"""
                المستخدم: {user_data['name']}
                الدور: {user_data['role']}
                القسم: {user_data['department']}
            """)
            
            # تفعيل/تعطيل الأزرار حسب الصلاحيات
            self.employees_btn.setEnabled(user_data['role'] in ['admin', 'hr'])
            self.salary_btn.setEnabled(user_data['role'] in ['admin', 'hr', 'finance'])
            
        except Exception as e:
            self.logger.error(f"خطأ في تهيئة بيانات المستخدم: {str(e)}")
    
    def switch_view(self, index: int):
        """التبديل بين الواجهات"""
        try:
            self.stack.setCurrentIndex(index)
        except Exception as e:
            self.logger.error(f"خطأ في تبديل الواجهة: {str(e)}")
    
    def closeEvent(self, event):
        """معالجة إغلاق النافذة"""
        try:
            reply = QMessageBox.question(
                self, 'تأكيد',
                'هل أنت متأكد من الخروج من النظام؟',
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                event.accept()
            else:
                event.ignore()
                
        except Exception as e:
            self.logger.error(f"خطأ في معالجة إغلاق النافذة: {str(e)}")