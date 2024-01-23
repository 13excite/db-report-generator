import PyPDF2


def is_karten(type_string):
    if type_string.startswith("Kartenz"):
        return True
    return False


def is_sepa(type_string):
    if type_string.startswith("SEPA"):
        return True
    return False


def main():
    with open('rechnung.pdf',"rb") as file:

        reader = PyPDF2.PdfReader(file)

        page1 = reader.pages[1]
        page_count = len(reader.pages)
        print(page_count)

        pdf_data = page1.extract_text()

        counter = -1

        sepa_payment = False
        karten_payment = False

        #print(pdf_data)
        for l in pdf_data.split('\n'):

            if counter < 0:
                if l == "Haben Soll Vorgang Valuta Buchung":
                    print("HEADER FOUND")
                    counter = 0
            else:
                #print(">>>",l)
                if l.startswith("IBAN von Seite Auszug"):
                    counter = -1
                    continue

                if l.startswith("-") and counter == 0:
                    amount_and_type = l.split(' ')
                    amount = amount_and_type[0]
                    type_of_amount = amount_and_type[1]

                    print(type_of_amount)

                    sepa_payment = is_sepa(type_of_amount)
                    karten_payment = is_karten(type_of_amount)
                    # DELETE THIS IF when sepa parser will be ready
                    if karten_payment:
                        counter += 1

                    continue
                if counter == 1 and karten_payment:
                    # unneeded info
                    counter += 1
                    continue
                if counter == 2 and karten_payment:
                    print("DATEEEEE",l)
                    counter += 1
                    continue
                if counter == 3 and karten_payment:
                    # just year, skip
                    counter +=1
                    continue
                if counter == 4 and karten_payment:
                    print("WHOOOO",l)
                    counter = 0
                    continue



                #if counter == 1:

                # if counter == 3:
                #     print("Amount: ", l.split(' ')[0])


if __name__ == "__main__":
    main()
