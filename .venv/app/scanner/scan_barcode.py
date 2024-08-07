import time
import winsound
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
                    barcode_data = barcode.data.decode('utf-8')
                    
                    show_text = f"Code: {barcode_data}"
                    x, y, w, h = barcode.rect
                    cv.rectangle(frame, (x, y), (x + w, y + h), (77, 97, 248), 2)
                    
                    text_x = x
                    text_y = y - 10  
                
                    cv.putText(frame, show_text, (text_x, text_y), cv.FONT_HERSHEY_SIMPLEX, 0.7, (255, 77, 0), 2)
                    
                    if barcode_data:
                        list_code.append(barcode_data)
                        winsound.Beep(1000, 500)
                        print(f"Barcode data: {barcode_data}")
                        time.sleep(3)  
                    
        cv.namedWindow("Scanner", cv.WINDOW_NORMAL)
        cv.imshow("Scanner", frame)
        
        
        if cv.waitKey(1) & 0xFF == 27:  
            capture.release()
            cv.destroyAllWindows()
            return list_code

if __name__ == "__main__":
    # scanned_codes = scanner()
    # print("Scanned barcodes:")
    # for code in scanned_codes:
    #     print(code)
    pass
    
