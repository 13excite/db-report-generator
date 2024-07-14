import argparse
import glob
import os
import sys

from config import config
from excel.writer import ExcelWriter
from parser.pdf import PdfReportParser


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
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

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
            # reset the result list and parse the pdf file
            pdf_parser.result = []
            pdf_parser.parse()

        payments_by_category = result_by_category(pdf_parser.result)
        report_month = os.path.basename(report_file).split('.')[0]
        e_writer.write(payments_by_category, report_month)


if __name__ == "__main__":
    main()
