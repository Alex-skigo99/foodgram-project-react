import io

# import csv
# import openpyxl
from rest_framework import renderers

HEADER = "список ингредиентов для покупки"
# HEADER_XLS = ["name", "measurement_unit", "amount"]


class TextIngredientRenderer(renderers.BaseRenderer):
    media_type = "text/plain"
    format = "txt"

    def render(self, data, accepted_media_type=None, renderer_context=None):
        text_buffer = io.StringIO()
        text_buffer.write(HEADER + "\n" * 2)
        for ingredient in data:
            text_buffer.write(
                " ".join(str(sd) for sd in list(ingredient.values())) + "\n"
            )
        return text_buffer.getvalue()


# class ExcelIngredientsRenderer(renderers.BaseRenderer):
#     media_type = "application/vnd.ms-excel"
#     format = "xls"

#     def render(self, data, accepted_media_type=None, renderer_context=None):
#         workbook = openpyxl.Workbook()
#         buffer = io.BytesIO()
#         worksheet = workbook.active
#         worksheet.append(HEADER_XLS)
#         for ingredient in data:
#             worksheet.append(list(ingredient.values()))
#         workbook.save(buffer)
#         return buffer.getvalue()
