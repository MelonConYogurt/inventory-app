import cv2

# Cargar el clasificador preentrenado de rostros
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Inicializar la captura de video desde la cámara web
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: No se puede abrir la cámara")
    exit()

while True:
    # Capturar frame por frame
    ret, frame = cap.read()
    
    # Si el frame se lee correctamente, ret es True
    if not ret:
        print("No se puede recibir frame (stream end?). Exiting ...")
        break
    
    # Convertir el frame a escala de grises
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Detectar rostros en el frame
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)
    
    for (x, y, w, h) in faces:
        # Recortar la región de interés (ROI) que contiene el rostro
        roi = frame[y:y+h, x:x+w]
        
        # Mostrar la ROI en una ventana
        cv2.imshow('ROI', roi)
        
        # Dibujar un rectángulo en la imagen original para mostrar la ROI
        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
    
    # Mostrar el frame con los rectángulos dibujados
    cv2.imshow('frame', frame)
    
    # Salir del bucle cuando se presione 'q'
    if cv2.waitKey(1) == ord('q'):
        break

# Liberar el objeto captura y cerrar todas las ventanas
cap.release()
cv2.destroyAllWindows()
