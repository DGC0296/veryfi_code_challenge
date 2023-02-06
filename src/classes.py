from collections import Counter
from copy import deepcopy
import json
import re


class OCR:
    def __init__(self, input_json):
        self.full_annotation = ""
        self.json = input_json
        self.known_tax_codes = []
        self.lines = []
        self.line_items = []

        try:
            self._parse_json()
        except Exception as e:
            raise e

        self._find_tax_codes()

    def __str__(self):
        return json.dumps(self.full_annotation)

    def _parse_json(self):
        input_pages = self.json.get("pages") 
        if input_pages is not None:
            full_annotation = input_pages[0].get("fullTextAnnotation")
            text = full_annotation.get("text")
            lines = text.split('\n')
            self.full_annotation =  text
            self.lines =  lines
        else:
            raise Exception("The provided OCR doesn't have any pages.")

    def _extract_date(self):
        pattern = r"(?<=[01][0-9]:[0-5]\d).*(([0-2]|(3))(?(3)[01]|\d)/(0|(1)(?(5)[0-2]|[09]))/(1|(2))(?(7)0|9)(?(7)[0-3]|[7-9])\d)"
        local_annotation = deepcopy(self.full_annotation)
        local_annotation = local_annotation.replace("\n", "\\n")
        self.date = re.findall(pattern, local_annotation, re.MULTILINE)[0][0]

    def _extract_store_address(self):
        pattern = r"(?<=JUMBO).*[^\n]((.*\s)*)(?=VENDEDOR ELECTRO)"
        start = { "regex": r'JUMBO'}
        end = { "threshold": 10 }
        annotation_slice = self._get_annotation_slice(start_params=start, end_params=end)
        store_address = re.findall(pattern, annotation_slice, re.MULTILINE)[0][1]
        self.store_address = store_address.replace("\n", '')

    def _extract_invoice_number(self):
        pattern = r"(?<=TIQUETE)\s?(J\d{3})\s?(?=(\d{6}))"
        prefix, number = re.findall(pattern, self.full_annotation, re.MULTILINE)[0]
        self.invoice_number = f'{prefix} {number}'

    def _extract_line_items_SKU_and_description(self):
        pattern = r"(\d{13})\s?((\w*[^\n])*)"
        start = { "regex": r"VENDEDOR\s?ELECTRO" }
        end = { "regex": r"NRO\.?\s?CUENTA" }
        annotation_slice = self._get_annotation_slice(start_params=start, end_params=end)
        
        skus = []
        descriptions = []
        for values in re.findall(pattern, annotation_slice, re.MULTILINE):
            sku, description, _ = values
            skus.append(sku)
            descriptions.append(description)

        self._set_line_items_attribute(skus, "sku")
        self._set_line_items_attribute(descriptions, "description")

    def _extract_line_items_tax_codes_and_totals(self):
        tax_codes_pattern = ''.join(self.known_tax_codes)
        look_ahead = f'(?=([{tax_codes_pattern}])$)'
        pattern = r"^(\d*)\s" + look_ahead

        for i, l in enumerate(self.lines):
            if re.search(pattern, l):
                start_index = i - 1
                break
        for i, l in enumerate(reversed(self.lines)):
            if re.search(pattern, l):
                end_index = i - 1
                break

        local_lines = self.lines[start_index:-end_index]
        new_pattern = pattern + r"|^\d*$"
        local_lines = [l for l in local_lines if re.search(new_pattern, l)]

        totals = []
        tax_codes = []
        for i, l in enumerate(local_lines):
            if re.search(pattern, l):
                value, code = re.findall(pattern, l)[0]
                totals.append(int(value))
                tax_codes.append(code)
            else:
                if (int(l) != totals[-1]):
                    prev, _ = re.findall(pattern, local_lines[i-1])[0]
                    if (int(l) % int(prev)) != 0:
                        value = int(l)
                        if value < sum(totals):
                            totals.append(value)
                            tax_codes.append(None)
                else:
                    value = int(l)
                    totals.append(value)
                    tax_codes.append(None)

        self._set_line_items_attribute(totals, "total")
        self._set_line_items_attribute(tax_codes, "tax_code")

    def _find_tax_codes(self):
        pattern = r"(((?<=\d\s)|(?<!.))([A-Z])\n)|(([A-Z])(?=\=))"
        
        tentative_tax_codes = []
        known_tax_codes = []
        for m in re.findall(pattern, self.full_annotation, re.MULTILINE):
            if m[2] != '':
                tentative_tax_codes.append(m[2])
            elif m[-1] != '':
                known_tax_codes.append(m[-1])
        freq_tentative_tax_codes = dict(Counter(tentative_tax_codes))
        freq_tentative_tax_codes = { k: v/sum(freq_tentative_tax_codes.values()) for k, v in freq_tentative_tax_codes.items() }
        tentative_tax_codes = [c for c in set(tentative_tax_codes) if freq_tentative_tax_codes[c] >= 0.1]
        known_tax_codes.extend(tentative_tax_codes)
        self.known_tax_codes = known_tax_codes

    def _set_line_items_attribute(self, values_list, attribute):
        collection = [{ attribute: v } for v in values_list]
        if self.line_items == []:
            self.line_items = collection
        else:
            for l_i, c in zip(self.line_items, collection):
                l_i.update(c)

    def _get_annotation_slice(self, start_params={}, end_params={}, return_lines=False):
        greedy_start = start_params.get("greedy", False)
        greedy_end = end_params.get("greedy", False)

        start = None
        end = None

        lines = self.lines

        if greedy_start:
            start = 0
        elif "threshold" in start_params:
            start = start_params["threshold"]

        if greedy_end:
            end = len(lines)
        elif "threshold" in end_params:
            end = end_params["threshold"] + 1

        if (start is None) or (end is None):
            for i, l in enumerate(lines):
                if "regex" in start_params:
                    if re.search(start_params["regex"], l):
                        start = i
                if "regex" in end_params:
                    if re.search(end_params["regex"], l):
                        end = i + 1
                if (start is not None) and (end is not None):
                    break

        if return_lines:
            return lines[start:end]
        else:
            return "\n".join(lines[start:end])

    def set_date(self):
        self._extract_date()

    def set_store_address(self):
        self._extract_store_address()

    def set_invoice_number(self):
        self._extract_invoice_number()

    def set_line_items_SKU_and_description(self):
        self._extract_line_items_SKU_and_description()

    def set_line_items_tax_codes_and_totals(self):
        self._extract_line_items_tax_codes_and_totals()
