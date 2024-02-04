import PyPDF2
import xlsxwriter


UNKNOWN_CATEGORY_NAME = "UNKNOWN"

shops_type = {
    "FOOD_SHOP": [
        "ALDI",
        "REWE",
        "Kaufland",
        "Edeka",
        "Metro",
        "kliver",
        "mixmarkt",
        "penny",
        "TEGUTSAGT",
        "lemberg",
        "ROSSMANN",
        "JACQUES",
    ],
    "RENT": [
        "NorbertBeran",
        "VATTENFALLE",
        "Vodafone",
        "Immobilien",
        "GCreGetsafe",
    ],
    "Education": [
        "Volkshochschule",
        "Linuxf",
    ],
    "CAFE": [
        "Backerei"
        "B.ckerei",
        "Kulturbrauerei",
        "Cafe",
        "KAMPS",
        "Restaurant",
        "Liebesbrot",
    ],
    "TRAVEL": [
        "DBVertriebGmbH",
        "BerlinerVerkehrsbetriebe",
        "Booking",
        "AUSTRIAN",  # austrian airlines
        "RYANAIR",
        "MALLORCA",
        "TAXI",
        "Hotel"
    ],
    "Amazon": [
        "Amazon",
    ],
    "InternetService": [
        "Spotify",
        "Blizzard",
    ]
}


def is_card(type_string):
    if type_string.startswith("Kartenz"):
        return True
    return False


def is_bargeld(type_string):
    if type_string.startswith("Bargeld"):
        return True
    return False


def is_sepa(type_string):
    if type_string.startswith("SEPA"):
        return True
    return False


def amount_fmt(amount: str):
    if ("," in amount) and ("." in amount):
        r = amount.replace(".", "").replace(",", ".")
        return float(r)
    return float(amount.replace(',', '.'))


def date_fmt(date_str: str):
    # 202304.12.

    month = date_str.split(".")[1]
    year = date_str[:4]
    day = date_str[4:6]
    "".replace(',', '.')
    return f"{year}.{month}.{day}"


def result_by_category(result_list):
    result_map = {}
    for lst in result_list:
        # idx 3 is name of payments

        # by default payment category is unknown
        # set False if shop_prefix will be found in the name of payment
        unknown_cat = True
        prefix_found = False
        for cat_type, values in shops_type.items():
            if prefix_found:
                # break cat_type, values in shops_type.items() LOOP
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
            if not result_map.get(UNKNOWN_CATEGORY_NAME, ''):
                result_map[UNKNOWN_CATEGORY_NAME] = [lst]
            else:
                result_map[UNKNOWN_CATEGORY_NAME].append(lst)
            unknown_cat = True
            continue
    return result_map


def excel_writer(payments_by_category: dict, file_name, sheet_name):
    workbook = xlsxwriter.Workbook(file_name)
    worksheet = workbook.add_worksheet(sheet_name)
    # payments_by_category values indexes
    # idx_payment_type = 0
    # idx_amount = 1
    # idx_date = 2
    # idx_payment_name = 3

    worksheet.set_column(0, 4, 30)
    merge_format = workbook.add_format(
        {
            "bold": 1,
            "border": 1,
            "align": "center",
            "valign": "vcenter",
            "fg_color": "yellow",
        }
    )
    total_format = workbook.add_format(
        {
            "bold": 1,
            "border": 1,
            "align": "center",
            "valign": "vcenter",
            "fg_color": "red",
        }
    )
    row_idx = 0
    total_by_month = 0
    for category, values in payments_by_category.items():
        worksheet.merge_range(row_idx, 0, row_idx, 4, category, merge_format)
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
    workbook.close()


def main():
    with open('jan.pdf', "rb") as file:

        reader = PyPDF2.PdfReader(file)

        result_list = []
        for page_num in range(0, len(reader.pages)):

            page1 = reader.pages[page_num]
            pdf_data = page1.extract_text()

            # -1 means that lines with payment information haven't yet read
            counter = -1
            # set True if it's a line with SEPA transaction info
            sepa_payment = False
            # set True if it's a line with payment by card info
            card_payment = False

            bargeld_payment = False

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
                    if line.startswith("-") and counter == 0:
                        # sometimes the string is read as simply -
                        # needs to skip it
                        if line == "-":
                            continue
                        amount_and_type = line.split(' ')

                        # 0 index is amount
                        amount = amount_fmt(amount_and_type[0])

                        # 1 index is payment type: SEPA or Kartenzahlung
                        payment_type = amount_and_type[1]

                        # and check the type of pyment
                        sepa_payment = is_sepa(payment_type)
                        card_payment = is_card(payment_type)
                        bargeld_payment = is_bargeld(payment_type)

                        # prepare a tmp result
                        if card_payment:
                            tmp_list.extend(["Karten", amount])
                            counter += 1
                        if sepa_payment:
                            tmp_list.extend(["SEPA", amount])
                            counter += 1
                        if bargeld_payment:
                            tmp_list.extend(["Bargeldauszahlung", amount])
                            counter += 1
                        # next iteration
                        continue
                    if (card_payment or bargeld_payment) and counter != 0:
                        if counter == 1:
                            # unneeded info
                            counter += 1
                            # next iteration
                            continue
                        # line with date for the card info
                        if counter == 2:
                            tmp_list.append(date_fmt(line))
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
                    if sepa_payment and counter != 0:
                        # payment name
                        if counter == 1:
                            tmp_list.append(line)
                            counter += 1
                            # next iteration
                            continue
                        # line with date for the SEPA
                        if counter == 2:
                            # append the date
                            tmp_list.append(date_fmt(line))
                            # formatting list
                            tmp_list[2], tmp_list[3] = tmp_list[3], tmp_list[2]
                            # append tmp to the result
                            result_list.append(tmp_list)
                            # and clear the counter and tmp_list
                            tmp_list = []
                            counter = 0
                            # next iteration
                            continue

    payments_by_category = result_by_category(result_list)

    # simple stdout writer
    for k, v in payments_by_category.items():
        print("#" * 10)
        print("#" * 3, k, "#" * 3)
        print("#" * 10)
        total = 0
        print(v)
        for i in v:
            total += i[1]
        print(total)

    excel_writer(payments_by_category, "test2.xlsx", "test_p1")


if __name__ == "__main__":
    main()
