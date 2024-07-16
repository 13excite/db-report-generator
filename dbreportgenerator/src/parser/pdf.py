import io
import re
import PyPDF2

from dataclasses import dataclass as struct
from typing import List


@struct
class _paymentData:
    type_text: str
    card_payment: bool
    sepa_payment: bool
    bargeld_payment: bool


class PdfReportParser:

    def __init__(self) -> None:
        self._result: List = []
        self.__reader: PyPDF2.PdfReader = None
        self.__payment_data: _paymentData = None

    # read pdf file
    def read_pdf(self, file_stream: io.BufferedReader):
        self.__reader = PyPDF2.PdfReader(file_stream)

    def parse(self):
        for page_num, _ in enumerate(self.__reader.pages):

            page1 = self.__reader.pages[page_num]
            pdf_data = page1.extract_text()

            # -1 means that lines with payment information haven't yet read
            counter = -1

            # tmp_list contains temporary data that will be inserted into the self._result
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
                        amount = self._amount_fmt(amount_and_type[0])

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
                            tmp_list.append(self._date_fmt(line))
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
                            self._result.append(tmp_list)
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
                            tmp_list.append(self._date_fmt(line))
                            # formatting list
                            tmp_list[2], tmp_list[3] = tmp_list[3], tmp_list[2]
                            # append tmp to the result
                            self._result.append(tmp_list)
                            # and clear the counter and tmp_list
                            tmp_list = []
                            counter = 0
                            # next iteration
                            continue

    def __get_payment_type(self, payment_type: str) -> _paymentData:
        sepa_payment = self._is_sepa(payment_type)
        card_payment = self._is_card(payment_type)
        bargeld_payment = self._is_bargeld(payment_type)

        pyment_type_str = "Unknown"
        if card_payment:
            pyment_type_str = "Karten"
        elif sepa_payment:
            pyment_type_str = "SEPA"
        elif bargeld_payment:
            pyment_type_str = "Bargeldauszahlung"

        return _paymentData(pyment_type_str, card_payment, sepa_payment, bargeld_payment)

    @property
    def result(self):
        return self._result

    @result.setter
    def result(self, value: List):
        self._result = value

    # check if the payment type is card payment
    @staticmethod
    def _is_card(type_string):
        if type_string.startswith("Kartenz"):
            return True
        return False

    # check if the payment type is cash withdrawal
    @staticmethod
    def _is_bargeld(type_string):
        if type_string.startswith("Bargeld"):
            return True
        return False

    # check if the payment type is SEPA transaction
    @staticmethod
    def _is_sepa(type_string):
        if type_string.startswith("SEPA"):
            return True
        return False

    # format amount from '1.234,00' to '1234.00
    @staticmethod
    def _amount_fmt(amount: str):
        if ("," in amount) and ("." in amount):
            r = amount.replace(".", "").replace(",", ".")
            return float(r)
        return float(amount.replace(',', '.'))

    # format date from '202304.12.' to '2023.04.12'
    @staticmethod
    def _date_fmt(date_str: str):
        month = date_str.split(".")[1]
        year = date_str[:4]
        day = date_str[4:6]
        "".replace(',', '.')
        return f"{year}.{month}.{day}"
