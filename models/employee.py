# -*- coding: utf-8 -*-
from database.db_handler import DatabaseHandler
import logging
from datetime import datetime

class Employee:
    def __init__(self):
        self.db = DatabaseHandler()
        self.logger = logging.getLogger('Employee')
    
    def add_employee(self, data: dict) -> bool:
        """إضافة موظف جديد"""
        try:
            # تحويل التاريخ إلى نص
            join_date = data['join_date'].strftime('%Y-%m-%d')
            
            query = """
                INSERT INTO employees 
                (name, position, department, join_date, basic_salary, phone, email)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            return self.db.execute(query, (
                data['name'],
                data['position'],
                data['department'],
                join_date,  # تاريخ التعيين كنص
                data['salary'],
                data.get('phone', ''),
                data.get('email', '')
            ))
            
        except Exception as e:
            self.logger.error(f"خطأ في إضافة موظف: {str(e)}")
            return False
    
    def update_employee(self, data: dict) -> bool:
        """تحديث بيانات موظف"""
        try:
            query = """
                UPDATE employees 
                SET name = ?,
                    position = ?,
                    department = ?,
                    basic_salary = ?,
                    phone = ?,
                    email = ?
                WHERE id = ?
            """
            return self.db.execute(query, (
                data['name'],
                data['position'],
                data['department'],
                data['salary'],
                data.get('phone', ''),
                data.get('email', ''),
                data['id']
            ))
        except Exception as e:
            self.logger.error(f"خطأ في تحديث بيانات الموظف: {str(e)}")
            return False
    
    def delete_employee(self, employee_id: int) -> bool:
        """حذف موظف"""
        try:
            query = "UPDATE employees SET status = 'غير نشط' WHERE id = ?"
            return self.db.execute(query, (employee_id,))
        except Exception as e:
            self.logger.error(f"خطأ في حذف الموظف: {str(e)}")
            return False
    
    def get_all_employees(self) -> list:
        """جلب قائمة الموظفين"""
        try:
            query = """
                SELECT 
                    id, name, department, position, join_date,
                    basic_salary, phone, email, status
                FROM employees
                WHERE status = 'نشط'
                ORDER BY id
            """
            results = self.db.fetch_all(query)
            return [self._format_employee_data(row) for row in results]
        except Exception as e:
            self.logger.error(f"خطأ في جلب قائمة الموظفين: {str(e)}")
            return []
    
    def _format_employee_data(self, row: tuple) -> dict:
        """تنسيق بيانات الموظف"""
        return {
            'id': row[0],
            'name': row[1],
            'department': row[2],
            'position': row[3],
            'join_date': row[4],
            'salary': row[5],
            'phone': row[6],
            'email': row[7],
            'status': row[8]
        }
