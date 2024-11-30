# -*- coding: utf-8 -*-
import os
import shutil
from datetime import datetime
import sqlite3
import logging
from config.settings import SYSTEM_CONFIG, DATABASE_PATH

class BackupManager:
    def __init__(self):
        self.logger = logging.getLogger('BackupManager')
        self.backup_dir = os.path.join(SYSTEM_CONFIG['BACKUP_DIR'])
        
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
    
    def create_backup(self) -> bool:
        """إنشاء نسخة احتياطية"""
        try:
            # اسم ملف النسخة الاحتياطية
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = os.path.join(self.backup_dir, f"backup_{timestamp}.db")
            
            # نسخ قاعدة البيانات
            shutil.copy2(DATABASE_PATH, backup_file)
            
            self.logger.info(f"تم إنشاء نسخة احتياطية: {backup_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"خطأ في إنشاء النسخة الاحتياطية: {str(e)}")
            return False
    
    def restore_backup(self, backup_file: str) -> bool:
        """استعادة نسخة احتياطية"""
        try:
            # التحقق من صحة ملف النسخة الاحتياطية
            if not os.path.exists(backup_file):
                self.logger.error("ملف النسخة الاحتياطية غير موجود")
                return False
            
            # إغلاق جميع الاتصالات
            connection = sqlite3.connect(DATABASE_PATH)
            connection.close()
            
            # استبدال قاعدة البيانات الحالية
            shutil.copy2(backup_file, DATABASE_PATH)
            
            self.logger.info(f"تم استعادة النسخة الاحتياطية: {backup_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"خطأ في استعادة النسخة الاحتياطية: {str(e)}")
            return False
    
    def get_backups(self) -> list:
        """جلب قائمة النسخ الاحتياطية"""
        try:
            backups = []
            for file in os.listdir(self.backup_dir):
                if file.startswith("backup_") and file.endswith(".db"):
                    file_path = os.path.join(self.backup_dir, file)
                    file_date = datetime.fromtimestamp(os.path.getctime(file_path))
                    backups.append({
                        'file': file,
                        'path': file_path,
                        'date': file_date,
                        'size': os.path.getsize(file_path)
                    })
            return sorted(backups, key=lambda x: x['date'], reverse=True)
            
        except Exception as e:
            self.logger.error(f"خطأ في جلب قائمة النسخ الاحتياطية: {str(e)}")
            return [] 