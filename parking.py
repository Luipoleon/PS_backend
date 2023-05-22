import sqlite3 as sql #BASE DE DATOS SQLITE 
import random    #GENERADOR ALEATORIO
import qrcode    #GENERADOR QR
from PIL import Image   #GENERADOR DE IMAGEN desde pillow
import cv2              #LECTOR QR EN CAMARA
import numpy as np      #CALCULO NÚMERICO
from fpdf import FPDF  #GENERADOR DE PDF
import datetime as dt  #FECHA, HORA SISTEMA
import getpass as gtp  #GENERADOR CONTRASEÑA SIN VISTA 
import cryptocode as cryp    #CIFRADO Y DESCIFRADO
import serial                #CONEXION CON ARDUINO 
from time import sleep    #GENERA TIEMPOS DE ESPERA
import threading #Permite realizar subprocesos o ejecutar funciones simultaneamente 
import datetime #fecha y hora


#Lineas de arduino comentadas: 17, 95-111, 209-245, 407, 457, 493-494 

#ser = serial.Serial('COM3',9600) #Regresa los datos de conexion con Arduino (puerto,9600 default)



def createDB():
    conn = sql.connect("myparking.db")
    conn.commit()
    conn.close()

def createTableEspacio():
    conn = sql.connect("myparking.db")
    cursor = conn.cursor() #Conecta con una consulta
    cursor.execute("""CREATE TABLE espacio (
                        id_espacio INTEGER PRIMARY KEY,
                        no_cajon VARCHAR(5),
                        estado BOOLEAN DEFAULT FALSE,
                        fecha_hora TIMESTAMP DEFAULT NULL,
                        direccion VARCHAR(8),
                        tipo VARCHAR(10),
                        discapacitado BOOLEAN DEFAULT FALSE,
                        cord_x INT,
                        cord_y INT
                        );
    """)
    conn.commit() #Realiza cambios
    conn.close()
    

def createTableRevokedTokens():
    conn = sql.connect("myparking.db")
    cursor = conn.cursor() #Conecta con una consulta
    cursor.execute("""CREATE TABLE revockedTokens(
                      id INTEGER PRIMARY KEY AUTOINCREMENT,
                      jti TEXT UNIQUE,
                      revoked_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                      );
    """)
    conn.commit() #Realiza cambios
    conn.close()

def createTableAdmin():
    conn = sql.connect("myparking.db")
    cursor = conn.cursor() #Conecta con una consulta
    cursor.execute("""CREATE TABLE admin(
                      RFC varchar(13),
                      nombre varchar(30),
                      contrasena varchar(32),
                      CURP varchar(18),
                      primary key(RFC)
                      );
    """)
    conn.commit() #Realiza cambios
    #Se inserta el primer admin por default 
    cursor.execute("""INSERT INTO admin values('XAXX010101000','admin','1234','XAXX01010X000X1010');
    """)
    conn.commit() #Realiza cambios
    conn.close()

def insertEspacio(next_espacio: str, direc: str, tipo: str, cord_x:int, cord_y:int):
    conn = sql.connect("myparking.db")
    cursor = conn.cursor() #Conecta con una consulta
    cursor.execute("INSERT INTO espacio(no_cajon,direccion,tipo,cord_x,cord_y) VALUES (?,?,?,?,?)",
                   (next_espacio, direc, tipo, cord_x, cord_y))
    conn.commit() #Realiza cambios
    conn.close()


# TODO: Pendiente
def insertFilaDEspacio():
    conn = sql.connect("myparking.db")
    cursor = conn.cursor() #Conecta con una consulta
    cursor.execute("SELECT MAX(seccion) FROM espacio")
    conn.commit()
    ultimaSeccion = cursor.fetchone()
    nuevaSeccion = chr(ord(ultimaSeccion[0])+1) #chr convert to ASCII ord convert to number
   
    cursor.execute("SELECT COUNT(*) FROM espacio WHERE seccion=?", ultimaSeccion)
    conn.commit()#Realiza cambios
    numeroColumnas = int(cursor.fetchone()[0])
    conn.close()
    
    for i in range(numeroColumnas):
        insertEspacio(f"{nuevaSeccion}{i}")
    
    




def obtenerEspacio() -> list:
    conn = sql.connect("myparking.db")
    cursor = conn.cursor() #Conecta con una consulta
    cursor.execute("SELECT MIN(no_cajon) FROM espacio WHERE estado=0 AND discapacitado=0 AND tipo='lugar'")
    espacio = cursor.fetchone()
    conn.close()
    return espacio
    
def obtenerEspacioDiscapacitado() -> list:
    conn = sql.connect("myparking.db")
    cursor = conn.cursor() #Conecta con una consulta
    cursor.execute("SELECT MIN(no_cajon) FROM espacio WHERE estado=0 AND discapacitado=1 AND tipo='lugar'")
    espacio = cursor.fetchone()
    conn.close()
    return espacio






def updateDiscapacitado(espacio):
    conn = sql.connect("myparking.db")
    cursor = conn.cursor() #Conecta con una consulta
    cursor.execute("UPDATE espacio SET discapacitado = ? where no_cajon = ?",(1,espacio))
    #Actualiza los espacios para discapacitados
    conn.commit() #Realiza cambios
    conn.close()

def deleteEspacio(ant_espacio):
    conn = sql.connect("myparking.db")
    cursor = conn.cursor() #Conecta con una consulta
    cursor.execute("DELETE FROM espacio where no_cajon ='"+str(ant_espacio)+"'")
    conn.commit() #Realiza cambios
    conn.close()

def selectCountEspacios():
    conn = sql.connect("myparking.db")
    cursor = conn.cursor() #Conecta con una consulta
    cursor.execute("""SELECT COUNT(*) FROM espacio;
    """) #Obtiene la cantidad de espacios que hay en el parking
    datos = cursor.fetchall() #Regresa los datos de la consulta (Los lee y los regresa)
    conn.commit() #Realiza cambios
    conn.close()
    return datos

# TODO: Revisar si esta funcion sigue siendo necesaria (UI)
def espacio_discapacitado():
    conn = sql.connect("myparking.db")
    cursor = conn.cursor() #Conecta con una consulta
    cursor.execute("SELECT MIN(no_cajon) FROM espacio where no_cajon > (select MIN(no_cajon) FROM espacio)")
    #Selecciona al segundo espacio minimo 
    disc2 = cursor.fetchall() #Regresa los datos de la consulta (Los lee y los regresa)
    conn.commit() #Realiza cambios
    cursor.execute("SELECT MIN(no_cajon) FROM espacio")
    #Selecciona al espacio minimo 
    disc1 = cursor.fetchall() 
    conn.close()
    updateDiscapacitado(disc1[0][0]) #Primer lugar mas cercano discapacitado 1
    updateDiscapacitado(disc2[0][0]) #Segundo lugar mas cercano discapaticado 2 

    
def espaciosSensor():
    #Conexion con la BD
    conn = sql.connect("myparking.db")
    cursor = conn.cursor() #Conecta con una consulta
    cursor.execute("SELECT MIN(no_cajon) FROM espacio where no_cajon > (select MIN(no_cajon) FROM espacio where no_cajon > (select MIN(no_cajon) FROM espacio))")
#Selecciona al tercer espacio minimo 
    disc3 = cursor.fetchall() #Regresa los datos de la consulta (Los lee y los regresa)
    cursor.execute("SELECT MIN(no_cajon) FROM espacio where no_cajon > (select MIN(no_cajon) FROM espacio)")
#Selecciona al segundo espacio minimo 
    disc2 = cursor.fetchall() #Regresa los datos de la consulta (Los lee y los regresa)
    conn.commit() #Realiza cambios
    cursor.execute("SELECT MIN(no_cajon) FROM espacio")
#Selecciona el primer espacio minimo 
    disc1 = cursor.fetchall() 
    conn.close()
    return {disc1[0][0],disc2[0][0],disc3[0][0]} 
    
    

def ocupar_desocupar(espacio: str, estado: bool, fecha_hora: str):
    conn = sql.connect("myparking.db")
    cursor = conn.cursor() #Conecta con una consulta
    if estado:
        cursor.execute("UPDATE espacio SET estado = ?, fecha_hora = ? where no_cajon = ?",(estado,fecha_hora,espacio))
    else:
        cursor.execute("UPDATE espacio SET estado = ?, fecha_hora = NULL where no_cajon = ?",(estado,espacio))
    #Actualiza el estado de un espacio
    conn.commit() #Realiza cambios
    conn.close()

def selectEspacios():
    conn = sql.connect("myparking.db")
    cursor = conn.cursor() #Conecta con una consulta
    cursor.execute("""SELECT * FROM espacio;
    """) #Obtiene todos los espacios del parking
    datos = cursor.fetchall() #Regresa los datos de la consulta (Los lee y los regresa)
    conn.commit() #Realiza cambios
    conn.close()
    return datos
    
def selectEspacio(espacio):
    conn = sql.connect("myparking.db")
    cursor = conn.cursor() #Conecta con una consulta
    cursor.execute("SELECT * FROM espacio where no_cajon = '"+str(espacio)+"'")
    #Obtiene un espacio del parking 
    datos = cursor.fetchall() #Regresa los datos de la consulta (Los lee y los regresa)
    conn.commit() #Realiza cambios
    conn.close()
    return datos    

def consultarEspacio(espacio):
    conn = sql.connect("myparking.db")
    cursor = conn.cursor() #Conecta con una consulta
    cursor.execute("SELECT estado FROM espacio where no_cajon = '"+str(espacio)+"'")
    #Obtiene el estado del espacio (desocupado/0, ocupado/1)
    datos = cursor.fetchall() #Regresa los datos de la consulta (Los lee y los regresa)
    conn.commit() #Realiza cambios
    conn.close()
    return datos    

def validarEspacio(noCajon, noCajonAnterior = ""):
    conn = sql.connect("myparking.db")
    cursor = conn.cursor() #Conecta con una consulta
    if noCajonAnterior:
        cursor.execute("SELECT * FROM espacio where no_cajon = '"+str(noCajon)+"' AND no_cajon != '" + str(noCajonAnterior) + "'")
    else:   
        cursor.execute("SELECT * FROM espacio where no_cajon = '"+str(noCajon)+"'")
    #Obtiene todos los espacios del parking
    datos = cursor.fetchall() #Regresa los datos de la consulta (Los lee y los regresa)
    conn.commit() #Realiza cambios
    conn.close()
    return datos 

def consultarCajonXY(x, y):
    conn = sql.connect("myparking.db")
    cursor = conn.cursor() #Conecta con una consulta
    cursor.execute("SELECT * FROM espacio WHERE cord_x = " + str(x) + " AND cord_y = " + str(y))
    datos = cursor.fetchall() #Regresa los datos de la consulta (Los lee y los regresa)
    conn.commit() #Realiza cambios
    conn.close()
    return datos

def updateEspacio(no_cajon, estado, fecha_hora, direccion, tipo, discapacitado, x, y):
    conn = sql.connect("myparking.db")
    cursor = conn.cursor() #Conecta con una consulta
    cursor.execute("SELECT * FROM espacio where cord_x = " + str(x) + " AND cord_y = " + str(y))
    espacio = cursor.fetchall()
    if espacio:
        # El espacio ya existe, actualizamos
        cursor.execute("UPDATE espacio SET " +
                       "no_cajon = ?, " +
                       "estado = ?, " +
                       "fecha_hora = ?, " +
                       "direccion = ?, " +
                       "tipo = ?, " +
                       "discapacitado = ? " +
                       "WHERE cord_x = ? AND cord_y = ?", 
                       (no_cajon, estado, fecha_hora, direccion, tipo, discapacitado, x, y)
                    )
    else:
        # Si no ps lo agregamos
        cursor.execute("INSERT INTO espacio(no_cajon,direccion,tipo,discapacitado,cord_x,cord_y) VALUES (?,?,?,?,?,?)",
                   (no_cajon, direccion, tipo, discapacitado, x, y))
    conn.commit() #Realiza cambios
    conn.close()

def eliminarTodoEspacios():
    conn = sql.connect("myparking.db")
    cursor = conn.cursor() #Conecta con una consulta
    cursor.execute("DELETE FROM espacio")
    conn.commit() #Realiza cambios
    conn.close()

def LoginAdmin(user,passw):
    conn = sql.connect("myparking.db")
    cursor = conn.cursor() #Conecta con una consulta
    cursor.execute("SELECT RFC FROM admin where nombre = '"+str(user)+"' and contrasena = '"+str(passw)+"'" )
    #Obtiene el admin dado en Login
    datos = cursor.fetchone() #Regresa los datos de la consulta (Los lee y los regresa)
    conn.commit() #Realiza cambios
    conn.close()
    return datos  

def insertAdmin(RFC,name,passw,CURP):
    conn = sql.connect("myparking.db")
    cursor = conn.cursor() #Conecta con una consulta
    cursor.execute("INSERT INTO admin(RFC,nombre,contrasena,CURP) VALUES (?,?,?,?)",(RFC,name,passw,CURP))
    conn.commit() #Realiza cambios
    conn.close()

def deleteAdmin(RFC):
    conn = sql.connect("myparking.db")
    cursor = conn.cursor() #Conecta con una consulta
    cursor.execute("DELETE FROM admin where RFC ='"+str(RFC)+"'")
    conn.commit() #Realiza cambios
    conn.close()

def updateAdmin(RFC,name,curp, nuevoRFC):
    conn = sql.connect("myparking.db")
    cursor = conn.cursor() #Conecta con una consulta
    cursor.execute("UPDATE admin SET nombre = ?, CURP = ?, RFC = ? where RFC = ?",
                   (name, curp, nuevoRFC, RFC))
    conn.commit() #Realiza cambios
    conn.close()

def updateAdminPassword(password, RFC):
    conn = sql.connect("myparking.db")
    cursor = conn.cursor() #Conecta con una consulta
    cursor.execute("UPDATE admin SET contrasena = ? where RFC = ?", (password, RFC))
    conn.commit() #Realiza cambios
    conn.close()

def consultarAdmin(RFC):
    conn = sql.connect("myparking.db")
    cursor = conn.cursor() #Conecta con una consulta
    cursor.execute("SELECT RFC,nombre,CURP FROM admin where RFC = '"+str(RFC)+"'")
    #Obtiene todos los espacios del parking
    datos = cursor.fetchall() #Regresa los datos de la consulta (Los lee y los regresa)
    conn.commit() #Realiza cambios
    conn.close()
    return datos

def validarNombre(nombre, nombreAnterior = ""):
    conn = sql.connect("myparking.db")
    cursor = conn.cursor() #Conecta con una consulta
    if nombreAnterior:
        cursor.execute("SELECT * FROM admin where nombre = '"+str(nombre)+"' AND nombre != '" + str(nombreAnterior) + "'")
    else:   
        cursor.execute("SELECT * FROM admin where nombre = '"+str(nombre)+"'")
    #Obtiene todos los espacios del parking
    datos = cursor.fetchall() #Regresa los datos de la consulta (Los lee y los regresa)
    conn.commit() #Realiza cambios
    conn.close()
    return datos

def selectAllAdmin():
    conn = sql.connect("myparking.db")
    cursor = conn.cursor() #Conecta con una consulta
    cursor.execute("SELECT RFC,nombre,CURP FROM admin WHERE nombre != 'admin'")
    #Obtiene todos los espacios del parking
    datos = cursor.fetchall() #Regresa los datos de la consulta (Los lee y los regresa)
    conn.commit() #Realiza cambios
    conn.close()
    return datos     

def selectCountAdmin():
    conn = sql.connect("myparking.db")
    cursor = conn.cursor() #Conecta con una consulta
    cursor.execute("SELECT COUNT(*) FROM admin")
    #Obtiene todos los espacios del parking
    datos = cursor.fetchall() #Regresa los datos de la consulta (Los lee y los regresa)
    conn.commit() #Realiza cambios
    conn.close()
    # Regresa el resultado del conteo, el cual esta dentro de una matriz de listas y tuplas
    return datos[0][0]

def parkingFull():
    can_esp = selectCountEspacios()
    conn = sql.connect("myparking.db")
    cursor = conn.cursor() #Conecta con una consulta
    cursor.execute("""SELECT count(ID) FROM espacio where estado = 1;
    """) #Obtiene la cantidad de espacios que hay en el parking ocupados
    datos = cursor.fetchall() #Regresa los datos de la consulta (Los lee y los regresa)
    conn.commit() #Realiza cambios
    if can_esp[0][0] != 0:
         porcentaje = int((datos[0][0]*100)/(can_esp[0][0]))
    else:
         porcentaje = 0
    conn.close()
    return porcentaje
     
"""
def validarEspacioOcupado(espacio1,espacio2,espacio3): #Validacion de espacios por sensor
     #print(' -Por favor, espere...')   
     cont = 1
     sleep(5)
     while True:      #Regresa la distancia del objeto detectado al sensor en tiempo real 
        if(ser.inWaiting()>0):
            mydata = ser.readline()
            try:
                 datos = float(mydata)
            except ValueError:
                datos = float(mydata.replace('\r\n',"0")) 
            if cont == 2:
                if datos <= 10:
                    #print(f' Espacio 1 ocupado: {datos}cm')
                    ocupar_desocupar(espacio1,1)
                else:
                    #print(' Espacio 1 desocupado')
                    ocupar_desocupar(espacio1,0)
            if cont == 4:
                if datos <= 10:
                    #print(f' Espacio 2 ocupado: {datos}cm')
                    ocupar_desocupar(espacio2,1)
                else:
                    #print(' Espacio 2 desocupado')
                    ocupar_desocupar(espacio2,0)
            if cont == 6:
                if datos <= 10:
                    #print(f' Espacio 3 ocupado: {datos}cm')
                    ocupar_desocupar(espacio3,1)
                else:
                    #print(' Espacio 3 desocupado')
                    ocupar_desocupar(espacio3,0)
            cont+=1
            if cont == 7:
                cont = 1
"""       

def CRUDadmins():
    print("""ADMIN
            1) Agregar administrador
            2) Consultar administrador
            3) Modificar administrador
            4) Eliminar administrador
            5) Ir a espacios
            6) Salir de admin
            """)
    opca = int(input('-Opcion: '))
    if opca == 1:
        rfc = input('-RFC: ')
        name = input('nombre: ')
        passw = gtp.getpass('password: ')
        curp = input('-CURP: ')
        insertAdmin(rfc,name,passw,curp)
    if opca == 2:
            rfc = input('-RFC del admin a consultar: ')
            existe = consultarAdmin(rfc)
            if len(existe) > 0:
                 print(f'RFC: {existe[0][0]} CURP: {existe[0][1]}')
            else:
                 print('No existe el RFC del admin dado.')
    if opca == 3:
            rfc = input('-RFC del admin a modificar: ')
            existe = consultarAdmin(rfc)
            if len(existe) > 0:
                 name = input('Nuevo nombre: ')
                 passw = gtp.getpass('Nueva contraseña: ')
                 updateAdmin(rfc,name,passw)
            else:
                 print('No existe el RFC del admin dado.')
    if opca == 4:
            rfc = input('-RFC del admin a eliminar: ')
            if rfc == 'XAXX010101000':
                print('No se puede eliminar al admin por defecto.')
            else:
                existe = consultarAdmin(rfc)
                if len(existe) > 0:
                    deleteAdmin(rfc)
                else:
                    print('No existe el RFC del admin dado.')        
    if opca == 5:
          CRUDespacios()
    if opca == 6:
          main()
    if opca < 1 and opca > 6:
        print('Opcion no valida.')
    CRUDadmins()

def CRUDespacios():
    print("""ADMIN
            1) Agregar espacio
            2) Consultar espacio
            3) Ocupar/Desocupar espacio
            4) Eliminar espacio
            5) Ir a administradores
            6) Salir de admin
            7) Visualizar espacios (No implementado)
            """)
    opca = int(input('-Opcion: '))
    if opca == 1:
        cantidad = int(input('-Ingresa cantidad de espacios a añadir: '))
        for i in range(cantidad):
            cant_espacios = selectCountEspacios()
            next_espacio = chr(65)+str(cant_espacios[0][0])
            insertEspacio(next_espacio)
    if opca == 2:
                consulta_espacio = input('-Ingresa el espacio a consultar: ')
                existe = selectEspacio(consulta_espacio)
                if len(existe)>0:
                    print(f"""Espacio ----- Estado (0/desocupado, 1/ocupado) ----- Discapacitados (0/no, 1/si)
                    Espacio: {existe[0][0]} Estado: {existe[0][1]} Discapacitados: {existe[0][2]}""")
                else:
                    print('El espacio no existe.')
    if opca == 3:
            espacio = input('-Ingrese espacio: ')
            estado = int(input('-Elija estado (ocupado/1),(desocupado/0): '))
            existe = selectEspacio(espacio)
            if len(existe) > 0:
                ocupar_desocupar(espacio,estado)
                print('Espacio modificado.')
            else:
                print('El espacio no existe.')
    if opca == 4:
            cantidad = int(input('-Ingresa cantidad de espacios a eliminar: '))
            for i in range(cantidad):
                cant_espacios = selectCountEspacios()
                if cant_espacios[0][0] == 0:
                     print('El parking no contiene espacios.')
                else:
                     ant_espacio = chr(65)+str(cant_espacios[0][0]-1) 
                     deleteEspacio(ant_espacio)
    if opca == 5:
          CRUDadmins()
    if opca == 6:
          main()
    if opca == 7:
        print('Visualizacion de espacios') #No implementado
    if opca < 1 and opca > 7:
        print('Opcion no valida.')
    CRUDespacios()

def main():
    #createDB()
    #createTableEspacio()
    #createTableAdmin()
    while True:
        espacio_discapacitado()  #Actualiza los primeros 2 espacios del parking para discapacitados

        print("""< USUARIO >
        1) Selección de lugar 
        2) Escanear QR
        3) ADMIN
        4) Exit
        """)
        opc = int(input('-Opcion: '))

        if opc == 1:
            seccion = int(input('Selecciona una seccion (normal/0),(discapacitado/1): '))
            parking = selectEspacios() #Selecciona todos los espacios actuales 
            espacios_normales = []
            espacios_discapacitados = []
            dis= 0
            for espacio in parking:
                if dis < 2: #Cantidad de espacios para discapacitados
                    espacios_discapacitados.append(espacio[0])
                    dis+=1
                else:
                    espacios_normales.append(espacio[0])
            print(espacios_discapacitados)
            print(espacios_normales)
            
            if seccion == 0:
                espacio_asignado = random.choice(espacios_normales) #Espacio asignado aleatorio
                secc = 'Normal'
            else:
                espacio_asignado = random.choice(espacios_discapacitados) #Espacio asignado aleatorio
                secc = 'Discapacitados'
                #--------------------------------------------
                #Validación de la credencial para discapacitados (No implementado)
                #--------------------------------------------
            #Se valida si el espacio esta ocupado (O si no cumple la validación de discapacitado)
            est_espacio = consultarEspacio(espacio_asignado) 
            if est_espacio[0][0] != 0:
                print(f'El espacio {espacio_asignado} esta ocupado')
            else:
                print('Lugar asignado: ',espacio_asignado)
                
                ocupar_desocupar(espacio_asignado,1) #Se ocupa el espacio 
            
                imagen = qrcode.make(espacio_asignado)     #SE GENERA EL CODIGO QR CON EL ESPACIO DADO
            
                archivo = open('Espacio.png','wb')  #CREA EL ARCHIVO CON EL NOMBRE DE LA IMAGEN
                imagen.save(archivo)    #GUARDA EL QR EN EL ARCHIVO DE LA IMAGEN
                archivo.close()         

                ruta_img = './'+'Espacio.png'   #SE GENERA LA RUTA
                Image.open(ruta_img).show()  #SE MUESTRA LA IMAGEN CON EL QR 
                #SUBE LA PLUMA PARA DEJAR PASAR
                #ser.write(str(100).encode())   #Modifica el angulo del servo para apertura
                #------------------------------------------------------------------
                #Se genera el PDF del ticket con la imagen del QR creado del espacio
                pdf = FPDF(orientation = 'P',unit='mm',format=(80,118)) #Nuevo PDF
                pdf.set_margins(4,10,4)
                pdf.add_page()

                fecha_sis = dt.date.today() #Obtiene la fecha actual
                hora_sis = dt.datetime.now().time() #Obtiene la hora actual

                fecha = str(fecha_sis.day)+'/'+str(fecha_sis.month)+'/'+str(fecha_sis.year)
                hora = str(hora_sis.hour)+':'+str(hora_sis.minute)+':'+str(hora_sis.second)

                #Encabezado y datos
                pdf.image('parkinglogo.png',15,5,w=50,h=15)
                pdf.ln(5)
                #pdf.multi_cell(0,5,'Parking Sites',0,'C',False)
                pdf.ln(8)
                pdf.set_font('Arial','',9)
                pdf.multi_cell(0,5,f'Fecha: {fecha}',0,'C',False)
                pdf.multi_cell(0,5,f'Hora/entrada: {hora}',0,'C',False)
                pdf.multi_cell(0,5,f'Sección: {secc}',0,'C',False)

                pdf.ln(1)
                pdf.cell(0,5,"--------------------------------------------------------",0,0,'C')
                pdf.ln(5)

                pdf.set_font('Arial','B',15)
                pdf.set_text_color(0,0,0)
                pdf.multi_cell(0,5,f'Cajón: {espacio_asignado}',0,'C',False)
                #QR CODE
                pdf.image('Espacio.png',5,50,w=70,h=70)
                pdf.output('Ticket.pdf') #PDF 
                
        if opc == 2:
            capture = cv2.VideoCapture(0) #Captura video
            while(capture.isOpened()):
                ret,frame = capture.read()

                if(cv2.waitKey(1) == ord('s')):
                    break
                qrDetector = cv2.QRCodeDetector()
                espacio_liberar,bbox,rectImage = qrDetector.detectAndDecode(frame)

                if len(espacio_liberar) > 0:
                    print(f'Espacio: {espacio_liberar}') 
                    cv2.imshow('webCam',rectImage) #Detecta espacio del QR
                    break
                else:
                    cv2.imshow('webCam',frame)
            #ser.write(str(100).encode())   #Modifica el angulo del servo para salida
            capture.release()
            cv2.destroyAllWindows()
            ocupar_desocupar(espacio_liberar,0) #Se desocupa el espacio leido
            
        if opc == 3:
            user = input('Usuario: ')
            passw = gtp.getpass('Contraseña: ')
            login = LoginAdmin(user,passw)
            #key = str(random.randint(1,100))+'PK'
            #pass_encoded = cryp.encrypt(passw,key)
            #print(pass_encoded)
            #pass_decoded = cryp.decrypt(pass_encoded,key)
            #print(pass_decoded)
            if len(login)>0:
                print(f"""Bienvenido {login[0][0]}
                1) Ir a administradores
                2) Ir a espacios
                """)
                if parkingFull() >= 75:     #Notifica si mas del 75% de Parking esta ocupado
                    print(f'>System: La capacidad del parking esta en {parkingFull()}% de ocupación.')
                opc = int(input('-Opcion: '))
                if opc == 1:
                    CRUDadmins()
                if opc == 2:
                    CRUDespacios()
                else:
                    print('Opcion invalida.')
            else:
                print('Datos incorrectos')
        if opc == 4:
             exit()
        if opc < 1 or opc > 4:
            print('Opcion invalida.')         

if __name__ =="__main__":
    #sensores = threading.Thread(target=espaciosSensor)  #Funcion a ejecutar simultaneamente 
    #sensores.start()   #Ejecuta la validacion de sensores
    main()
    
