from classes import OCR
import getopt
from glob import glob
import json
import re
import sys


def main(argv):
    opts, _ = getopt.getopt(argv,"hbf:")
    for opt, arg in opts:
        if opt == "-h":
            print()
            print("python src -b [-f [<file_name>]]")
            print("""Where:
            -b      Extracts in batch every file within the folder ocr/
            -f      Is the filename for the JSON in ocr/ e.g. ticket1.json""")
            sys.exit()
        elif opt == "-b":
            ocrs = glob("ocr/*.json")
            for ocr in ocrs:
                output_filename = re.findall(r"(\w*)\.json", ocr)[0]
                with open(ocr, 'r') as text_ocr:
                    json_ocr = json.loads(text_ocr.read())
                    object_ocr = OCR(json_ocr)
                    object_ocr.extract(output_filename)
        elif opt == "-f":
            output_filename = re.findall(r"(\w*)\.json", arg)[0]
            with open(f'ocr/{arg}', 'r') as text_ocr:
                json_ocr = json.loads(text_ocr.read())
                object_ocr = OCR(json_ocr)
                object_ocr.extract(output_filename)


if __name__ == "__main__":
    main(sys.argv[1:])
