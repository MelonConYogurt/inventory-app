import cv2 as cv
import keyboard

def scanner():
    capture = cv.VideoCapture(0)
    
    while True:
        isTrue, frame = capture.read()
        if not isTrue:
            break
        
        cv.imshow("Image", frame)
        
        # Espera 1 milisegundo para ver si la tecla fue presionada
        key = cv.waitKey(1)
        
        # Si la tecla es 'Esc' (código 27) o la tecla 'Esc' está presionada
        if key == 27 or keyboard.is_pressed("esc"):
            break
    
    capture.release()
    cv.destroyAllWindows()
    
    
if __name__ == "__main__":
    scanner()
