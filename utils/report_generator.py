# -*- coding: utf-8 -*-
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
import arabic_reshaper
from bidi.algorithm import get_display
from datetime import datetime
import os
import logging
from config.settings import SYSTEM_CONFIG

class ReportGenerator:
    def __init__(self):
        self.logger = logging.getLogger('ReportGenerator')
        self._setup_fonts()
        
    def _setup_fonts(self):
        """تهيئة الخطوط العربية"""
        try:
            font_path = os.path.join(SYSTEM_CONFIG['RESOURCES_DIR'], 'fonts', 'arabic.ttf')
            pdfmetrics.registerFont(TTFont('Arabic', font_path))
        except Exception as e:
            self.logger.error(f"خطأ في تحميل الخطوط: {str(e)}")

    def _prepare_arabic_text(self, text: str) -> str:
        """تجهيز النص العربي للطباعة"""
        try:
            reshaped_text = arabic_reshaper.reshape(text)
            return get_display(reshaped_text)
        except Exception as e:
            self.logger.error(f"خطأ في تجهيز النص العربي: {str(e)}")
            return text

    def _add_header(self, c: canvas.Canvas, title: str):
        """إضافة ترويسة التقرير"""
        try:
            # شعار الشركة
            logo_path = os.path.join(SYSTEM_CONFIG['RESOURCES_DIR'], 'images', 'logo.png')
            if os.path.exists(logo_path):
                c.drawImage(logo_path, 50, A4[1] - 120, width=100, height=100)

            # معلومات الشركة
            c.setFont('Arabic', 16)
            c.drawString(200, A4[1] - 50, self._prepare_arabic_text(SYSTEM_CONFIG['COMPANY_NAME']))
            c.setFont('Arabic', 12)
            c.drawString(200, A4[1] - 70, self._prepare_arabic_text(SYSTEM_CONFIG['COMPANY_ADDRESS']))
            c.drawString(200, A4[1] - 90, f"هاتف: {SYSTEM_CONFIG['COMPANY_PHONE']}")
            
            # عنوان التقرير
            c.setFont('Arabic', 18)
            c.drawString(250, A4[1] - 150, self._prepare_arabic_text(title))
            
            # التاريخ
            c.setFont('Arabic', 12)
            current_date = datetime.now().strftime('%Y/%m/%d')
            c.drawString(50, A4[1] - 150, f"التاريخ: {current_date}")
            
            # خط فاصل
            c.line(50, A4[1] - 170, A4[0] - 50, A4[1] - 170)
            
        except Exception as e:
            self.logger.error(f"خطأ في إضافة ترويسة التقرير: {str(e)}")

    def generate_salary_report(self, data: list, filename: str) -> bool:
        """إنشاء تقرير الرواتب"""
        try:
            c = canvas.Canvas(os.path.join(SYSTEM_CONFIG['REPORTS_DIR'], filename), pagesize=A4)
            self._add_header(c, "تقرير الرواتب الشهري")
            
            # محتوى التقرير
            y = A4[1] - 200
            c.setFont('Arabic', 12)
            
            # عناوين الأعمدة
            headers = ["الرقم", "الاسم", "الراتب الأساسي", "البدلات", "الخصومات", "الصافي"]
            x_positions = [500, 400, 300, 200, 100, 50]
            
            for i, header in enumerate(headers):
                c.drawString(x_positions[i], y, self._prepare_arabic_text(header))
            
            # البيانات
            y -= 30
            total = 0
            
            for row in data:
                if y < 50:  # صفحة جديدة
                    c.showPage()
                    self._add_header(c, "تقرير الرواتب الشهري - تابع")
                    y = A4[1] - 200
                
                c.drawString(500, y, str(row['employee_id']))
                c.drawString(400, y, self._prepare_arabic_text(row['name']))
                c.drawString(300, y, f"{row['basic_salary']:.2f}")
                c.drawString(200, y, f"{row['allowances']:.2f}")
                c.drawString(100, y, f"{row['deductions']:.2f}")
                c.drawString(50, y, f"{row['net_salary']:.2f}")
                
                total += row['net_salary']
                y -= 20
            
            # الإجمالي
            c.setFont('Arabic', 14)
            c.drawString(100, y - 30, f"إجمالي الرواتب: {total:.2f}")
            
            c.save()
            return True
            
        except Exception as e:
            self.logger.error(f"خطأ في إنشاء تقرير الرواتب: {str(e)}")
            return False 