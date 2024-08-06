import cv2 as cv
import keyboard
from pyzbar.pyzbar import decode

def scanner():
    capture = cv.VideoCapture(0)
    if not capture.isOpened():
        print("Cannot acces to the camera")
        exit()
    
    while True:
        ret, frame = capture.read()
        if not ret:
            print("Can't receive frame (stream end?). Exiting ...")
            break
        
        decode_frame = decode(frame)
        if not decode_frame:
            pass
        else:
            for barcode in decode_frame:
                if barcode.data != "":
                    barcode_data = barcode.data
                    print(barcode_data)
                    return barcode_data
            
        cv.imshow("Scanner", frame)
        
        # Espera 1 milisegundo para ver si la tecla fue presionada
        key = cv.waitKey(1)
        
        # Si la tecla es 'Esc' (código 27) o la tecla 'Esc' está presionada
        if key == 27 or keyboard.is_pressed("esc"):
            break
    
    capture.release()
    cv.destroyAllWindows()
    
    
if __name__ == "__main__":
    scanner()



import cv2 as cv
from pyzbar.pyzbar import decode

def scanner():
    capture = cv.VideoCapture(0)
    if not capture.isOpened():
        print("Cannot access the camera")
        return
    
    while True:
        ret, frame = capture.read()
        if not ret:
            print("Can't receive frame (stream end?). Exiting ...")
            break
        
        decode_frame = decode(frame)
        if decode_frame:
            for barcode in decode_frame:
                barcode_data = barcode.data.decode('utf-8')
                if barcode_data:
                    print(f"Barcode data: {barcode_data}")
                    capture.release()
                    cv.destroyAllWindows()
                    return barcode_data
            
        cv.imshow("Scanner", frame)
        
        # Espera 1 milisegundo para ver si la tecla 'Esc' fue presionada
        if cv.waitKey(1) & 0xFF == 27:  # 27 es el código ASCII para 'Esc'
            break
    
    capture.release()
    cv.destroyAllWindows()

if __name__ == "__main__":
    scanner()
