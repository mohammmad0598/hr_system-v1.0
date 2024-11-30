# -*- coding: utf-8 -*-
import sys
import os
from datetime import datetime
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

# إضافة المسار الرئيسي للمشروع
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from config.settings import SYSTEM_CONFIG
from utils.logger import Logger
from utils.backup import BackupManager
from ui.login_window import LoginWindow
from ui.main_window import MainWindow

def setup_system():
    """تهيئة النظام"""
    try:
        # إنشاء المجلدات المطلوبة
        for dir_path in [
            SYSTEM_CONFIG['REPORTS_DIR'],
            SYSTEM_CONFIG['LOGS_DIR'],
            SYSTEM_CONFIG['BACKUP_DIR'],
            SYSTEM_CONFIG['RESOURCES_DIR'],
            os.path.join(SYSTEM_CONFIG['RESOURCES_DIR'], 'images'),
            os.path.join(SYSTEM_CONFIG['RESOURCES_DIR'], 'fonts')
        ]:
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
        
        # إعداد نظام التسجيل
        if not Logger.setup():
            print("فشل في تهيئة نظام التسجيل")
            return False
        
        # إنشاء نسخة احتياطية تلقائية
        backup_manager = BackupManager()
        if not backup_manager.create_backup():
            print("فشل في إنشاء نسخة احتياطية")
            return False
        
        # تهيئة قاعدة البيانات
        from database.init_db import init_database
        if not init_database():
            print("فشل في تهيئة قاعدة البيانات")
            return False
        
        return True
        
    except Exception as e:
        print(f"خطأ في تهيئة النظام: {str(e)}")
        return False

def main():
    """الدالة الرئيسية للبرنامج"""
    try:
        # تهيئة النظام
        if not setup_system():
            return
        
        # إنشاء التطبيق
        app = QApplication(sys.argv)
        
        # تطبيق الإعدادات العامة
        app.setLayoutDirection(Qt.RightToLeft)
        app.setStyle('Fusion')
        
        # تعيين أيقونة التطبيق
        icon_path = os.path.join(SYSTEM_CONFIG['RESOURCES_DIR'], 'images', 'icon.png')
        if os.path.exists(icon_path):
            app.setWindowIcon(QIcon(icon_path))
        
        # إنشاء النوافذ
        login_window = LoginWindow()
        main_window = MainWindow()
        
        # ربط نجاح تسجيل الدخول بفتح النافذة الرئيسية
        def on_login(user_data):
            main_window.initialize_user(user_data)
            main_window.show()
            login_window.close()
        
        login_window.login_success.connect(on_login)
        login_window.show()
        
        sys.exit(app.exec_())
        
    except Exception as e:
        print(f"خطأ في تشغيل البرنامج: {str(e)}")

if __name__ == '__main__':
    main() 