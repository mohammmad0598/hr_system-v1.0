# -*- coding: utf-8 -*-
import sqlite3
import logging
from config.settings import DATABASE_PATH

class DatabaseHandler:
    def __init__(self):
        self.db_path = DATABASE_PATH
        self.logger = logging.getLogger('DatabaseHandler')
    
    def execute(self, query: str, params: tuple = None) -> bool:
        """تنفيذ استعلام قاعدة البيانات"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                conn.commit()
                return True
        except Exception as e:
            self.logger.error(f"خطأ في تنفيذ الاستعلام: {str(e)}")
            return False
    
    def fetch_all(self, query: str, params: tuple = None) -> list:
        """جلب جميع النتائج"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                return cursor.fetchall()
        except Exception as e:
            self.logger.error(f"خطأ في جلب البيانات: {str(e)}")
            return []
    
    def fetch_one(self, query: str, params: tuple = None):
        """جلب نتيجة واحدة"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                return cursor.fetchone()
        except Exception as e:
            self.logger.error(f"خطأ في جلب البيانات: {str(e)}")
            return None
    
    def execute_many(self, query: str, params_list: list) -> bool:
        """تنفيذ استعلام متعدد"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.executemany(query, params_list)
                conn.commit()
                return True
        except Exception as e:
            self.logger.error(f"خطأ في تنفيذ الاستعلام المتعدد: {str(e)}")
            return False
