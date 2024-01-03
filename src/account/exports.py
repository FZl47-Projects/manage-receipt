import os
import xlsxwriter
from django.conf import settings
from core.utils import random_str


class Excel:

    @classmethod
    def perform_export_users(cls, users) -> str:
        # TODO: maybe need to refactor
        file_name = f"{settings.EXPORT_ROOT_DIR}/export-building-{random_str(5)}.xlsx"
        export_file = os.path.join(settings.MEDIA_ROOT, file_name)
        workbook = xlsxwriter.Workbook(export_file)
        # add users
        # add title rows
        worksheet = workbook.add_worksheet('لیست کاربران عادی')
        worksheet.write(0, 0, 'نام')
        worksheet.write(0, 1, 'نام خانوادگی')
        worksheet.write(0, 2, 'شماره همراه')
        worksheet.write(0, 3, 'ایمیل')
        worksheet.write(0, 4, 'وضعیت حساب کاربری')
        worksheet.write(0, 5, 'وضعیت شماره همراه')
        worksheet.write(0, 6, 'تعداد رسید ها')
        worksheet.write(0, 7, 'امتیاز کل')
        worksheet.write(0, 8, 'پرداخت کل')
        worksheet.write(0, 9, 'ساختمان های باز')
        row = 2
        # add data
        for user in users:
            available_buildings = '|'.join(user.get_available_building_names())
            worksheet.write(row, 0, user.first_name)
            worksheet.write(row, 1, user.last_name)
            worksheet.write(row, 2, user.get_raw_phonenumber())
            worksheet.write(row, 3, user.get_email())
            worksheet.write(row, 4, 'فعال' if user.is_active else 'غیر فعال')
            worksheet.write(row, 5, 'تایید شده' if user.is_phonenumber_confirmed else 'تایید نشده')
            worksheet.write(row, 6, user.get_receipts().count())
            worksheet.write(row, 7, user.get_scores())
            worksheet.write(row, 8, user.get_payments())
            worksheet.write(row, 9, available_buildings)
            row += 1
        workbook.close()
        return file_name
