# -*- coding: utf-8 -*-
import re
from datetime import datetime

class Validators:
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """التحقق من صحة رقم الهاتف"""
        pattern = r'^(05)\d{8}$'
        return bool(re.match(pattern, phone))
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """التحقق من صحة البريد الإلكتروني"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_name(name: str) -> bool:
        """التحقق من صحة الاسم"""
        return len(name.strip()) >= 3 and all(c.isalpha() or c.isspace() for c in name)
    
    @staticmethod
    def validate_password(password: str) -> tuple:
        """التحقق من قوة كلمة المرور"""
        if len(password) < 8:
            return False, "كلمة المرور يجب أن تكون 8 أحرف على الأقل"
        
        if not re.search(r"[A-Z]", password):
            return False, "يجب أن تحتوي على حرف كبير واحد على الأقل"
            
        if not re.search(r"[a-z]", password):
            return False, "يجب أن تحتوي على حرف صغير واحد على الأقل"
            
        if not re.search(r"\d", password):
            return False, "يجب أن تحتوي على رقم واحد على الأقل"
            
        if not re.search(r"[ !@#$%&'()*+,-./[\\\]^_`{|}~"+r'"]', password):
            return False, "يجب أن تحتوي على رمز خاص واحد على الأقل"
            
        return True, "كلمة مرور قوية"
    
    @staticmethod
    def validate_date(date_str: str) -> bool:
        """التحقق من صحة التاريخ"""
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            return True
        except ValueError:
            return False
    
    @staticmethod
    def validate_salary(salary: str) -> bool:
        """التحقق من صحة الراتب"""
        try:
            salary_float = float(salary)
            return salary_float >= 0
        except ValueError:
            return False 