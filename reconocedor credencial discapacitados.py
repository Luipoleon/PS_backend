import cv2           #Libreria OpenCv para activar camara
import pytesseract   #Libreria deteccion de texto
import re            #Libreria de coincidencia de expresionres regulares

#El programa necesita: pip install pytesseract (CMD, Anaconda...) y
#el isntalador en: https://github.com/UB-Mannheim/tesseract/wiki (x64 bits) 

# Variables
cuadro = 100 #Dimension del cuadro para escanear
doc = 0      #Estado del documento (0/por leer, 1/credencial valida)

# Captura de video
cap = cv2.VideoCapture(0) #Captura video de la camara, argumentos validos = (0),(1),(2)
cap.set(3,1280) #Resolucion de fotogramas camara (Ancho,x)
cap.set(4,720)  #Resolucion de fotogramas camara (Alto,y)

def texto(image): #Busca caracteres en la imagen al escanear
    global doc
    #Direccion de instalacion de Pytesseract por default 
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    # Escala de grises
    gris = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Umbral
    umbral = cv2.adaptiveThreshold(gris, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 55, 25)

    # Configuracion del OCR
    config = "--psm 1"
    texto = pytesseract.image_to_string(umbral, config=config)

    # Palabras clave credencial discapacidad
    secemex = r'SALUD'
    secemex2 = r'ESTADOS UNIDOS MEXICANOS'

    buscemex = re.findall(secemex, texto)
    buscemex2 = re.findall(secemex2, texto)

    
    print(texto) #Imprime por consola el texto identificado por la camara 
    #El texto identificado varia dependiendo de la iluminacion y la camara 

    # Si se detectan las palabras clave, es discapacitado
    if len(buscemex) != 0 or len(buscemex2) != 0:
        doc = 1

while True:
    # Lectura de la VideoCaptura
    ret, frame = cap.read()
    # 'Interfaz'
    #Los tamaños entre parentesis Ej: (150,80),(cuadro,cuadro),(720,480) 
    #se pueden ajustar a la resolucion de la camara
    cv2.putText(frame, 'Ubique el documento de identidad', (150, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.71, (0, 255, 0), 2)
    cv2.rectangle(frame, (cuadro, cuadro), (720 - cuadro, 480 - cuadro), (0, 255, 0), 2)

    # Press S or s to Scan
    if doc == 0:
        cv2.putText(frame, 'PRESIONA S PARA IDENTIFICAR', (150, 480), cv2.FONT_HERSHEY_SIMPLEX, 0.71,(0, 255, 0), 2)
        print('Escaneado.')

    #Si se detecta una credencial valida muestra por videoCamara
    elif doc == 1:
        cv2.putText(frame, 'IDENTIFICACION DE DISCAPACIDAD', (150, 500 - cuadro), cv2.FONT_HERSHEY_SIMPLEX, 0.71,(0, 255, 255), 2)
        print('Credencial de Discapacidad Mexicana')

    t = cv2.waitKey(1)
    # Reset [R] [r]
    if t == 82 or t == 114:
        doc = 0

    # Scan [S] [s] Llama a la funcion texto para encontrar caracteres en la credencial
    if t == 83 or t == 115:
        texto(frame)

    # Mostramos FPS
    cv2.imshow("ID INTELIGENTE", frame)
    if t == 27:
        break

cap.release()
cv2.destroyAllWindows()
