import cv2 as cv
from pyzbar.pyzbar import decode

def scanner():
    list_code = []
    capture = cv.VideoCapture(0)
    if not capture.isOpened():
        print("Cannot access the camera")
        return
    
    while True:
        ret, frame = capture.read()
        if not ret:
            print("Can't receive frame (stream end?). Exiting ...")
            break
        else:
            decode_frame = decode(frame)
            if decode_frame:
                for barcode in decode_frame:
                    
                    # Obtener el recuadro delimitador del código de barras
                    x, y, w, h = barcode.rect
                    # Dibujar el recuadro alrededor del código de barras
                    cv.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    
                    
                    barcode_data = barcode.data.decode('utf-8')
                    if barcode_data:
                        if barcode_data not in list_code:
                            list_code.append(barcode_data)
                        print(f"Barcode data: {barcode_data}")
            
        cv.imshow("Scanner", frame)
        
        # Espera 1 milisegundo para ver si la tecla 'Esc' fue presionada
        if cv.waitKey(1) & 0xFF == 27:  # 27 es el código ASCII para 'Esc'
            capture.release()
            cv.destroyAllWindows()
            return list_code

if __name__ == "__main__":
    scanned_codes = scanner()
    print("Scanned barcodes:")
    for code in scanned_codes:
        print(code)