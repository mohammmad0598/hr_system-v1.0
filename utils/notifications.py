# -*- coding: utf-8 -*-
from twilio.rest import Client
from config.settings import SYSTEM_CONFIG
import logging
from datetime import datetime

class NotificationManager:
    def __init__(self):
        self.logger = logging.getLogger('NotificationManager')
        self.twilio_enabled = False
        self.setup_twilio()
    
    def setup_twilio(self):
        """إعداد خدمة Twilio"""
        try:
            if all(key in SYSTEM_CONFIG for key in ['TWILIO_SID', 'TWILIO_TOKEN', 'TWILIO_PHONE']):
                self.client = Client(
                    SYSTEM_CONFIG['TWILIO_SID'],
                    SYSTEM_CONFIG['TWILIO_TOKEN']
                )
                self.from_number = SYSTEM_CONFIG['TWILIO_PHONE']
                self.twilio_enabled = True
            else:
                self.logger.warning("لم يتم تكوين خدمة Twilio")
        except Exception as e:
            self.logger.error(f"خطأ في إعداد Twilio: {str(e)}")
    
    def send_sms(self, to_number: str, message: str) -> bool:
        """إرسال رسالة نصية"""
        if not self.twilio_enabled:
            self.logger.warning("خدمة Twilio غير مفعلة")
            return False
            
        try:
            message = self.client.messages.create(
                body=message,
                from_=self.from_number,
                to=to_number
            )
            self.logger.info(f"تم إرسال الرسالة: {message.sid}")
            return True
        except Exception as e:
            self.logger.error(f"خطأ في إرسال الرسالة: {str(e)}")
            return False
    
    def notify_late_attendance(self, employee_data: dict) -> bool:
        """إرسال إشعار تأخير"""
        message = f"""
        السلام عليكم {employee_data['name']}،
        نود إعلامكم بتسجيل تأخير في الحضور ليوم {datetime.now().strftime('%Y-%m-%d')}
        وقت الحضور: {employee_data['check_in']}
        الرجاء الالتزام بمواعيد العمل.
        """
        return self.send_sms(employee_data['phone'], message)
    
    def notify_salary_transfer(self, employee_data: dict) -> bool:
        """إرسال إشعار تحويل الراتب"""
        message = f"""
        السلام عليكم {employee_data['name']}،
        تم إيداع راتب شهر {employee_data['month']}/{employee_data['year']}
        المبلغ: {employee_data['net_salary']} ريال
        """
        return self.send_sms(employee_data['phone'], message)
    
    def notify_evaluation(self, employee_data: dict) -> bool:
        """إرسال إشعار التقييم"""
        message = f"""
        السلام عليكم {employee_data['name']}،
        تم إضافة تقييم جديد بتاريخ {datetime.now().strftime('%Y-%m-%d')}
        الدرجة: {employee_data['total_score']}%
        """
        return self.send_sms(employee_data['phone'], message)
    
    def notify_leave_approval(self, employee_data: dict) -> bool:
        """إرسال إشعار الموافقة على الإجازة"""
        message = f"""
        السلام عليكم {employee_data['name']}،
        تمت الموافقة على طلب إجازتكم
        من: {employee_data['start_date']}
        إلى: {employee_data['end_date']}
        نوع الإجازة: {employee_data['leave_type']}
        """
        return self.send_sms(employee_data['phone'], message)