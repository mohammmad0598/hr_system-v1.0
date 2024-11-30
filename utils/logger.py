# -*- coding: utf-8 -*-
import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler
from config.settings import SYSTEM_CONFIG

class Logger:
    @staticmethod
    def setup():
        """إعداد نظام التسجيل"""
        try:
            # إنشاء مجلد السجلات
            if not os.path.exists(SYSTEM_CONFIG['LOGS_DIR']):
                os.makedirs(SYSTEM_CONFIG['LOGS_DIR'])
            
            # تنسيق السجل
            log_format = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            
            # ملف السجل
            log_file = os.path.join(
                SYSTEM_CONFIG['LOGS_DIR'],
                f"hr_system_{datetime.now().strftime('%Y%m%d')}.log"
            )
            
            # إعداد مُعالج الملف
            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=5*1024*1024,  # 5 ميجابايت
                backupCount=5,
                encoding='utf-8'
            )
            file_handler.setFormatter(log_format)
            
            # إعداد مُعالج وحدة التحكم
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(log_format)
            
            # إعداد المُسجل الرئيسي
            root_logger = logging.getLogger()
            root_logger.setLevel(logging.INFO)
            root_logger.addHandler(file_handler)
            root_logger.addHandler(console_handler)
            
            return True
            
        except Exception as e:
            print(f"خطأ في إعداد نظام التسجيل: {str(e)}")
            return False 