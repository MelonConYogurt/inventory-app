from pyzbar.pyzbar import decode
import threading
import cv2 as cv
import winsound
import time

class Scanner:
    def __init__(self) -> None:
        self.list_code = []
        self.capture = cv.VideoCapture(0)
        self.flag = False  # Added a flag to control the storage
    
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
                    # Decode each frame to look for barcodes    
                    self.decode_barcode(frame) 
                                            
                cv.namedWindow("Scanner", cv.WINDOW_NORMAL)
                cv.imshow("Scanner", frame)
                
                # Wait 1 millisecond to see if the 'Esc' key was pressed
                if cv.waitKey(1) & 0xFF == 27:  # 27 is the ASCII code for 'Esc'
                    self.capture.release()
                    cv.destroyAllWindows()
                    return self.list_code

    def decode_barcode(self, frame):
        decode_frame = decode(frame)
        if decode_frame:
            for barcode in decode_frame:
                barcode_data = barcode.data.decode('utf-8')
                
                # Get the bounding box of the barcode
                x, y, w, h = barcode.rect
                # Draw the bounding box around the barcode
                cv.rectangle(frame, (x, y), (x + w, y + h), (77, 97, 248), 2)
                
                show_text = f"Code: {barcode_data}"
                # Adjust the text position so it does not overlap with the bounding box
                text_x = x
                text_y = y - 10  
                # Display the code above the barcode
                cv.putText(frame, show_text, (text_x, text_y), cv.FONT_HERSHEY_SIMPLEX, 0.7, (255, 77, 0), 2)
                
                # Store each of the read codes
                if not self.flag:  # Only store if the flag is not activated
                    threading.Thread(target=self.local_storage, args=(barcode_data,)).start()

    def local_storage(self, data):
        self.flag = True  # Activate the flag
        self.list_code.append(data)  # Add the code to the list
        winsound.Beep(1000, 500)
        print(f"Barcode data: {data}")
        time.sleep(3)  # Wait for 3 seconds after adding the code
        self.flag = False  # Deactivate the flag after 3 seconds

if __name__ == "__main__":
    # scanner_instance = Scanner()
    # scanned_codes = scanner_instance.recorder()
    # print("Scanned barcodes:")
    # for code in scanned_codes:
    #     print(code)
    pass