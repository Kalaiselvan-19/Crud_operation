import xlsxwriter


class Writter:
    def __int__(self):
        self.workbook = None
        self.worksheet = None

    def create(self, name):
        self.workbook = xlsxwriter.Workbook(name)
        self.worksheet = self.workbook.add_worksheet()

    def write(self, row, col, data):
        self.worksheet.write(row, col, data)

    def close(self):
        self.workbook.close()
