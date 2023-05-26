from datetime import datetime
import serial  # CONEXION CON ARDUINO
from time import sleep  # GENERA TIEMPOS DE ESPERA
# Permite realizar subprocesos (ejecuta las funciones de Arduino simultaneamente
import threading
from multiprocessing import Value
from random import randint

def initSensores() -> serial.Serial:
    intentos: int = 1
    while intentos <= 3:
        try:
            ser = serial.Serial('COM3', 9600)
            if not ser.isOpen():
                ser.open()
                print('com3 is open', ser.isOpen())
            else:
                print('com3 is open', ser.isOpen())
                break
        except Exception as e:
            # print(f"[Sensores]: No se pudo conectar con el arduino. Reintentado ({intentos}/3)")
            print(f"{e}. Retrying ({intentos}/3)")
            sleep(1)
            intentos += 1
            continue
    if intentos > 3:
        raise serial.SerialTimeoutException("[WARNING]:  No se pudo establecer conexíon con el arduino")
    else:
        print("[OK]: Se ha establecido conexión con el arduino")
        return ser


# Validacion de espacios por                                                              #sensor
def validarEspacioOcupado(ser: serial.Serial, espacios: list, database: str = "sqlite"):
    if database == "sqlite":
        from parking import ocupar_desocupar
    else:
        from parking_mysql import ocupar_desocupar
    cont = 1
    set_ocupar1 = True
    set_ocupar2 = True
    set_ocupar3 = True
    sleep(5)
    while True:  # Regresa la distancia del objeto detectado al sensor en tiempo                           #real
        if (ser.inWaiting() > 0):
            mydata = ser.readline()  # Obtiene los datos de Arduino
            try:
                datos = float(mydata)
            except ValueError:
                datos = float(mydata.replace('\r\n', "0"))
            if cont == 2:  # Primer epacio
                if datos <= 5:  # Si la distancia menor/igual a 5
                    # print(f' Espacio 1 ocupado: {datos}cm')
                    # Se llama a la funcion que ocupa espacios:
                    if set_ocupar1:
                        fecha_hora = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
                        ocupar_desocupar('A1', 1, fecha_hora)
                        set_ocupar1 = False
                else:
                    # print(' Espacio 1 desocupado')
                    # Se llama a la funcion que desocupa espacios
                    if not set_ocupar1:
                        ocupar_desocupar('A1', 0, None)
                        set_ocupar1 = True
            elif cont == 4:  # Segundo espacio
                if datos <= 5:  # Si la distancia menor/igual a 5
                    # print(f' Espacio 2 ocupado: {datos}cm')
                    # Se llama a la funcion que ocupa espacios:
                    if set_ocupar2:
                        fecha_hora = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
                        ocupar_desocupar('A2', 1, fecha_hora)
                        set_ocupar2 = False
                else:
                    # print(' Espacio 2 desocupado')
                    if not set_ocupar2:
                        ocupar_desocupar('A2', 0, None)
                        set_ocupar2 = True
            elif cont == 6:  # Tercer espacio
                if datos <= 3:  # Si la distancia menor/igual a 3
                    # print(f' Espacio 3 ocupado: {datos}cm')
                    # Se llama a la funcion que ocupa espacios:
                    if set_ocupar2:
                        fecha_hora = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
                        ocupar_desocupar('A3', 1, fecha_hora)
                        set_ocupar2 = False
                else:
                    # print(' Espacio 3 desocupado')
                    if not set_ocupar3:
                        ocupar_desocupar('A3', 0, None)
                        set_ocupar3 = True
            cont += 1
            # sleep(1)
            if cont == 7:
                cont = 1


# Validacion de espacios por                                                              #sensor
def fakevalidarEspacioOcupado(espacios: list, database: str = "sqlite"):
    if database == "sqlite":
        from parking import ocupar_desocupar
    else:
        from parking_mysql import ocupar_desocupar
    cont = 1
    set_ocupar1 = True
    set_ocupar2 = True
    set_ocupar3 = True
    sleep(5)
    while True:  # Regresa la distancia del objeto detectado al sensor en tiempo                           #real
        datos = randint(0,10)  # Obtiene los datos falsos
        if cont == 2:  # Primer epacio
            if datos <= 5:  # Si la distancia menor/igual a 5
                # print(f' Espacio 1 ocupado: {datos}cm')
                # Se llama a la funcion que ocupa espacios:
                if set_ocupar1:
                    fecha_hora = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
                    ocupar_desocupar('A1', 1, fecha_hora)
                    set_ocupar1 = False
            else:
                # print(' Espacio 1 desocupado')
                # Se llama a la funcion que desocupa espacios
                if not set_ocupar1:
                    ocupar_desocupar('A1', 0, None)
                    set_ocupar1 = True
        elif cont == 4:  # Segundo espacio
            if datos <= 5:  # Si la distancia menor/igual a 5
                # print(f' Espacio 2 ocupado: {datos}cm')
                # Se llama a la funcion que ocupa espacios:
                if set_ocupar2:
                    fecha_hora = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
                    ocupar_desocupar('A2', 1, fecha_hora)
                    set_ocupar2 = False
            else:
                # print(' Espacio 2 desocupado')
                if not set_ocupar2:
                    ocupar_desocupar('A2', 0, None)
                    set_ocupar2 = True
        elif cont == 6:  # Tercer espacio
            if datos <= 3:  # Si la distancia menor/igual a 3
                # print(f' Espacio 3 ocupado: {datos}cm')
                # Se llama a la funcion que ocupa espacios:
                if set_ocupar3:
                    fecha_hora = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
                    ocupar_desocupar('A3', 1, fecha_hora)
                    set_ocupar3 = False
            else:
                # print(' Espacio 3 desocupado')
                if not set_ocupar3:
                    ocupar_desocupar('A3', 0, None)
                    set_ocupar3 = True
        cont += 1
        sleep(3)
        if cont == 7:
            cont = 1