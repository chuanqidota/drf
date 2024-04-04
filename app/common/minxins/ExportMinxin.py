from io import BytesIO

from django.http import HttpResponse
from django.utils.timezone import now
from openpyxl.workbook import Workbook


class ExportMix(object):
    """
    导出数据
    """
    file_name = None  # 最好不要包含中文字符，可能会导致浏览器不能自动下载
    export_serializer_class = None  # 可以自定义导出序列化类，加快导出速度
    xlsx_header_to_fields = None  # {'f1':'字段1', ’f2‘: '字段2'}, f1, f2, ...为序列化类中的字段名

    def get_export_serializer_class(self):
        return self.export_serializer_class or self.get_serializer_class()

    def get_export_serializer(self, *args, **kwargs):
        serializer_class = self.get_export_serializer_class()
        kwargs.setdefault('context', self.get_serializer_context())
        return serializer_class(*args, **kwargs)

    def response_xlsx(self):
        """
        返回导出文件
        """

        file_name = self.get_file_name()
        wb = Workbook()
        ws = wb.active

        if not hasattr(self, 'get_export_data'):
            qs = self.filter_queryset(self.get_queryset())
            serializer = self.get_export_serializer(qs, many=True)
            data = serializer.data

            # append header
            xlsx_fields = None
            if self.xlsx_header_to_fields:
                ws.append(list(self.xlsx_header_to_fields.values()))
                xlsx_fields = self.xlsx_header_to_fields.keys()

            for dat in data:
                if not self.xlsx_header_to_fields:
                    ws.append(list(dat.values()))
                else:
                    ws.append([dat.get(f) for f in xlsx_fields])
        else:
            data, headers = self.get_export_data()
            ws.append(headers)
            for dat in data:
                ws.append(dat)

        file_stream = BytesIO()
        wb.save(file_stream)
        response = HttpResponse(content=file_stream.getvalue(), content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename=%s' % file_name
        return response

    def get_file_name(self):
        """
        返回导出文件名
        """
        dt = now().strftime('%Y%m%d%H%M%S')
        return '%s-%s.xlsx' % (self.file_name, dt)
