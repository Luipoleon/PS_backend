import cv2

capture = cv2.VideoCapture(0) #Captura video
while(capture.isOpened()):
    ret,frame = capture.read()
    if(cv2.waitKey(1) == ord('s')):
        break
    qrDetector = cv2.QRCodeDetector()
    espacio_liberar,bbox,rectImage = qrDetector.detectAndDecode(frame)

    if len(espacio_liberar) > 0:
        print(f'Espacio {espacio_liberar} liberado') 
        cv2.imshow('webCam',rectImage) #Detecta espacio del QR
        break
    else:
        cv2.imshow('webCam',frame)
        #ser.write(str(100).encode())   #Modifica el angulo del servo para salida
capture.release()
cv2.destroyAllWindows()