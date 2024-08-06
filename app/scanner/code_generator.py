from barcode import EAN13
from barcode.writer import SVGWriter

def generate_barcode_ean13(code: int):
    try:
        with open (f"code-{code}.svg", "wb") as f:
            EAN13(str(code), writer= SVGWriter()).write(f)
    except Exception as e:
        print(e)
        
        
        
if __name__== "__main__":
    generate_barcode_ean13(1222780790790)