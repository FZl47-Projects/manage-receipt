import os
import xlsxwriter
from django.conf import settings


class Excel:

    @classmethod
    def perform_export_question(cls, question_obj) -> str:
        file_name = f"{settings.EXPORT_ROOT_DIR}/export-question-{question_obj.id}-{question_obj.building.id}.xlsx"
        export_file = os.path.join(settings.MEDIA_ROOT, file_name)
        workbook = xlsxwriter.Workbook(export_file)
        # add information
        # add title rows
        worksheet = workbook.add_worksheet('اطلاعات')
        worksheet.write(0, 0, 'عنوان پرسش')
        worksheet.write(0, 1, 'نام ساختمان')
        # add data
        worksheet.write(2, 0, question_obj.title)
        worksheet.write(2, 1, question_obj.building.name)
        # add results
        # add title rows
        worksheet = workbook.add_worksheet('نتایج')
        worksheet.write(0, 0, 'مشخصات کاربر')
        worksheet.write(0, 1, 'جواب کاربر')
        row = 2
        # add data
        for answer in question_obj.get_answers():
            # user info
            worksheet.write(row, 0, f"{answer.user.get_full_name()}|{answer.user.get_raw_phonenumber()}")
            # user answer
            worksheet.write(row, 1, answer.answer)
            row += 1
        # add answer percentages
        # add title rows
        worksheet = workbook.add_worksheet('درصد نظرسنجی')
        worksheet.write(0, 0, '(گزینه 1){}'.format(question_obj.option_1))
        worksheet.write(0, 1, '(گزینه 2){}'.format(question_obj.option_2))
        worksheet.write(0, 2, '(گزینه 3){}'.format(question_obj.option_3))
        worksheet.write(0, 3, '(گزینه 4){}'.format(question_obj.option_4))
        # set answer percentages
        worksheet.write(1, 0, '%{}'.format(question_obj.get_answer_percentage(question_obj.option_1)))
        worksheet.write(1, 1, '%{}'.format(question_obj.get_answer_percentage(question_obj.option_2)))
        worksheet.write(1, 2, '%{}'.format(question_obj.get_answer_percentage(question_obj.option_3)))
        worksheet.write(1, 3, '%{}'.format(question_obj.get_answer_percentage(question_obj.option_4)))

        workbook.close()
        return file_name
