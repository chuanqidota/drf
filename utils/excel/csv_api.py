import csv
import traceback


class CSVManager:
    def __init__(self, file_path):
        """
            操作csv
        :param file_path:
        """
        self.file_path = file_path

    def read_csv(self):
        """
            读数据
        :return: [{}]
        """
        try:
            with open(self.file_path, 'r', newline='') as file:
                reader = csv.reader(file)
                headers = next(reader)  # 获取第一行作为列名（键）
                data = [{header: value for header, value in zip(headers, row)} for row in reader]
            return data
        except Exception as e:
            print(traceback.format_exc(), repr(e))
            return []

    def write_csv(self, data):
        """
            写数据
        :param data: [[],[]]
        :return:
        """
        try:
            with open(self.file_path, "w", newline='') as file:
                writer = csv.writer(file)
                writer.writerows(data)
                return True
        except Exception as e:
            print(traceback.format_exc(), repr(e))
            return False


if __name__ == '__main__':
    csv_manager = CSVManager("test.csv")
    _data = [["列头1", "列头2"], ["数据1", "数据2"], ["数据11", "数据22"]]
    csv_manager.write_csv(_data)
    print(csv_manager.read_csv())
