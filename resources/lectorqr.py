from threading import Thread
from flask_restful import Resource
from multiprocessing import Process, Value
import ctypes
import cv2 
from pyzbar import pyzbar
from apscheduler.schedulers.background import BackgroundScheduler

"""
class lectorQR(Resource):
    response: dict = {"estatus":200, "mensaje":"Sin cambios realizados"}
    def get(self):
        try: 
            canal = Value(ctypes.c_wchar_p, "")
            qr = Process(target=lectorqr, args=(canal,))
            espacio = lectorqr()
            if not espacio:
                return self.response
            self.response["estatus"] = 200
            self.response["mensaje"] = espacio
            return self.response
        except:
            self.response["estatus"] = 500
            self.response["mensaje"] = "Ocurrio un problema"

"""
# Intento de chatgpt
class lectorQR(Resource):
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.data = None

    def start_scanning(self):
        self.scheduler.add_job(func=self.scan_qr_code, trigger='interval', seconds=1)
        self.scheduler.start()

    def stop_scanning(self):
        self.scheduler.shutdown()

    def scan_qr_code(self):
        camera = cv2.VideoCapture(0)

        _, frame = camera.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        barcodes = pyzbar.decode(gray)

        for barcode in barcodes:
            (x, y, w, h) = barcode.rect
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            barcode_data = barcode.data.decode("utf-8")
            barcode_type = barcode.type

            self.data = barcode_data
            break

        cv2.imshow("QR Scanner", frame)

        if cv2.waitKey(1) == ord('q'):
            camera.release()
            cv2.destroyAllWindows()

    def get(self):
        if self.scheduler.running:
            return {'message': 'Scanning already in progress'}
        
        self.data = None  # Reiniciar los datos del código QR
        self.start_scanning()

        # Esperar hasta que se detecte un código QR válido
        while self.data is None:
            pass

        self.stop_scanning()
        return {'data': self.data}

def lectorqr(canal):
    capture = cv2.VideoCapture(0) #Captura video
    espacio_liberar: int
    while(capture.isOpened()):
        ret,frame = capture.read()
        if(cv2.waitKey(1) == ord('s')):
            return -1
            # break
        qrDetector = cv2.QRCodeDetector()
        espacio_liberar,_,rectImage = qrDetector.detectAndDecode(frame)
        print("Somehow, im here")
        if len(espacio_liberar) > 0:
            print(f'Espacio: {espacio_liberar}') 
            cv2.imshow('webCam',rectImage) #Detecta espacio del QR
            print("Finish!")
            break
        else:
            cv2.imshow('webCam',frame)
            print("Retrying!")
    capture.release()
    cv2.destroyAllWindows()
    return espacio_liberar

if __name__ == "__main__":
    canal = Value(ctypes.c_wchar_p, "")
    while True:
        qr = Process(target=lectorqr, args=(canal,))
        if int(input('H->')):
            qr.start()
            qr.join()
            print(canal.value.value)