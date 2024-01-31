import PyPDF2


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
    ],
    "InternetService": [
        "Spotify",
    ]
}


def is_card(type_string):
    if type_string.startswith("Kartenz"):
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
    return "%s.%s.%s" % (year, month, day)
def main():
    with open('rechnung.pdf',"rb") as file:

        reader = PyPDF2.PdfReader(file)

        page_count = len(reader.pages)
        print(page_count)

        result_list = []
        for page_num in range(0, len(reader.pages)):
            page1 = reader.pages[page_num]
            pdf_data = page1.extract_text()

            counter = -1
            sepa_payment = False
            card_payment = False

            #result_list = []
            tmp_list = []
            for l in pdf_data.split('\n'):
                if counter < 0:
                    if l == "Haben Soll Vorgang Valuta Buchung":
                        #print("HEADER FOUND")
                        counter = 0
                else:
                    if l.startswith("IBAN von Seite Auszug"):
                        counter = -1
                        continue

                    if l.startswith("-") and counter == 0:
                        amount_and_type = l.split(' ')

                        amount = amount_fmt(amount_and_type[0])

                        type_of_amount = amount_and_type[1]
                        #print(">>>>", type_of_amount, amount)

                        # print(type_of_amount)

                        sepa_payment = is_sepa(type_of_amount)
                        card_payment = is_card(type_of_amount)
                        # DELETE THIS IF when sepa parser will be ready
                        if card_payment:
                            tmp_list.append("Karten")
                            tmp_list.append(amount)
                            counter += 1
                        if sepa_payment:
                            tmp_list.append("SEPA")
                            tmp_list.append(amount)
                            counter += 1

                        continue
                    if card_payment and counter != 0:
                        if counter == 1:
                            # unneeded info
                            counter += 1
                            continue
                        if counter == 2:
                            # print("DATEEEEE", l)
                            tmp_list.append(date_fmt(l))
                            counter += 1
                            continue
                        if counter == 3:
                            # just year, skip
                            counter +=1
                            continue
                        if counter == 4:
                            # print("WHOOOO",l)
                            tmp_list.append(l)
                            result_list.append(tmp_list)
                            tmp_list = []
                            counter = 0
                            continue
                    if sepa_payment and counter != 0:
                        if counter == 1:
                            tmp_list.append(l)
                            counter += 1
                            continue
                        if counter == 2:
                            tmp_list.append(date_fmt(l))
                            tmp_list[2],tmp_list[3] = tmp_list[3], tmp_list[2]
                            result_list.append(tmp_list)
                            tmp_list = []
                            counter = 0
                            continue

    result_by_category = {}
    for lst in result_list:
        # idx 3 is name of costs
        unknown_cat = True
        for cat_type, values in shops_type.items():
            # iterate by each shop pfx
            for shop_pfx in values:
                pfx_found = False
                if shop_pfx.lower() in lst[3].lower():
                    if result_by_category.get(cat_type, "") == "":
                        result_by_category[cat_type] = [lst]
                        unknown_cat = False
                        pfx_found = True
                        break
                    else:
                        result_by_category[cat_type].append(lst)
                        unknown_cat = False
                        pfx_found = True
                        break
                if pfx_found:
                    break



            # if lst[3].lower() in values:
            #     if result_by_category.get(cat_type, "") == "":
            #         result_by_category[cat_type] = [lst]
            #         unknown_cat = False
            #         break
            #     else:
            #         result_by_category[cat_type].append(lst)
            #         unknown_cat = False
            #         break
        if unknown_cat:
            if result_by_category.get("UNKNOWN", "") == "":
                result_by_category["UNKNOWN"] = [lst]
            else:
                result_by_category["UNKNOWN"].append(lst)
            unknown_cat = True
            continue
    print(result_by_category)

    for k, v in result_by_category.items():
        print("#"*10)
        print("#"*3, k, "#"*3)
        print("#"*10)
        total = 0
        for i in v:
            total += i[1]
        print(total)

        #print(lst)


if __name__ == "__main__":
    main()
