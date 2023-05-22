import serial                #CONEXION CON ARDUINO 
from time import sleep       #GENERA TIEMPOS DE ESPERA
import threading             #Permite realizar subprocesos (ejecuta las funciones de Arduino simultaneamente
from multiprocessing import Value

def initSensores() -> serial.Serial:
    intentos: int = 1
    while intentos <= 3:
        try:
            ser = serial.Serial('COM3',9600)
        except Exception as e:
            #print(f"[Sensores]: No se pudo conectar con el arduino. Reintentado ({intentos}/3)")
            print(f"{e}. Retrying ({intentos}/3)")
            sleep(1)
            intentos += 1
            continue
    if intentos > 3:
        raise serial.SerialTimeoutException
    else:
        print("[OK]: Se ha establecido conexión con el arduino")
        return ser
            
def validarEspacioOcupado(ser: serial.Serial, espacios: list, canales: list): #Validacion de espacios por                                                              #sensor
     cont = 1
     sleep(5)
     while True:      #Regresa la distancia del objeto detectado al sensor en tiempo                           #real 
        if(ser.inWaiting()>0):
            mydata = ser.readline() #Obtiene los datos de Arduino
            try:
                 datos = float(mydata)
            except ValueError:
                datos = float(mydata.replace('\r\n',"0")) 
            if cont == 2: #Primer epacio
                if datos <= 5: #Si la distancia menor/igual a 5
                    #print(f' Espacio 1 ocupado: {datos}cm')
                    #Se llama a la funcion que ocupa espacios:
                    #ocupar_desocupar(espacio1,1)
                    canales[0].value = 1
                else:
                    #print(' Espacio 1 desocupado')
                    #Se llama a la funcion que desocupa espacios
                    #ocupar_desocupar(espacio1,0)
                    canales[0].value = 0
            if cont == 4: #Segundo espacio
                if datos <= 5: #Si la distancia menor/igual a 5
                    #print(f' Espacio 2 ocupado: {datos}cm')
                    #Se llama a la funcion que ocupa espacios:
                    #ocupar_desocupar(espacio2,1)
                    canales[1].value = 1
                else:
                    #print(' Espacio 2 desocupado')
                    #Se llama a la funcion que desocupa espacios:
                    #ocupar_desocupar(espacio2,0)
                    canales[1].value = 0
            if cont == 6: #Tercer espacio
                if datos <= 3: #Si la distancia menor/igual a 3
                    #print(f' Espacio 3 ocupado: {datos}cm')
                    #Se llama a la funcion que ocupa espacios:
                    #ocupar_desocupar(espacio3,1)
                    canales[2].value = 1
                else:
                    #print(' Espacio 3 desocupado')
                    #Se llama a la funcion que desocupa espacios:
                    #ocupar_desocupar(espacio3,0)
                    canales[2].value = 0
            cont+=1
            if cont == 7:
                cont = 1