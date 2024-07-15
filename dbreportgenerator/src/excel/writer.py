import xlsxwriter


class ExcelWriter:
    merge_excel_style = {
        "bold": 1,
        "border": 1,
        "align": "center",
        "valign": "vcenter",
        "fg_color": "yellow",
    }
    total_excel_style = {
        "bold": 1,
        "border": 1,
        "align": "center",
        "valign": "vcenter",
        "fg_color": "red",
    }

    def __init__(self, file_name: str,) -> None:
        self.workbook = xlsxwriter.Workbook(file_name)

    def __del__(self) -> None:
        self.workbook.close()

    def write(self, payments_by_category: dict, sheet_name) -> None:
        self._excel_writer(payments_by_category, sheet_name)

    def _excel_writer(self, payments_by_category: dict, sheet_name) -> None:
        worksheet = self.workbook.add_worksheet(sheet_name)
        # payments_by_category values indexes:
        # idx_payment_type = 0
        # idx_amount = 1
        # idx_date = 2
        # idx_payment_name = 3

        worksheet.set_column(0, 4, 30)
        merge_format = self.workbook.add_format(self.merge_excel_style)
        total_format = self.workbook.add_format(self.total_excel_style)

        row_idx = 0
        total_by_month = 0
        for category, values in payments_by_category.items():
            worksheet.merge_range(row_idx, 0, row_idx, 4,
                                  category, merge_format)
            row_idx += 1

            total_by_category = 0
            for data in values:
                worksheet.write(row_idx, 0, data[2])
                worksheet.write(row_idx, 1, data[1])
                worksheet.write(row_idx, 2, data[3])
                worksheet.write(row_idx, 3, data[0])
                total_by_category += data[1]
                total_by_month += data[1]
                row_idx += 1

            worksheet.set_row(row_idx, height=10, cell_format=total_format)
            worksheet.write(row_idx, 0, f"Total by {category}")
            worksheet.write(row_idx, 1, total_by_category)
            # and switch to the next line for write the category type header
            row_idx += 1

        # switch to a bit below and write total amount of money spent
        row_idx += 2
        worksheet.set_row(row_idx, height=10, cell_format=total_format)
        worksheet.write(row_idx, 0, "Total by month")
        worksheet.write(row_idx, 1, total_by_month)