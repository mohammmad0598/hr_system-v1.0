# -*- coding: utf-8 -*-
import os
from dotenv import load_dotenv

# تحميل المتغيرات البيئية
load_dotenv()

# المسار الأساسي للتطبيق
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# مسار قاعدة البيانات
DATABASE_PATH = os.path.join(BASE_DIR, 'database', 'hr_system.db')

# إعدادات النظام
SYSTEM_CONFIG = {
    'rtl': True,
    'language': 'ar',
    'date_format': 'yyyy-MM-dd',
    'time_format': 'HH:mm:ss',
    'currency': 'SAR',
    
    # إعدادات Twilio
    'TWILIO_SID': os.getenv('TWILIO_SID', ''),
    'TWILIO_TOKEN': os.getenv('TWILIO_TOKEN', ''),
    'TWILIO_PHONE': os.getenv('TWILIO_PHONE', ''),
    
    # أوقات الدوام
    'WORK_START': '09:00',
    'WORK_END': '17:00',
    'LATE_THRESHOLD': 15,  # السماح بالتأخير 15 دقيقة
    
    # مسارات الملفات
    'REPORTS_DIR': os.path.join(BASE_DIR, 'reports'),
    'LOGS_DIR': os.path.join(BASE_DIR, 'logs'),
    'BACKUP_DIR': os.path.join(BASE_DIR, 'backups'),
    'RESOURCES_DIR': os.path.join(BASE_DIR, 'resources'),
    
    # إعدادات الشركة
    'COMPANY_NAME': 'شركة نظام الموارد البشرية',
    'COMPANY_ADDRESS': 'المملكة العربية السعودية',
    'COMPANY_PHONE': '+966000000000',
    'COMPANY_EMAIL': 'info@hr-system.com',
    'COMPANY_WEBSITE': 'www.hr-system.com',
    
    # إعدادات الأمان
    'SESSION_TIMEOUT': 30,  # مدة الجلسة بالدقائق
    'MAX_LOGIN_ATTEMPTS': 3,  # عدد محاولات تسجيل الدخول
    'PASSWORD_EXPIRY_DAYS': 90,  # مدة صلاحية كلمة المرور بالأيام
    
    # إعدادات النسخ الاحتياطي
    'BACKUP_ENABLED': True,
    'BACKUP_FREQUENCY': 'daily',  # daily, weekly, monthly
    'MAX_BACKUPS': 10  # عدد النسخ الاحتياطية المحتفظ بها
}

# إنشاء المجلدات المطلوبة
for dir_path in [SYSTEM_CONFIG['REPORTS_DIR'], SYSTEM_CONFIG['LOGS_DIR']]:
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
