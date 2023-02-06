from datetime import datetime, timedelta
import re
from src.classes import PATTERNS


def date_range(start, end):
    dates=[]
    days_delta = end - start
    years_delta = days_delta.days//365 + 1 
    for i in range(years_delta):
        dates.append((start+timedelta(days=i*365)).strftime("%d/%m/%Y"))
    return dates

class TestClassPatterns:
    """Test cases for regex patterns."""
    def test_date_pattern(self):
        """given a range of dates between 1970 and 2039 assert that regex does match in all cases."""
        start_date = datetime(1970, 1, 1)
        end_date = datetime(2039, 12, 31)
        dates = date_range(start_date, end_date)
        pattern = PATTERNS["DATE"]

        matches = []
        for d in dates:
            text = f'00:00 AM {d}'
            matches.append(re.findall(pattern, text)[0])

        assert all(matches)

    def test_store_address_patern(self):
        """given the string JUMBO STORE ADDRESS CAPTURED VENDEDOR ELE… assert that regex does match"""
        pattern = PATTERNS["STORE_ADDRESS"]["VALUE"]
        text = "JUMBO STORE\nADDRESS CAPTURED\nVENDEDOR ELECTRO"
        store_address = re.findall(pattern, text)[0][1]
        match = store_address.replace("\n", '')

        assert match is not None
        assert match == "ADDRESS CAPTURED"

    def test_invoice_number(self):
        """given the string TIQUETE J123 205263 assert that regex does match"""
        pattern = PATTERNS["INVOICE_NUMBER"]
        text = "TIQUETE J123 205263"
        prefix, number = re.findall(pattern, text)[0]
        match = f'{prefix} {number}'

        assert match is not None
        assert match == "J123 205263"

    def test_line_item_sku(self):
        """given the string 1111111111111 DESC 1 assert that regex does match"""
        pattern = PATTERNS["SKU"]["VALUE"]
        text = "1111111111111 DESC 1"
        match = re.findall(pattern, text)[0][0]

        assert match is not None
        assert match == "1111111111111"

    def test_line_item_description(self):
        """given the string 1111111111111 DESC 1 assert that regex does match"""
        pattern = PATTERNS["SKU"]["VALUE"]
        text = "1111111111111 DESC 1"
        match = re.findall(pattern, text)[0][1]

        assert match is not None
        assert match == "DESC 1"

    def test_line_item_tax_code(self):
        """given the string A NOT V 90 B C= D assert that regex does match"""
        pattern = PATTERNS["TAX_CODE"]
        text = "A\nNOT V\n90 B\nC=\nD"
        matches = []
        for m in re.findall(pattern, text):
            if m[2] != '':
                matches.append(m[2])
            elif m[-1] != '':
                matches.append(m[-1])

        assert matches != []
        assert matches == ['A', 'B', 'C']

    def test_line_item_total(self):
        """given the string A NOT V 90 B C= D assert that regex does match"""
        pattern = r"^(\d*)\s(?=([B])$)"
        text = ("A\n"
                "NOT V\n"
                "90 B\n"
                "C=\n"
                "D")
        match = re.findall(pattern, text, re.MULTILINE)[0][0]

        assert match is not None
        assert match == "90"