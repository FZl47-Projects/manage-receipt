import os
import xlsxwriter

from django.conf import settings
from core.utils import gregorian_to_jalali


class Excel:

    @classmethod
    def perform_export_building(cls, building_obj) -> str:
        # TODO: maybe need to refactor
        file_name = f"{settings.EXPORT_ROOT_DIR}/export-building-{building_obj.id}.xlsx"
        export_file = os.path.join(settings.MEDIA_ROOT, file_name)
        workbook = xlsxwriter.Workbook(export_file)
        # add information
        # add title rows
        worksheet = workbook.add_worksheet('اطلاعات کلی')
        worksheet.write(0, 0, 'نام پروژه')
        worksheet.write(0, 1, 'نام ساختمان')
        worksheet.write(0, 2, 'درصد پیشرفت')
        worksheet.write(0, 3, 'تعداد کاربران شرکت کرده')
        worksheet.write(0, 4, 'وضعیت')
        worksheet.write(0, 5, 'مبلغ پرداخت شده')
        worksheet.write(0, 6, 'تعداد رسید ها')
        worksheet.write(0, 7, 'توضیحات')
        worksheet.write(0, 8, 'ادرس')
        # add data
        worksheet.write(2, 0, building_obj.project.name)
        worksheet.write(2, 1, building_obj.name)
        worksheet.write(2, 2, building_obj.progress_percentage)
        worksheet.write(2, 3, building_obj.get_users().count())
        worksheet.write(2, 4, 'فعال' if building_obj.is_active else 'غیر فعال')
        worksheet.write(2, 5, building_obj.get_payments())
        worksheet.write(2, 6, building_obj.get_receipts().count())
        worksheet.write(2, 7, building_obj.description)
        worksheet.write(2, 8, building_obj.address)
        # add receipts
        # add title rows
        worksheet = workbook.add_worksheet('رسید ها')
        worksheet.write(0, 0, 'کد رهگیری')
        worksheet.write(0, 1, 'کاربر')
        worksheet.write(0, 2, 'مبلغ')
        worksheet.write(0, 3, 'امتیاز')
        worksheet.write(0, 4, 'ضریب امتیاز')
        worksheet.write(0, 5, 'تاریخ ثبت')
        worksheet.write(0, 6, 'تاریخ واریز')
        worksheet.write(0, 7, 'نام واریز کننده')
        worksheet.write(0, 8, 'نام بانک')
        worksheet.write(0, 9, 'توضیحات کاربر')
        worksheet.write(0, 10, 'توضیحات مدیر')
        worksheet.write(0, 11, 'ادرس عکس رسید')
        row = 2
        # add data
        for receipt in building_obj.get_receipts():
            worksheet.write(row, 0, receipt.tracking_code)
            worksheet.write(row, 1, f"{receipt.user.get_full_name()}|{receipt.user.get_raw_phonenumber()}")
            worksheet.write(row, 2, receipt.amount)
            worksheet.write(row, 3, receipt.get_score())
            worksheet.write(row, 4, receipt.ratio_score)
            creation_time = receipt.created_at
            deposit_time = receipt.deposit_datetime
            worksheet.write(row, 5, gregorian_to_jalali(creation_time.year, creation_time.month, creation_time.day))
            worksheet.write(row, 6,
                            f"{gregorian_to_jalali(deposit_time.year, deposit_time.month, deposit_time.day)}({receipt.get_deposit_timepast()})")
            worksheet.write(row, 7, receipt.depositor_name)
            worksheet.write(row, 8, receipt.bank_name)
            worksheet.write(row, 9, receipt.description)
            worksheet.write(row, 10, receipt.note)
            worksheet.write(row, 11, receipt.get_picture_full_url())
            row += 1
        # add users
        # add title rows
        worksheet = workbook.add_worksheet('کاربران')
        worksheet.write(0, 0, 'نام و نام خانوادگی')
        worksheet.write(0, 1, 'شماره همراه')
        worksheet.write(0, 2, 'مبلغ پرداخت کرده کل')
        worksheet.write(0, 3, 'امتیاز کل')
        row = 2
        # add data
        for user in building_obj.get_users():
            worksheet.write(row, 0, user.get_full_name())
            worksheet.write(row, 1, user.get_raw_phonenumber())
            worksheet.write(row, 2, building_obj.get_building_payments_user(user))
            worksheet.write(row, 3, building_obj.get_building_score_user(user))
            row += 1
        workbook.close()
        return file_name
