import os
import logging
import qrcode
from faker import Faker
from barcode import EAN13
from barcode.writer import SVGWriter

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

faker = Faker()

def generate_barcode_ean13(code: str) -> str:
    try:
        directory = r"app/scanner/svg"
        if not os.path.exists(directory):
            os.makedirs(directory)
        
        path = os.path.join(directory, f"code-{code}.svg")
        with open(path, "wb") as f:
            EAN13(code, writer=SVGWriter()).write(f)
        return path
    except Exception as e:
        logger.error(f"Error al generar el código de barras: {e}")
        return None

def generate_qr(data:any):
    try:
        directory = r"app/scanner/img"
        if not os.path.exists(directory):
            os.makedirs(directory)
        path = os.path.join(directory, f"qr-{faker.random_digit()}-{faker.random_letter()}.png")
       
        qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
        )  
        
        qr.add_data(data)
        qr.make(fit = True) 
        img = qr.make_image(fill_color="black", back_color="white")   
        img.save(path) 
        
        
    except Exception as e:
        print(e)

def generate_fake_barcodes(quantity: int):
    for _ in range(quantity):
        new_barcode = faker.ean13()
        barcode_path = generate_barcode_ean13(new_barcode)
        if barcode_path:
            logger.info(f"Código de barras generado: {barcode_path}")
        else:
            logger.error("No se pudo generar el código de barras")

if __name__ == "__main__":
    # generate_fake_barcodes(1)
    # generate_qr(data = "https://github.com/MelonConYogurt")
    pass
