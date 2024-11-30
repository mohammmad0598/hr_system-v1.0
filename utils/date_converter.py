# -*- coding: utf-8 -*-
from hijri_converter import convert
from datetime import date, datetime
import logging

class DateConverter:
    def __init__(self):
        self.logger = logging.getLogger('DateConverter')
    
    def to_hijri(self, gregorian_date: date) -> str:
        """تحويل التاريخ الميلادي إلى هجري"""
        try:
            hijri_date = convert.Gregorian(
                gregorian_date.year,
                gregorian_date.month,
                gregorian_date.day
            ).to_hijri()
            return f"{hijri_date.day}/{hijri_date.month}/{hijri_date.year}"
        except Exception as e:
            self.logger.error(f"خطأ في تحويل التاريخ إلى هجري: {str(e)}")
            return ""

    def to_gregorian(self, hijri_date: str) -> date:
        """تحويل التاريخ الهجري إلى ميلادي"""
        try:
            day, month, year = map(int, hijri_date.split('/'))
            gregorian = convert.Hijri(year, month, day).to_gregorian()
            return date(gregorian.year, gregorian.month, gregorian.day)
        except Exception as e:
            self.logger.error(f"خطأ في تحويل التاريخ إلى ميلادي: {str(e)}")
            return None
    
    def format_date(self, date_obj: date, include_hijri: bool = True) -> str:
        """تنسيق التاريخ"""
        try:
            gregorian = date_obj.strftime('%Y/%m/%d')
            if include_hijri:
                hijri = self.to_hijri(date_obj)
                return f"{gregorian} - {hijri}"
            return gregorian
        except Exception as e:
            self.logger.error(f"خطأ في تنسيق التاريخ: {str(e)}")
            return "" 