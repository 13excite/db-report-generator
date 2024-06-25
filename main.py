import argparse
import glob
import io
import os
import re
import sys

import PyPDF2
import xlsxwriter

from config import config

from dataclasses import dataclass
from typing import List


@dataclass
class PaymentData:
    type_text: str
    card_payment: bool
    sepa_payment: bool
    bargeld_payment: bool


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
        self.__excel_writer(payments_by_category, sheet_name)

    def __excel_writer(self, payments_by_category: dict, sheet_name) -> None:
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


class PdfReportParser:

    def __init__(self) -> None:
        # self.result_list = []
        self.__reader: PyPDF2.PdfReader = None
        self.__payment_data: PaymentData = None

    # read pdf file
    def read_pdf(self, file_stream: io.BufferedReader):
        self.__reader = PyPDF2.PdfReader(file_stream)

    def parse(self, result_list: List):
        for page_num, _ in enumerate(self.__reader.pages):

            page1 = self.__reader.pages[page_num]
            pdf_data = page1.extract_text()

            # -1 means that lines with payment information haven't yet read
            counter = -1

            # tmp_list contains temporary data that will be inserted into the result_list
            tmp_list = []
            for line in pdf_data.split('\n'):
                if counter < 0:
                    # means that the line with payment information will be the next
                    if line == "Haben Soll Vorgang Valuta Buchung":
                        counter = 0
                else:
                    if line.startswith("IBAN von Seite Auszug"):
                        counter = -1
                        continue
                    # debit always starts with "-", for example -20.0  Kartenzahlung
                    # also we need to skip line with - and alphabetic symbols
                    if line.startswith("-") and not counter and (
                        not re.match(r"^-[A-Z]+", line)
                    ):
                        # sometimes the string is read as simply -
                        # needs to skip it
                        if line == "-":
                            continue
                        amount_and_type = line.split(' ')

                        # 0 index is amount
                        amount = self.__amount_fmt(amount_and_type[0])

                        # 1 index is payment type: SEPA, Bar or Kartenzahlung
                        payment_type = amount_and_type[1]
                        self.__payment_data = self.__get_payment_type(
                            payment_type)

                        tmp_list.extend(
                            [self.__payment_data.type_text, amount])
                        counter += 1
                        # next iteration
                        continue
                    if (self.__payment_data.card_payment or
                            self.__payment_data.bargeld_payment) and counter:
                        if counter == 1:
                            # unneeded info
                            counter += 1
                            # next iteration
                            continue
                        # line with date for the card info
                        if counter == 2:
                            tmp_list.append(self.__date_fmt(line))
                            counter += 1
                            # next iteration
                            continue
                        # duplication
                        if counter == 3:
                            # just year, skip
                            counter += 1
                            # next iteration
                            continue
                        # payment name
                        if counter == 4:
                            tmp_list.append(line)
                            # append to result
                            result_list.append(tmp_list)
                            # and clear the counter and tmp_list
                            tmp_list = []
                            counter = 0
                            # next iteration
                            continue
                    if self.__payment_data.sepa_payment and counter:
                        # payment name
                        if counter == 1:
                            tmp_list.append(line)
                            counter += 1
                            # next iteration
                            continue
                        # line with date for the SEPA
                        if counter == 2:
                            # append the date
                            tmp_list.append(self.__date_fmt(line))
                            # formatting list
                            tmp_list[2], tmp_list[3] = tmp_list[3], tmp_list[2]
                            # append tmp to the result
                            result_list.append(tmp_list)
                            # and clear the counter and tmp_list
                            tmp_list = []
                            counter = 0
                            # next iteration
                            continue

    def __get_payment_type(self, payment_type: str) -> PaymentData:
        sepa_payment = self.__is_sepa(payment_type)
        card_payment = self.__is_card(payment_type)
        bargeld_payment = self.__is_bargeld(payment_type)

        pyment_type_str = "Unknown"
        if card_payment:
            pyment_type_str = "Karten"
        elif sepa_payment:
            pyment_type_str = "SEPA"
        elif bargeld_payment:
            pyment_type_str = "Bargeldauszahlung"

        return PaymentData(pyment_type_str, card_payment, sepa_payment, bargeld_payment)

    # check if the payment type is card payment

    @staticmethod
    def __is_card(type_string):
        if type_string.startswith("Kartenz"):
            return True
        return False

    # check if the payment type is cash withdrawal
    @staticmethod
    def __is_bargeld(type_string):
        if type_string.startswith("Bargeld"):
            return True
        return False

    # check if the payment type is SEPA transaction
    @staticmethod
    def __is_sepa(type_string):
        if type_string.startswith("SEPA"):
            return True
        return False

    # format amount from '1.234,00' to '1234.00
    @staticmethod
    def __amount_fmt(amount: str):
        if ("," in amount) and ("." in amount):
            r = amount.replace(".", "").replace(",", ".")
            return float(r)
        return float(amount.replace(',', '.'))

    # format date from '202304.12.' to '2023.04.12'
    @staticmethod
    def __date_fmt(date_str: str):
        month = date_str.split(".")[1]
        year = date_str[:4]
        day = date_str[4:6]
        "".replace(',', '.')
        return f"{year}.{month}.{day}"


# extract date from the filename
def extract_date(filename):
    # Remove the .pdf extension
    month_year = filename[:-4]
    # Split month and year
    month, year = month_year[:-4], month_year[-4:]
    # Convert month to number
    month_number = config.MONTH_TO_NUMBER[month.lower()]
    return (int(year), month_number)


# get list of report files and sort them by month and year
def get_db_report_names(report_dir: str) -> list:
    file_pathes = glob.glob(f"{report_dir}/*.pdf")
    unorderd_files = []
    for path in file_pathes:
        unorderd_files.append(os.path.basename(path))

    sorted_file_list = sorted(unorderd_files, key=extract_date)

    for idx, _ in enumerate(sorted_file_list):
        sorted_file_list[idx] = os.path.join(report_dir, sorted_file_list[idx])

    return sorted_file_list


def result_by_category(result_list):
    result_map = {}
    for lst in result_list:
        # idx 3 is name of payments

        # by default payment category is unknown
        # set False if shop_prefix will be found in the name of payment
        unknown_cat = True
        prefix_found = False
        for cat_type, values in config.SHOP_TYPES.items():
            if prefix_found:
                # break cat_type, values in shop_types.items() LOOP
                break
            # iterate by each shop pfx
            for shop_prefix in values:
                if shop_prefix.lower() in lst[3].lower():
                    if not result_map.get(cat_type, ''):
                        result_map[cat_type] = [lst]
                        unknown_cat = False
                        prefix_found = True
                        # break "shop_prefix in values" LOOP
                        break

                    result_map[cat_type].append(lst)
                    unknown_cat = False
                    prefix_found = True
                    # break shop_prefix in values LOOP
                    break

        if unknown_cat:
            if not result_map.get(config.UNKNOWN_CATEGORY_NAME, ''):
                result_map[config.UNKNOWN_CATEGORY_NAME] = [lst]
            else:
                result_map[config.UNKNOWN_CATEGORY_NAME].append(lst)
            unknown_cat = True
            continue
    return result_map


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-o', '--out', type=str,
                        default="db_report.xlsx",
                        help='usage (-o|--out) output file name',
                        required=False
                        )
    parser.add_argument('-i', '--input', type=str,
                        default="./reports",
                        help='usage (-i|--input) input folder with pdf reports',
                        required=False
                        )
    args = parser.parse_args()

    # check if the input folder exists
    if not os.path.exists(args.input):
        sys.exit(f"ERROR: Directory {args.input} doesn't exist")

    e_writer = ExcelWriter(args.out)
    pdf_parser = PdfReportParser()

    for report_file in get_db_report_names(args.input):
        with open(report_file, "rb") as file:

            pdf_parser.read_pdf(file)

            # TODO: use result_list as a class attribute
            result_list = []
            pdf_parser.parse(result_list)

        payments_by_category = result_by_category(result_list)
        report_month = os.path.basename(report_file).split('.')[0]
        e_writer.write(payments_by_category, report_month)


if __name__ == "__main__":
    main()
