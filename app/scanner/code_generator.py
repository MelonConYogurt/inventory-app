import os
from faker import Faker
from barcode import EAN13
from barcode.writer import SVGWriter

faker = Faker()


def generate_barcode_ean13(code: int):
    try:
        directory = r"app/scanner/svg"
        if not os.path.exists(directory):
            os.makedirs(directory)
        
        path = os.path.join(directory, f"code-{code}.svg")
        with open (path, "wb") as f:
            EAN13(str(code), writer= SVGWriter()).write(f)
            return path
    except Exception as e:
        print(e)
        

def generate_fake_barcode(quantity:int):
    for _ in range(quantity):
        new_barcode = generate_barcode_ean13(faker.ean13())
        print(new_barcode)
            

if __name__== "__main__":
    generate_fake_barcode(20)
    pass