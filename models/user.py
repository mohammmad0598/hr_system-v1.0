# -*- coding: utf-8 -*-
from database.db_handler import DatabaseHandler
import hashlib
import logging

class User:
    def __init__(self):
        self.db = DatabaseHandler()
        self.logger = logging.getLogger('User')
    
    def verify_login(self, username: str, password: str) -> bool:
        """التحقق من صحة بيانات تسجيل الدخول"""
        try:
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            query = "SELECT id FROM users WHERE username = ? AND password = ?"
            result = self.db.fetch_one(query, (username, hashed_password))
            return bool(result)
        except Exception as e:
            self.logger.error(f"خطأ في التحقق من بيانات الدخول: {str(e)}")
            return False
    
    def get_user_data(self, username: str) -> dict:
        """جلب بيانات المستخدم"""
        try:
            query = """
                SELECT u.id, u.username, u.role, u.employee_id,
                       e.name as employee_name, e.department
                FROM users u
                LEFT JOIN employees e ON e.id = u.employee_id
                WHERE u.username = ?
            """
            result = self.db.fetch_one(query, (username,))
            if result:
                return {
                    'id': result[0],
                    'username': result[1],
                    'role': result[2],
                    'employee_id': result[3],
                    'name': result[4] or result[1],  # إذا لم يكن مرتبط بموظف، نستخدم اسم المستخدم
                    'department': result[5] or 'غير محدد'
                }
            return None
        except Exception as e:
            self.logger.error(f"خطأ في جلب بيانات المستخدم: {str(e)}")
            return None
    
    def get_all_users(self) -> list:
        """جلب قائمة المستخدمين"""
        try:
            query = """
                SELECT u.id, u.username, u.role, u.employee_id,
                       e.name as employee_name
                FROM users u
                LEFT JOIN employees e ON e.id = u.employee_id
                ORDER BY u.id
            """
            results = self.db.fetch_all(query)
            return [{
                'id': row[0],
                'username': row[1],
                'role': row[2],
                'employee_id': row[3],
                'employee_name': row[4]
            } for row in results]
        except Exception as e:
            self.logger.error(f"خطأ في جلب قائمة المستخدمين: {str(e)}")
            return []
    
    def add_user(self, data: dict) -> bool:
        """إضافة مستخدم جديد"""
        try:
            # التحقق من عدم تكرار اسم المستخدم
            query = "SELECT id FROM users WHERE username = ?"
            if self.db.fetch_one(query, (data['username'],)):
                self.logger.warning(f"اسم المستخدم {data['username']} موجود مسبقاً")
                return False
            
            # إضافة المستخدم
            hashed_password = hashlib.sha256(data['password'].encode()).hexdigest()
            query = """
                INSERT INTO users (username, password, role, employee_id)
                VALUES (?, ?, ?, ?)
            """
            return self.db.execute(query, (
                data['username'],
                hashed_password,
                data['role'],
                data.get('employee_id')
            ))
        except Exception as e:
            self.logger.error(f"خطأ في إضافة المستخدم: {str(e)}")
            return False
    
    def update_password(self, user_id: int, new_password: str) -> bool:
        """تحديث كلمة المرور"""
        try:
            hashed_password = hashlib.sha256(new_password.encode()).hexdigest()
            query = "UPDATE users SET password = ? WHERE id = ?"
            return self.db.execute(query, (hashed_password, user_id))
        except Exception as e:
            self.logger.error(f"خطأ في تحديث كلمة المرور: {str(e)}")
            return False
    
    def delete_user(self, user_id: int) -> bool:
        """حذف مستخدم"""
        try:
            # لا نسمح بحذف المستخدم admin
            query = "SELECT username FROM users WHERE id = ?"
            result = self.db.fetch_one(query, (user_id,))
            if result and result[0] == 'admin':
                self.logger.warning("لا يمكن حذف المستخدم admin")
                return False
            
            query = "DELETE FROM users WHERE id = ?"
            return self.db.execute(query, (user_id,))
        except Exception as e:
            self.logger.error(f"خطأ في حذف المستخدم: {str(e)}")
            return False
    
    def get_user_permissions(self, user_id: int) -> list:
        """جلب صلاحيات المستخدم"""
        try:
            query = """
                SELECT permission 
                FROM user_permissions 
                WHERE user_id = ?
            """
            results = self.db.fetch_all(query, (user_id,))
            return [row[0] for row in results] if results else []
        except Exception as e:
            self.logger.error(f"خطأ في جلب الصلاحيات: {str(e)}")
            return []
    
    def has_permission(self, user_id: int, permission: str) -> bool:
        """التحقق من وجود صلاحية معينة"""
        try:
            query = """
                SELECT COUNT(*) 
                FROM user_permissions 
                WHERE user_id = ? AND permission = ?
            """
            result = self.db.fetch_one(query, (user_id, permission))
            return result[0] > 0 if result else False
        except Exception as e:
            self.logger.error(f"خطأ في التحقق من الصلاحية: {str(e)}")
            return False