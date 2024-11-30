# -*- coding: utf-8 -*-
from database.db_handler import DatabaseHandler
import logging
from datetime import datetime

class EmployeeEvaluation:
    def __init__(self):
        self.db = DatabaseHandler()
        self.logger = logging.getLogger('EmployeeEvaluation')
    
    def add_evaluation(self, data: dict) -> bool:
        """إضافة تقييم جديد"""
        try:
            query = """INSERT INTO evaluations 
                      (employee_id, period, attendance_score, 
                       performance_score, behavior_score, date, notes) 
                      VALUES (?, ?, ?, ?, ?, ?, ?)"""
                      
            total_score = (
                data['attendance_score'] * 0.3 +
                data['performance_score'] * 0.4 +
                data['behavior_score'] * 0.3
            )
            
            self.db.execute(query, (
                data['employee_id'],
                data['period'],
                data['attendance_score'],
                data['performance_score'],
                data['behavior_score'],
                datetime.now(),
                data.get('notes', '')
            ))
            
            # تحديث متوسط تقييم الموظف
            self._update_employee_rating(data['employee_id'])
            return True
            
        except Exception as e:
            self.logger.error(f"خطأ في إضافة التقييم: {str(e)}")
            return False
    
    def get_employee_evaluations(self, employee_id: int) -> list:
        """جلب تقييمات موظف"""
        try:
            query = """
                SELECT e.*, emp.name as employee_name
                FROM evaluations e
                JOIN employees emp ON emp.id = e.employee_id
                WHERE e.employee_id = ?
                ORDER BY e.date DESC
            """
            return self.db.fetch_all(query, (employee_id,))
        except Exception as e:
            self.logger.error(f"خطأ في جلب تقييمات الموظف: {str(e)}")
            return []
    
    def get_department_evaluations(self, department: str, period: str = None) -> list:
        """جلب تقييمات قسم معين"""
        try:
            query = """
                SELECT 
                    emp.name,
                    emp.department,
                    AVG(e.attendance_score) as avg_attendance,
                    AVG(e.performance_score) as avg_performance,
                    AVG(e.behavior_score) as avg_behavior
                FROM evaluations e
                JOIN employees emp ON emp.id = e.employee_id
                WHERE emp.department = ?
            """
            params = [department]
            
            if period:
                query += " AND e.period = ?"
                params.append(period)
                
            query += " GROUP BY emp.id, emp.name, emp.department"
            
            return self.db.fetch_all(query, tuple(params))
        except Exception as e:
            self.logger.error(f"خطأ في جلب تقييمات القسم: {str(e)}")
            return []
    
    def _update_employee_rating(self, employee_id: int) -> bool:
        """تحديث متوسط تقييم الموظف"""
        try:
            query = """
                UPDATE employees 
                SET rating = (
                    SELECT AVG(
                        attendance_score * 0.3 + 
                        performance_score * 0.4 + 
                        behavior_score * 0.3
                    )
                    FROM evaluations
                    WHERE employee_id = ?
                )
                WHERE id = ?
            """
            return self.db.execute(query, (employee_id, employee_id))
        except Exception as e:
            self.logger.error(f"خطأ في تحديث تقييم الموظف: {str(e)}")
            return False 