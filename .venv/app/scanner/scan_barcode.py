from pyzbar.pyzbar import decode
import threading
import cv2 as cv
import winsound
import time

class Scanner:
    def __init__(self) -> None:
        self.list_code = []
        self.capture = cv.VideoCapture(0)
        self.flag = False  # Añadimos una bandera para controlar el almacenamiento
    
    def recorder(self):
        if not self.capture.isOpened():
            print("Cannot access the camera")
            return
        else:
            while True:
                ret, frame = self.capture.read()
                if not ret:
                    print("Can't receive frame (stream end?). Exiting ...")
                    break
                else:
                    # Decodificamos cada frame para buscar los codigos de barra    
                    self.decode_barcode(frame) 
                                            
                cv.namedWindow("Scanner", cv.WINDOW_NORMAL)
                cv.imshow("Scanner", frame)
                
                # Espera 1 milisegundo para ver si la tecla 'Esc' fue presionada
                if cv.waitKey(1) & 0xFF == 27:  # 27 es el código ASCII para 'Esc'
                    self.capture.release()
                    cv.destroyAllWindows()
                    return self.list_code

    def decode_barcode(self, frame):
        decode_frame = decode(frame)
        if decode_frame:
            for barcode in decode_frame:
                barcode_data = barcode.data.decode('utf-8')
                
                # Obtener el recuadro delimitador del código de barras
                x, y, w, h = barcode.rect
                # Dibujar el recuadro alrededor del código de barras
                cv.rectangle(frame, (x, y), (x + w, y + h), (77, 97, 248), 2)
                
                show_text = f"Code: {barcode_data}"
                # Ajustar la posición del texto para que no se solape con el recuadro
                text_x = x
                text_y = y - 10  
                # Mostrar el codigo sobre el codigo de barras
                cv.putText(frame, show_text, (text_x, text_y), cv.FONT_HERSHEY_SIMPLEX, 0.7, (255, 77, 0), 2)
                
                # Almacenamos cada uno de los códigos leídos
                if not self.flag:  # Solo almacenamos si la bandera no está activada
                    threading.Thread(target=self.local_storage, args=(barcode_data,)).start()

    def local_storage(self, data):
        self.flag = True  # Activamos la bandera
        self.list_code.append(data)  # Añadir el código a la lista
        winsound.Beep(1000, 500)
        print(f"Barcode data: {data}")
        time.sleep(3)  # Espera de 3 segundos después de añadir el código
        self.flag = False  # Desactivamos la bandera después de 3 segundos

if __name__ == "__main__":
    # scanner_instance = Scanner()
    # scanned_codes = scanner_instance.recorder()
    # print("Scanned barcodes:")
    # for code in scanned_codes:
    #     print(code)
    pass