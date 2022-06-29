class ExcelWriter:
    def __init__(self):
        self.wb = self.create_excel_workbook()
        self.ws = self.create_excel_worksheet()

        # try     : self.write_data()
        # except  : raise(Exception("Exception occured while writting data to an Excel file."))
        # finally : self.workbook.close()

    @property
    def excel_filename(self):
        """Generate filename with a timestamp for an Excel file."""
        dir = os.path.dirname(__file__)
        doc_name = doc.Title
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        return "{}/Excel/{}_Materials_{}.xlsx".format(dir, doc_name, timestamp)


    def create_excel_workbook(self):
        #type:() -> Workbook
        """Function to create an Excel Workbook."""

        # CHECK IF PATH EXISTS
        path_dir = os.path.dirname(self.excel_filename)
        if not os.path.exists(path_dir):
            os.makedirs(path_dir)
        workbook = Workbook(self.excel_filename)
        print('Created Excel Workbook: {}'.format(self.excel_filename))
        return workbook

    def create_excel_worksheet(self):
        #type:() -> Worksheet
        """Function to add a worksheet to the created self.workbook with its name derived from sheet_number
        :param sheet_number: str(sheet.SheetNumber)
        :return: Worksheet  """
        worksheet_name = 'Materials'
        worksheet = self.wb.add_worksheet(worksheet_name)
        return worksheet

    def write_data(self, data):
        """data - List of nested lists.
        data = [[1,2,3], [10,20,30]]
        1 | 2 | 3           Each nested list            represents a row and
        10| 20| 30          Each item in a nested list  represents a column"""
        for r, row in enumerate(data):
            for c, col in enumerate(row):
                self.ws.write(r, c, col)
        print('_' * 120)



# if __name__ == '__main__':
#     from xlsxwriter.workbook import Workbook, Worksheet
#
#     ExcelFile = ExcelWriter()
#     used_materials = []
#
#     excel_data = [[i] for i in used_materials]
#     ExcelFile.write_data(excel_data)
#
#
