import openpyxl


class ExcelManager:
    def __init__(self, file_path, mode):
        self.file_path = file_path
        self.mode = mode

    def __enter__(self):
        if self.mode == "r" and self.file_path:
            self.wb = openpyxl.load_workbook(self.file_path, read_only=True)
        elif self.mode == "w" and self.file_path:
            self.wb = openpyxl.Workbook()
        else:
            raise ValueError("参数错误")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.mode == "w":
            self.wb.save(self.file_path)
        self.wb.close()
        del self.wb

    def _get_sheet_names(self):
        """
            返回工作簿中所有工作表的名称列表
        :return: 列表名称
        """
        return self.wb.sheetnames

    def _get_sheet_by_name(self, name):
        """
            通过名称获取工作表。

        :param name: 工作表名称
        :return: 对应的工作表对象
        """
        return self.wb[name]

    def create_sheet(self, name, index=None):
        """
            创建新的工作表并添加到工作簿中。

        :param name: 新工作表的名称
        :param index: 可选，新工作表在工作簿中的位置索引。如果不指定，则添加到末尾。
        :return: 新创建的工作表对象
        """
        return self.wb.create_sheet(title=name, index=index)

    def delete_sheet(self, name_or_index):
        """
            删除指定的工作表。

        :param name_or_index: 要删除的工作表的名称或索引
        """
        self.wb.remove(self._get_sheet_by_name(name_or_index))

    def read_sheet_data(self, sheet_name=None):
        """
            读取指定excel的数据
        :param sheet_name: 工作表名称如果没有则是默认第一个
        :return: 列表嵌套字典
        """
        if sheet_name:
            sheet = self._get_sheet_by_name(sheet_name)
        else:
            sheet = self.wb.active
        headers = [cell.value.strip() for cell in sheet[1]]
        result = []
        for row in sheet.iter_rows(min_row=2, values_only=True):
            result.append(dict(zip(headers, row)))
        return result

    def read_all_sheet_data(self):
        """
            读取所有工作表的数据
        :return: 列表嵌套字典
        """
        result = []
        for sheet_name in self._get_sheet_names():
            result.append({sheet_name: self.read_sheet_data(sheet_name)})
        return result

    def write_sheet_data(self, data, sheet_name=None):
        """
            向指定工作表写入数据
        :param sheet_name:
        :param data: [["列头1","列头2"],["数据1","数据2"]]
        :return:
        """
        if sheet_name:
            sheet = self._get_sheet_by_name(sheet_name)
        else:
            sheet = self.wb.active
        for row in data:
            sheet.append(row)

    def write_sheet_data2(self, data, sheet_name=None):
        """
            向指定工作表写入数据
        :param sheet_name: 指定的工作表名称
        :param data: [{'列头1': '数据1', '列头2': '数据2'}, {'列头1': '数据3', '列头2': '数据4'}]
        :return:
        """
        if sheet_name:
            sheet = self._get_sheet_by_name(sheet_name)
        else:
            sheet = self.wb.active

        # 处理列头
        column_keys = data[0].keys()  # 获取第一个字典的所有键作为列头
        sheet.append(list(column_keys))  # 将列头写入第一行

        # 写入数据
        for row_dict in data:
            row_values = [row_dict[key] for key in column_keys]  # 根据列头顺序获取每个字典的值
            sheet.append(row_values)  # 将当前行数据写入工作表


if __name__ == '__main__':
    # 写数据1
    # data1 = [["列头1", "列头2"], ["数据1", "数据2"]]
    # with ExcelManager("test1.xlsx", "w") as excel:
    #     excel.write_sheet_data(data1)

    # 写数据2
    data2 = [{'列头1': '数据1', '列头2': '数据2'}, {'列头1': '数据3', '列头2': '数据4'}]
    with ExcelManager("test2.xlsx", "w") as excel:
        excel.write_sheet_data2(data2)

    # 读数据
    # with ExcelManager("test1.xlsx", "r") as excel:
    #     data = excel.read_sheet_data()
    #     print(data)
