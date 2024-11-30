from database.db_handler import DatabaseHandler
import logging
from datetime import datetime
from utils.report_generator import ReportGenerator
from config.settings import SYSTEM_CONFIG

class SalaryManager:
    def __init__(self):
        self.db = DatabaseHandler()
        self.logger = logging.getLogger('SalaryManager')
        self.report_generator = ReportGenerator()
    
    def get_departments(self) -> list:
        """جلب قائمة الأقسام"""
        try:
            query = "SELECT DISTINCT department FROM employees WHERE status = 'نشط'"
            results = self.db.fetch_all(query)
            return [row[0] for row in results if row[0]]
        except Exception as e:
            self.logger.error(f"خطأ في جلب الأقسام: {str(e)}")
            return []

    def calculate_monthly_salaries(self, month: int, year: int, department: str = None) -> list:
        """احتساب رواتب الشهر"""
        try:
            # بناء الاستعلام الأساسي
            query = """
                SELECT 
                    e.id,
                    e.name,
                    e.basic_salary,
                    e.department,
                    COALESCE(a.housing_allowance, 0) as housing_allowance,
                    COALESCE(a.transport_allowance, 0) as transport_allowance
                FROM employees e
                LEFT JOIN employee_allowances a ON a.employee_id = e.id
                WHERE e.status = 'نشط'
            """
            
            params = []
            if department:
                query += " AND e.department = ?"
                params.append(department)
                
            results = self.db.fetch_all(query, tuple(params) if params else None)
            salaries = []
            
            for emp in results:
                # احتساب البدلات والخصومات
                allowances = emp[4] + emp[5]  # housing + transport
                deductions = self._calculate_deductions(emp[0], month, year)
                
                # احتساب صافي الراتب
                net_salary = emp[2] + allowances - deductions
                
                salaries.append({
                    'employee_id': emp[0],
                    'name': emp[1],
                    'basic_salary': emp[2],
                    'department': emp[3],
                    'allowances': allowances,
                    'deductions': deductions,
                    'net_salary': net_salary,
                    'date': datetime.now().date(),
                    'status': 'معلق'
                })
            
            return salaries
            
        except Exception as e:
            self.logger.error(f"خطأ في اح��ساب الرواتب: {str(e)}")
            return []

    def approve_salaries(self, month: int, year: int) -> bool:
        """اعتماد رواتب الشهر"""
        try:
            # تحديث حالة الرواتب إلى معتمد
            query = """
                UPDATE salaries 
                SET status = 'معتمد', 
                    approved_date = ?
                WHERE MONTH(date) = ? 
                AND YEAR(date) = ?
                AND status = 'معلق'
            """
            return self.db.execute(query, (
                datetime.now(),
                month,
                year
            ))
            
        except Exception as e:
            self.logger.error(f"خطأ في اعتماد الرواتب: {str(e)}")
            return False

    def export_salary_report(self, month: int, year: int) -> bool:
        """تصدير تقرير الرواتب"""
        try:
            # جلب بيانات الرواتب
            salaries = self.calculate_monthly_salaries(month, year)
            
            # إنشاء التقرير
            filename = f"salary_report_{year}_{month:02d}.pdf"
            return self.report_generator.generate_salary_report(salaries, filename)
            
        except Exception as e:
            self.logger.error(f"خطأ في تصدير تقرير الرواتب: {str(e)}")
            return False

    def _calculate_deductions(self, employee_id: int, month: int, year: int) -> float:
        """حساب الخصومات"""
        try:
            # حساب خصومات الغياب
            query = """
                SELECT COUNT(*) 
                FROM attendance 
                WHERE employee_id = ? 
                AND MONTH(date) = ? 
                AND YEAR(date) = ?
                AND status = 'غائب'
            """
            result = self.db.fetch_one(query, (employee_id, month, year))
            absence_days = result[0] if result else 0
            
            # جلب الراتب اليومي
            query = "SELECT basic_salary FROM employees WHERE id = ?"
            result = self.db.fetch_one(query, (employee_id,))
            daily_salary = (result[0] / 30) if result else 0
            
            absence_deductions = absence_days * daily_salary

            # جلب الخصومات الأخرى
            query = """
                SELECT SUM(amount) 
                FROM deductions 
                WHERE employee_id = ? 
                AND MONTH(date) = ? 
                AND YEAR(date) = ?
            """
            result = self.db.fetch_one(query, (employee_id, month, year))
            other_deductions = result[0] if result and result[0] else 0

            return absence_deductions + other_deductions

        except Exception as e:
            self.logger.error(f"خطأ في حساب الخصومات: {str(e)}")
            return 0.0
