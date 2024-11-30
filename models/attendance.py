# -*- coding: utf-8 -*-
from database.db_handler import DatabaseHandler
import logging
from datetime import datetime
from utils.date_converter import DateConverter
from config.settings import SYSTEM_CONFIG

class Attendance:
    def __init__(self):
        self.db = DatabaseHandler()
        self.logger = logging.getLogger('Attendance')
        self.date_converter = DateConverter()
    
    def record_attendance(self, employee_id: int, attendance_type: str) -> bool:
        """تسجيل حضور أو انصراف"""
        try:
            # التحقق من وجود الموظف
            query = "SELECT id FROM employees WHERE id = ? AND status = 'نشط'"
            if not self.db.fetch_one(query, (employee_id,)):
                self.logger.warning(f"الموظف رقم {employee_id} غير موجود أو غير نشط")
                return False
            
            current_date = datetime.now().date()
            current_time = datetime.now().time()
            
            # تحويل التاريخ إلى هجري
            hijri_date = self.date_converter.to_hijri(current_date)
            
            if attendance_type == 'حضور':
                # التحقق من عدم وجود تسجيل حضور سابق لنفس اليوم
                query = """
                    SELECT id FROM attendance 
                    WHERE employee_id = ? AND date = ? AND type = 'حضور'
                """
                if self.db.fetch_one(query, (employee_id, current_date.strftime('%Y-%m-%d'))):
                    self.logger.warning(f"تم تسجيل حضور للموظف {employee_id} مسبقاً")
                    return False
                
                # تحديد حالة الحضور (متأخر/في الوقت)
                work_start = datetime.strptime(SYSTEM_CONFIG['WORK_START'], '%H:%M').time()
                late_threshold = SYSTEM_CONFIG.get('LATE_THRESHOLD', 15)  # السماح بالتأخير 15 دقيقة
                
                status = 'حاضر'
                if current_time > work_start:
                    minutes_late = (datetime.combine(current_date, current_time) - 
                                  datetime.combine(current_date, work_start)).total_seconds() / 60
                    if minutes_late > late_threshold:
                        status = 'متأخر'
                
                # تسجيل الحضور
                query = """
                    INSERT INTO attendance 
                    (employee_id, date, hijri_date, time, type, status)
                    VALUES (?, ?, ?, ?, ?, ?)
                """
                return self.db.execute(query, (
                    employee_id,
                    current_date.strftime('%Y-%m-%d'),
                    hijri_date,
                    current_time.strftime('%H:%M:%S'),
                    'حضور',
                    status
                ))
                
            elif attendance_type == 'انصراف':
                # التحقق من وجود تسجيل حضور لنفس اليوم
                query = """
                    SELECT id FROM attendance 
                    WHERE employee_id = ? AND date = ? AND type = 'حضور'
                    AND time_out IS NULL
                """
                if not self.db.fetch_one(query, (employee_id, current_date.strftime('%Y-%m-%d'))):
                    self.logger.warning(f"لم يتم تسجيل حضور للموظف {employee_id} أو تم تسجيل انصرافه مسبقاً")
                    return False
                
                # تحديد حالة الانصراف (مبكر/في الوقت)
                work_end = datetime.strptime(SYSTEM_CONFIG['WORK_END'], '%H:%M').time()
                status = 'منصرف'
                if current_time < work_end:
                    status = 'انصراف مبكر'
                
                # تسجيل الانصراف
                query = """
                    UPDATE attendance 
                    SET time_out = ?, status = ?
                    WHERE employee_id = ? AND date = ? AND type = 'حضور'
                    AND time_out IS NULL
                """
                return self.db.execute(query, (
                    current_time.strftime('%H:%M:%S'),
                    status,
                    employee_id,
                    current_date.strftime('%Y-%m-%d')
                ))
            
            return False
            
        except Exception as e:
            self.logger.error(f"خطأ في تسجيل الحضور/الانصراف: {str(e)}")
            return False
    
    def get_daily_records(self, date: datetime.date = None) -> list:
        """جلب سجلات الحضور اليومية"""
        try:
            if not date:
                date = datetime.now().date()
            
            query = """
                SELECT 
                    a.employee_id,
                    e.name,
                    a.date,
                    a.hijri_date,
                    a.time,
                    a.time_out,
                    a.status
                FROM attendance a
                JOIN employees e ON e.id = a.employee_id
                WHERE a.date = ?
                ORDER BY a.time
            """
            return self.db.fetch_all(query, (date.strftime('%Y-%m-%d'),))
            
        except Exception as e:
            self.logger.error(f"خطأ في جلب سجلات الحضور: {str(e)}")
            return []
    
    def get_employee_records(self, employee_id: int, start_date: datetime.date, end_date: datetime.date) -> list:
        """جلب سجلات حضور موظف محدد"""
        try:
            query = """
                SELECT 
                    a.date,
                    a.hijri_date,
                    a.time,
                    a.time_out,
                    a.status
                FROM attendance a
                WHERE a.employee_id = ?
                AND a.date BETWEEN ? AND ?
                ORDER BY a.date DESC
            """
            return self.db.fetch_all(query, (
                employee_id,
                start_date.strftime('%Y-%m-%d'),
                end_date.strftime('%Y-%m-%d')
            ))
            
        except Exception as e:
            self.logger.error(f"خطأ في جلب سجلات الموظف: {str(e)}")
            return []
