# -*- coding: utf-8 -*-
import os
import sys
import sqlite3
import hashlib
import random
from datetime import datetime, timedelta

# إضافة المسار الرئيسي للمشروع
current_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(current_dir)
sys.path.append(project_dir)

from config.settings import DATABASE_PATH

def generate_sample_data(cursor):
    """إنشاء بيانات افتراضية"""
    
    # قوائم البيانات الافتراضية
    departments = ['الموارد البشرية', 'المالية', 'تقنية المعلومات', 'التسويق', 'المبيعات', 'خدمة العملاء', 'الإدارة']
    positions = ['مدير', 'مشرف', 'موظف', 'محاسب', 'مبرمج', 'مسوق', 'محلل', 'منسق']
    first_names = ['محمد', 'أحمد', 'عبدالله', 'خالد', 'فهد', 'عمر', 'سعد', 'علي', 'يوسف', 'إبراهيم']
    last_names = ['العمري', 'السعيد', 'الحربي', 'القحطاني', 'الغامدي', 'السلمي', 'المالكي', 'الزهراني', 'الشهري', 'الدوسري']
    
    # إنشاء 100 موظف
    employees_data = []
    for i in range(1, 101):
        name = f"{random.choice(first_names)} {random.choice(last_names)}"
        department = random.choice(departments)
        position = random.choice(positions)
        
        # تاريخ التعيين خلال السنتين الماضيتين
        join_date = datetime.now() - timedelta(days=random.randint(1, 730))
        
        # الراتب الأساسي بين 4000 و 15000
        basic_salary = random.randint(4000, 15000)
        
        # رقم الجوال
        phone = f"0{random.choice(['55', '54', '53', '56'])}{random.randint(1000000, 9999999)}"
        
        # البريد الإلكتروني
        email = f"{name.replace(' ', '.').lower()}@company.com"
        
        employees_data.append((
            name,
            position,
            department,
            join_date.strftime('%Y-%m-%d'),
            basic_salary,
            phone,
            email,
            'نشط'
        ))
    
    # إدخال بيانات الموظفين
    cursor.executemany('''
        INSERT INTO employees 
        (name, position, department, join_date, basic_salary, phone, email, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', employees_data)
    
    # إنشاء بدلات للموظفين
    allowances_data = []
    for emp_id in range(1, 101):
        housing = random.uniform(0.2, 0.4) * basic_salary  # 20-40% من الراتب الأساسي
        transport = random.uniform(0.1, 0.2) * basic_salary  # 10-20% من الراتب الأساسي
        allowances_data.append((emp_id, housing, transport))
    
    cursor.executemany('''
        INSERT INTO employee_allowances 
        (employee_id, housing_allowance, transport_allowance)
        VALUES (?, ?, ?)
    ''', allowances_data)
    
    # إنشاء مستخدمين للنظام
    users_data = [
        ('admin', hashlib.sha256('admin123'.encode()).hexdigest(), 'admin', None),
        ('hr_manager', hashlib.sha256('hr123'.encode()).hexdigest(), 'hr', 1),
        ('finance_manager', hashlib.sha256('finance123'.encode()).hexdigest(), 'finance', 2)
    ]
    
    cursor.executemany('''
        INSERT INTO users (username, password, role, employee_id)
        VALUES (?, ?, ?, ?)
    ''', users_data)

def init_database():
    """تهيئة قاعدة البيانات وإنشاء الجداول"""
    try:
        # التأكد من وجود مجلد قاعدة البيانات
        database_dir = os.path.dirname(DATABASE_PATH)
        if database_dir and not os.path.exists(database_dir):
            os.makedirs(database_dir)
        
        # حذف قاعدة البيانات القديمة إذا كانت موجودة
        if os.path.exists(DATABASE_PATH):
            os.remove(DATABASE_PATH)
        
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        # جدول الموظفين
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            position TEXT,
            department TEXT,
            join_date TEXT,
            basic_salary REAL DEFAULT 0,
            phone TEXT,
            email TEXT,
            status TEXT DEFAULT 'نشط'
        )
        ''')

        # جدول المستخدمين
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            employee_id INTEGER,
            FOREIGN KEY (employee_id) REFERENCES employees (id)
        )
        ''')

        # جدول الحضور
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            hijri_date TEXT,
            time TEXT NOT NULL,
            time_out TEXT,
            type TEXT NOT NULL,
            status TEXT NOT NULL,
            FOREIGN KEY (employee_id) REFERENCES employees (id)
        )
        ''')

        # جدول التقييمات
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS evaluations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER,
            period TEXT,
            attendance_score INTEGER,
            performance_score INTEGER,
            behavior_score INTEGER,
            date TEXT,
            notes TEXT,
            FOREIGN KEY (employee_id) REFERENCES employees (id)
        )
        ''')

        # جدول البدلات الثابتة
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS employee_allowances (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER,
            housing_allowance REAL DEFAULT 0,
            transport_allowance REAL DEFAULT 0,
            FOREIGN KEY (employee_id) REFERENCES employees (id)
        )
        ''')

        # جدول البدلات الإضافية
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS extra_allowances (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER,
            amount REAL,
            reason TEXT,
            date TEXT,
            FOREIGN KEY (employee_id) REFERENCES employees (id)
        )
        ''')

        # جدول الخصومات
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS deductions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER,
            amount REAL,
            reason TEXT,
            date TEXT,
            FOREIGN KEY (employee_id) REFERENCES employees (id)
        )
        ''')

        # إدول الإجازات
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS leaves (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER NOT NULL,
            type TEXT NOT NULL,  -- سنوية، مرضية، طارئة، بدون راتب
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            duration INTEGER NOT NULL,  -- عدد الأيام
            reason TEXT,
            status TEXT NOT NULL,  -- معلق، مقبول، مرفوض
            approved_by INTEGER,  -- معرف الموظف الذي وافق على الإجازة
            approved_date TEXT,
            attachment TEXT,  -- مسار الملف المرفق (مثل التقرير الطبي)
            notes TEXT,
            FOREIGN KEY (employee_id) REFERENCES employees (id),
            FOREIGN KEY (approved_by) REFERENCES employees (id)
        )
        ''')

        # جدول رصيد الإجازات
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS leave_balance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER NOT NULL,
            year INTEGER NOT NULL,
            annual_leave INTEGER DEFAULT 30,  -- رصيد الإجازة السنوية
            sick_leave INTEGER DEFAULT 15,    -- رصيد الإجازة المرضية
            emergency_leave INTEGER DEFAULT 7, -- رصيد الإجازة الطارئة
            used_annual INTEGER DEFAULT 0,    -- الإجازات السنوية المستخدمة
            used_sick INTEGER DEFAULT 0,      -- الإجازات المرضية المستخدمة
            used_emergency INTEGER DEFAULT 0,  -- الإجازات الطارئة المستخدمة
            FOREIGN KEY (employee_id) REFERENCES employees (id),
            UNIQUE(employee_id, year)
        )
        ''')

        # إضافة البيانات الافتراضية
        generate_sample_data(cursor)

        conn.commit()
        conn.close()
        
        print("تم تهيئة قاعدة البيانات وإضافة البيانات الافتراضية بنجاح")
        print(f"مسار قاعدة البيانات: {DATABASE_PATH}")
        return True
        
    except Exception as e:
        print(f"حدث خطأ في تهيئة قاعدة البيانات: {str(e)}")
        return False

if __name__ == '__main__':
    init_database() 