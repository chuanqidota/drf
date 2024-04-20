import pandas as pd


class ExcelProcessor:
    def __init__(self, file_path, sheet_name="Sheet1"):
        """
            操作excel
        :param file_path: 文件路径
        :param sheet_name: sheet名称
        """
        self.file_path = file_path
        self.sheet_name = sheet_name

    def read_excel(self):
        """
            读取数据
        :return: [{},{}]
        """
        df = pd.read_excel(self.file_path, sheet_name=self.sheet_name)
        return df.to_dict("records")

    def write_excel(self, data):
        """
            写数据
        :param data: [[],[]]
        :return:
        """
        df = pd.DataFrame(data)
        df.to_excel(self.file_path, self.sheet_name, index=False, header=False)


if __name__ == '__main__':
    _data = [["列头1", "列头2"], ["数据1", "数据2"]]
    excel_processor = ExcelProcessor('test.xlsx', 'Sheet')

    excel_processor.write_excel(_data)
    print(excel_processor.read_excel())
