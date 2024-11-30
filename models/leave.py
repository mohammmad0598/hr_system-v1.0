# -*- coding: utf-8 -*-
from database.db_handler import DatabaseHandler
import logging
from datetime import datetime, timedelta
from utils.date_converter import DateConverter

class Leave:
    def __init__(self):
        self.db = DatabaseHandler()
        self.logger = logging.getLogger('Leave')
        self.date_converter = DateConverter()
    
    def request_leave(self, data: dict) -> bool:
        """تقديم طلب إجازة"""
        try:
            # التحقق من رصيد الإجازات
            if not self._check_leave_balance(data['employee_id'], data['type'], data['duration']):
                return False
            
            query = """
                INSERT INTO leaves 
                (employee_id, type, start_date, end_date, duration, reason, status)
                VALUES (?, ?, ?, ?, ?, ?, 'معلق')
            """
            return self.db.execute(query, (
                data['employee_id'],
                data['type'],
                data['start_date'],
                data['end_date'],
                data['duration'],
                data.get('reason', '')
            ))
            
        except Exception as e:
            self.logger.error(f"خطأ في تقديم طلب الإجازة: {str(e)}")
            return False
    
    def approve_leave(self, leave_id: int, approved_by: int, status: str) -> bool:
        """الموافقة/رفض طلب الإجازة"""
        try:
            query = """
                UPDATE leaves 
                SET status = ?, approved_by = ?, approved_date = ?
                WHERE id = ?
            """
            success = self.db.execute(query, (
                status,
                approved_by,
                datetime.now().strftime('%Y-%m-%d'),
                leave_id
            ))
            
            if success and status == 'مقبول':
                # تحديث رصيد الإجازات
                leave_data = self.get_leave(leave_id)
                if leave_data:
                    self._update_leave_balance(
                        leave_data['employee_id'],
                        leave_data['type'],
                        leave_data['duration']
                    )
            
            return success
            
        except Exception as e:
            self.logger.error(f"خطأ في معالجة طلب الإجازة: {str(e)}")
            return False
    
    def get_leave(self, leave_id: int) -> dict:
        """جلب تفاصيل إجازة محددة"""
        try:
            query = """
                SELECT 
                    l.*,
                    e.name as employee_name,
                    a.name as approved_by_name
                FROM leaves l
                JOIN employees e ON e.id = l.employee_id
                LEFT JOIN employees a ON a.id = l.approved_by
                WHERE l.id = ?
            """
            result = self.db.fetch_one(query, (leave_id,))
            if result:
                return {
                    'id': result[0],
                    'employee_id': result[1],
                    'type': result[2],
                    'start_date': result[3],
                    'end_date': result[4],
                    'duration': result[5],
                    'reason': result[6],
                    'status': result[7],
                    'approved_by': result[8],
                    'approved_date': result[9],
                    'employee_name': result[11],
                    'approved_by_name': result[12]
                }
            return None
            
        except Exception as e:
            self.logger.error(f"خطأ في جلب تفاصيل الإجازة: {str(e)}")
            return None
    
    def get_employee_leaves(self, employee_id: int) -> list:
        """جلب إجازات موظف محدد"""
        try:
            query = """
                SELECT 
                    l.*,
                    e.name as employee_name,
                    a.name as approved_by_name
                FROM leaves l
                JOIN employees e ON e.id = l.employee_id
                LEFT JOIN employees a ON a.id = l.approved_by
                WHERE l.employee_id = ?
                ORDER BY l.start_date DESC
            """
            return self.db.fetch_all(query, (employee_id,))
            
        except Exception as e:
            self.logger.error(f"خطأ في جلب إجازات الموظف: {str(e)}")
            return []
    
    def get_leave_balance(self, employee_id: int) -> dict:
        """جلب رصيد إجازات موظف"""
        try:
            current_year = datetime.now().year
            query = """
                SELECT * FROM leave_balance
                WHERE employee_id = ? AND year = ?
            """
            result = self.db.fetch_one(query, (employee_id, current_year))
            
            if not result:
                # إنشاء رصيد جديد للسنة الحالية
                self._initialize_leave_balance(employee_id, current_year)
                result = self.db.fetch_one(query, (employee_id, current_year))
            
            return {
                'annual': result[3] - result[6],  # المتبقي من السنوية
                'sick': result[4] - result[7],    # المتبقي من المرضية
                'emergency': result[5] - result[8] # المتبقي من الطارئة
            }
            
        except Exception as e:
            self.logger.error(f"خطأ في جلب رصيد الإجازات: {str(e)}")
            return None
    
    def _initialize_leave_balance(self, employee_id: int, year: int) -> bool:
        """تهيئة رصيد إجازات جديد"""
        try:
            query = """
                INSERT INTO leave_balance 
                (employee_id, year)
                VALUES (?, ?)
            """
            return self.db.execute(query, (employee_id, year))
            
        except Exception as e:
            self.logger.error(f"خطأ في تهيئة رصيد الإجازات: {str(e)}")
            return False
    
    def _check_leave_balance(self, employee_id: int, leave_type: str, duration: int) -> bool:
        """التحقق من رصيد الإجازات"""
        try:
            balance = self.get_leave_balance(employee_id)
            if not balance:
                return False
            
            if leave_type == 'سنوية' and balance['annual'] >= duration:
                return True
            elif leave_type == 'مرضية' and balance['sick'] >= duration:
                return True
            elif leave_type == 'طارئة' and balance['emergency'] >= duration:
                return True
            elif leave_type == 'بدون راتب':
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"خطأ في التحقق من رصيد الإجازات: {str(e)}")
            return False
    
    def _update_leave_balance(self, employee_id: int, leave_type: str, duration: int) -> bool:
        """تحديث رصيد الإجازات"""
        try:
            current_year = datetime.now().year
            field_map = {
                'سنوية': 'used_annual',
                'مرضية': 'used_sick',
                'طارئة': 'used_emergency'
            }
            
            if leave_type not in field_map:
                return True  # لا نحتاج لتحديث رصيد الإجازات بدون راتب
            
            query = f"""
                UPDATE leave_balance 
                SET {field_map[leave_type]} = {field_map[leave_type]} + ?
                WHERE employee_id = ? AND year = ?
            """
            return self.db.execute(query, (duration, employee_id, current_year))
            
        except Exception as e:
            self.logger.error(f"خطأ في تحديث رصيد الإجازات: {str(e)}")
            return False 