import mysql.connector as mysql #BASE DE DATOS MYSQL
import bcrypt

#Lineas de arduino comentadas: 17, 95-111, 209-245, 407, 457, 493-494 

#ser = serial.Serial('COM3',9600) #Regresa los datos de conexion con Arduino (puerto,9600 default)

def isMysqlRunning() -> bool:
    try:
        connection = mysql.connect(
            host="localhost",
            user="root",
            password="password"
        )
        if (connection.is_connected()):
            connection.close()
            return True
        else:
            connection.close()
            return False
    except Exception as e:
        raise e


def connect() -> mysql.connection:
    try:
        connection = mysql.connect(
            host="localhost",
            user="root",
            password="password",
            database="parking"
        )
        return connection
    except Exception as e:
        raise e

def createDB():
    conn = mysql.connect(
            host="localhost",
            user="root",
            password="password"
        )
    cursor = conn.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS parking;")
    conn.commit()
    conn.close()

def createTableEspacio():
    conn = connect()
    cursor = conn.cursor() #Conecta con una consulta
    cursor.execute("""CREATE TABLE IF NOT EXISTS espacio (
                        no_cajon VARCHAR(5),
                        estado BOOLEAN DEFAULT FALSE,
                        fecha_hora TIMESTAMP DEFAULT NULL,
                        direccion VARCHAR(8),
                        tipo VARCHAR(10),
                        discapacitado BOOLEAN DEFAULT FALSE,
                        cord_x INT,
                        cord_y INT,
                        id_espacio INTEGER AUTO_INCREMENT,
                        asignado BOOLEAN DEFAULT FALSE,
                        PRIMARY KEY(id_espacio)
                        );
    """)
    conn.commit() #Realiza cambios
    conn.close()
    

def createTableRevokedTokens():
    conn = connect()
    cursor = conn.cursor() #Conecta con una consulta
    cursor.execute("""CREATE TABLE IF NOT EXISTS revockedTokens(
                      id INTEGER PRIMARY KEY AUTOINCREMENT,
                      jti TEXT UNIQUE,
                      revoked_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                      );
    """)
    conn.commit() #Realiza cambios
    conn.close()

def createTableAdmin():
    conn = connect()
    cursor = conn.cursor() #Conecta con una consulta
    cursor.execute("""CREATE TABLE IF NOT EXISTS  admin(
                      RFC varchar(13),
                      nombre varchar(30),
                      contrasena varchar(32),
                      CURP varchar(18),
                      primary key(RFC)
                      );
    """)
    conn.commit() #Realiza cambios
    #Se inserta el primer admin por default 
    #default_password = bcrypt.hashpw('1234'.encode('utf-8'), bcrypt.gensalt())
    cursor.execute("""INSERT INTO admin values('XAXX010101000','admin','1234','XAXX01010X000X1010');
    """)
    conn.commit() #Realiza cambios
    conn.close()

def setupMysql_docker() -> None:
    try:
        createDB()
        createTableEspacio()
        createTableAdmin()
    except Exception as e:
        raise e

def hashpassword(passwd: str) -> str:
    return bcrypt.hashpw(passwd.encode('utf-8'), bcrypt.gensalt())

def insertEspacio(next_espacio: str, direc: str, tipo: str, cord_x:int, cord_y:int):
    conn = connect()
    cursor = conn.cursor() #Conecta con una consulta
    cursor.execute("INSERT INTO espacio(no_cajon,direccion,tipo,cord_x,cord_y) VALUES (%s,%s,%s,%s,%s)",
                   (next_espacio, direc, tipo, cord_x, cord_y))
    conn.commit() #Realiza cambios
    conn.close()


# TODO: Pendiente
def insertFilaDEspacio():
    conn = connect()
    cursor = conn.cursor() #Conecta con una consulta
    cursor.execute("SELECT MAX(seccion) FROM espacio")
    conn.commit()
    ultimaSeccion = cursor.fetchone()
    nuevaSeccion = chr(ord(ultimaSeccion[0])+1) #chr convert to ASCII ord convert to number
    cursor.execute("SELECT COUNT(*) FROM espacio WHERE seccion=%s", ultimaSeccion)
    conn.commit()#Realiza cambios
    numeroColumnas = int(cursor.fetchone()[0])
    conn.close()
    
    for i in range(numeroColumnas):
        insertEspacio(f"{nuevaSeccion}{i}")
    
    



def obtenerEspacio() -> list:
    conn = connect()
    cursor = conn.cursor() #Conecta con una consulta
    cursor.execute("SELECT MIN(no_cajon) FROM espacio WHERE estado=0 AND discapacitado=0 AND tipo='lugar' AND asignado=0")
    espacio = cursor.fetchone()
    conn.close()
    return espacio
    
def obtenerEspacioDiscapacitado() -> list:
    conn = connect()
    cursor = conn.cursor() #Conecta con una consulta
    cursor.execute("SELECT MIN(no_cajon) FROM espacio WHERE estado=0 AND discapacitado=1 AND tipo='lugar' AND asignado=0")
    espacio = cursor.fetchone()
    conn.close()
    return espacio






def updateDiscapacitado(espacio):
    conn = connect()
    cursor = conn.cursor() #Conecta con una consulta
    cursor.execute("UPDATE espacio SET discapacitado = %s where no_cajon = %s",(1,espacio))
    #Actualiza los espacios para discapacitados
    conn.commit() #Realiza cambios
    conn.close()

def deleteEspacio(ant_espacio):
    conn = connect()
    cursor = conn.cursor() #Conecta con una consulta
    cursor.execute("DELETE FROM espacio where no_cajon ='"+str(ant_espacio)+"'")
    conn.commit() #Realiza cambios
    conn.close()

def selectCountEspacios():
    conn = connect()
    cursor = conn.cursor() #Conecta con una consulta
    cursor.execute("""SELECT COUNT(*) FROM espacio;
    """) #Obtiene la cantidad de espacios que hay en el parking
    datos = cursor.fetchall() #Regresa los datos de la consulta (Los lee y los regresa)
    conn.commit() #Realiza cambios
    conn.close()
    return datos

# TODO: Revisar si esta funcion sigue siendo necesaria (UI)
def espacio_discapacitado():
    conn = connect()
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
    conn = connect()
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
    return (disc1[0][0],disc2[0][0],disc3[0][0]) 
    
    

def ocupar_desocupar(espacio: str, estado: bool, fecha_hora: str):
    conn = connect()
    cursor = conn.cursor() #Conecta con una consulta
    if estado:
        cursor.execute("UPDATE espacio SET estado = %s, fecha_hora = %s where no_cajon = %s",(estado,fecha_hora,espacio))
    else:
        cursor.execute("UPDATE espacio SET estado = %s, fecha_hora = NULL where no_cajon = %s",(estado,espacio))
    #Actualiza el estado de un espacio
    conn.commit() #Realiza cambios
    conn.close()

def setAsignar(espacio: str, asignación: int):
    conn = connect()
    cursor = conn.cursor() #Conecta con una consulta
    cursor.execute("UPDATE espacio SET asignado = %s where no_cajon = %s",(asignación,espacio))
    #Actualiza el estado de un espacio
    conn.commit() #Realiza cambios
    conn.close()



def selectEspacios():
    conn = connect()
    cursor = conn.cursor() #Conecta con una consulta
    cursor.execute("""SELECT * FROM espacio;
    """) #Obtiene todos los espacios del parking
    datos = cursor.fetchall() #Regresa los datos de la consulta (Los lee y los regresa)
    conn.commit() #Realiza cambios
    conn.close()
    return datos
    
def selectEspacio(espacio):
    conn = connect()
    cursor = conn.cursor() #Conecta con una consulta
    cursor.execute("SELECT * FROM espacio where no_cajon = '"+str(espacio)+"'")
    #Obtiene un espacio del parking 
    datos = cursor.fetchall() #Regresa los datos de la consulta (Los lee y los regresa)
    conn.commit() #Realiza cambios
    conn.close()
    return datos    

def consultarEspacio(espacio):
    conn = connect()
    cursor = conn.cursor() #Conecta con una consulta
    cursor.execute("SELECT estado FROM espacio where no_cajon = '"+str(espacio)+"'")
    #Obtiene el estado del espacio (desocupado/0, ocupado/1)
    datos = cursor.fetchall() #Regresa los datos de la consulta (Los lee y los regresa)
    conn.commit() #Realiza cambios
    conn.close()
    return datos    

def consultarEspacioAsignado(espacio):
    conn = connect()
    cursor = conn.cursor() #Conecta con una consulta
    cursor.execute("SELECT estado,asignado FROM espacio where no_cajon = '"+str(espacio)+"'")
    #Obtiene el estado del espacio (desocupado/0, ocupado/1)
    datos = cursor.fetchall() #Regresa los datos de la consulta (Los lee y los regresa)
    conn.commit() #Realiza cambios
    conn.close()
    return datos 

def validarEspacio(noCajon, noCajonAnterior = ""):
    conn = connect()
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
    conn = connect()
    cursor = conn.cursor() #Conecta con una consulta
    cursor.execute("SELECT * FROM espacio WHERE cord_x = " + str(x) + " AND cord_y = " + str(y))
    datos = cursor.fetchall() #Regresa los datos de la consulta (Los lee y los regresa)
    conn.commit() #Realiza cambios
    conn.close()
    return datos

def updateEspacio(no_cajon, estado, fecha_hora, direccion, tipo, discapacitado, x, y):
    conn = connect()
    cursor = conn.cursor() #Conecta con una consulta
    cursor.execute("SELECT * FROM espacio where cord_x = " + str(x) + " AND cord_y = " + str(y))
    espacio = cursor.fetchall()
    if espacio:
        # El espacio ya EXISTSe, actualizamos
        cursor.execute("UPDATE espacio SET " +
                       "no_cajon = %s, " +
                       "estado = %s, " +
                       "fecha_hora = %s, " +
                       "direccion = %s, " +
                       "tipo = %s, " +
                       "discapacitado = %s " +
                       "WHERE cord_x = %s AND cord_y = %s", 
                       (no_cajon, estado, fecha_hora, direccion, tipo, discapacitado, x, y)
                    )
    else:
        # Si no ps lo agregamos
        cursor.execute("INSERT INTO espacio(no_cajon,direccion,tipo,discapacitado,cord_x,cord_y) VALUES (%s,%s,%s,%s,%s,%s)",
                   (no_cajon, direccion, tipo, discapacitado, x, y))
    conn.commit() #Realiza cambios
    conn.close()

def eliminarTodoEspacios():
    conn = connect()
    cursor = conn.cursor() #Conecta con una consulta
    cursor.execute("DELETE FROM espacio")
    conn.commit() #Realiza cambios
    conn.close()

def LoginAdmin(user,passw):
    conn = connect()
    cursor = conn.cursor() #Conecta con una consulta
    cursor.execute("SELECT RFC FROM admin where nombre = '"+str(user)+"' and contrasena = '"+str(passw)+"'" )
    #Obtiene el admin dado en Login
    datos = cursor.fetchone() #Regresa los datos de la consulta (Los lee y los regresa)
    conn.commit() #Realiza cambios
    conn.close()
    return datos  

def insertAdmin(RFC,name,passw,CURP):
    conn = connect()
    cursor = conn.cursor() #Conecta con una consulta
    cursor.execute("INSERT INTO admin(RFC,nombre,contrasena,CURP) VALUES (%s,%s,%s,%s)",(RFC,name,passw,CURP))
    conn.commit() #Realiza cambios
    conn.close()

def deleteAdmin(RFC):
    conn = connect()
    cursor = conn.cursor() #Conecta con una consulta
    cursor.execute("DELETE FROM admin where RFC ='"+str(RFC)+"'")
    conn.commit() #Realiza cambios
    conn.close()

def updateAdmin(RFC,name,curp, nuevoRFC):
    conn = connect()
    cursor = conn.cursor() #Conecta con una consulta
    cursor.execute("UPDATE admin SET nombre = %s, CURP = %s, RFC = %s where RFC = %s",
                   (name, curp, nuevoRFC, RFC))
    conn.commit() #Realiza cambios
    conn.close()

def updateAdminPassword(password, RFC):
    conn = connect()
    cursor = conn.cursor() #Conecta con una consulta
    cursor.execute("UPDATE admin SET contrasena = %s where RFC = %s", (password, RFC))
    conn.commit() #Realiza cambios
    conn.close()

def consultarAdmin(RFC):
    conn = connect()
    cursor = conn.cursor() #Conecta con una consulta
    cursor.execute("SELECT RFC,nombre,CURP FROM admin where RFC = '"+str(RFC)+"'")
    #Obtiene todos los espacios del parking
    datos = cursor.fetchall() #Regresa los datos de la consulta (Los lee y los regresa)
    conn.commit() #Realiza cambios
    conn.close()
    return datos

def validarNombre(nombre, nombreAnterior = ""):
    conn = connect()
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
    conn = connect()
    cursor = conn.cursor() #Conecta con una consulta
    cursor.execute("SELECT RFC,nombre,CURP FROM admin WHERE nombre != 'admin'")
    #Obtiene todos los espacios del parking
    datos = cursor.fetchall() #Regresa los datos de la consulta (Los lee y los regresa)
    conn.commit() #Realiza cambios
    conn.close()
    return datos     

def selectCountAdmin():
    conn = connect()
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
    conn = connect()
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

