from flask_restful import Api, Resource, request, reqparse
from flask import Flask, session
from flask_cors import CORS
from secrets import token_urlsafe
from datetime import datetime
from sensores import *
from multiprocessing import Value
from make_ticket import make_ticket
from datetime import datetime
import threading
import serial
from sys import argv

FLASK_DEBUG=1

arduino: serial.Serial
lugares_sensor: list
sensores_disponibles: bool
DATABASE: str
FAKESENSORS: bool

if 'fakesensors' in argv:
    FAKESENSORS = True
else:
    FAKESENSORS = False

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True # Requerido para no recibir codigo 500 por usar flask_restful
api = Api(app)
app.config['SECRET_KEY'] = '\xd9M\xe6\x05\xa1-\xe6\x18\x86q\x89\x86t\x16\x91>\x8c\xef\x97(\x1e\xd0an'
CORS(app)

if 'sqlite' in argv:
    from parking import *
    DATABASE = 'sqlite'
else:
    from parking_mysql import isMysqlRunning   
    try:
        if isMysqlRunning():     # Revisar si mysql esta disponible
            DATABASE = 'mysql'
            from parking_mysql import *
    except: # Usar sqlite como fallback
        DATABASE = 'sqlite'
        from parking import *

#Lugares de estacionamiento

class Lugar():
    def __init__(self,numCajon,estado,fecha_hora,direccion,tipo,discapacitado,x_pos,y_pos,id_lugar,asignado):
        self.numCajon = numCajon
        self.estado = estado
        if DATABASE == 'sqlite':
            self.fecha_hora = fecha_hora
        else:
            if fecha_hora != None:
                self.fecha_hora = fecha_hora.strftime('%Y-%m-%d %H:%M:%S')
            else:
                self.fecha_hora = None
        self.direccion = direccion
        self.tipo = tipo
        self.discapacitado = discapacitado
        self.x = x_pos
        self.y = y_pos
        self.id_lugar = id_lugar
        self.asignado = asignado
    #Convertir lugar en diccionario de python y asignarle nombres a los campos
    def diccionario(self):
        return {"no_cajon": self.numCajon, "estado": self.estado,
                "fecha_hora": self.fecha_hora, "direccion":self.direccion, "tipo":self.tipo,
                "discapacitado":self.discapacitado, "x":self.x, "y": self.y,
                "asignado":self.asignado}
       
#CRUD lugares

class InsertEspacio(Resource):
    response = {"estatus": 400, "mensaje": "Espacio no creado"}

    def post(self):
        if "sessionID" not in session:
            return {"mensaje":"No autorizado"},401

        espacioPOST = request.get_json()
        id = espacioPOST["no_cajon"]
        if(id and len(id)==2):
            espacio = selectEspacio(id)
            if(not espacio):
                direccion = espacioPOST["direccion"]
                tipo = espacioPOST["tipo"]
                cord_x = espacioPOST["x"]
                cord_y = espacioPOST["y"]
                insertEspacio(id,direccion,tipo,cord_x,cord_y)
                self.response["estatus"] = 201
                self.response["mensaje"] = "Espacio creado exitosamente"
                espacioNuevo = selectEspacio(id)
                lugar = Lugar(espacioNuevo[0][0],espacioNuevo[0][1],espacioNuevo[0][2],
                              espacioNuevo[0][3],espacioNuevo[0][4],espacioNuevo[0][5],
                              espacioNuevo[0][6],espacioNuevo[0][7],espacioNuevo[0][8],
                              espacioNuevo[0][9])
                response = lugar.diccionario() 
                return response, 201
            else:
                self.response["estatus"] = 500
                self.response["mensaje"] = "El ID no esta disponible"
                
        else:
            self.response["estatus"] = 500
            self.response["mensaje"] = "ID no válido"
        return self.response, 500
    
class UpdateEspacio(Resource):
    response: dict
    def post(self):
        if "sessionID" not in session:
            return {"mensaje":"No autorizado"},401
        
        codigo: int = 500
        mensaje: str = "Error desconocido"
        data = request.get_json()
        try:
            if len(data["no_cajon"]) > 0:
                espacio = consultarCajonXY(data["x"], data["y"])
                if espacio:
                    if validarEspacio(data["no_cajon"], espacio[0][0]):
                        codigo: int = 500
                        mensaje: str = "Este número de cajón ya existe"
                        return {"mensaje":"Este número de cajón ya existe"},500
                else:
                    if validarEspacio(data["no_cajon"]): 
                        codigo: int = 500
                        mensaje: str = "Este número de cajón ya existe"
                        return {"mensaje":"Este número de cajón ya existe"},500
            
            updateEspacio(
                data["no_cajon"], 
                data["estado"], 
                data["fecha_hora"], 
                data["direccion"],
                data["tipo"],
                data["discapacitado"],
                data["x"],
                data["y"],
            ) 
            codigo = 200
            mensaje = "Lugar actualizado"
        except KeyError:
            codigo = 400
            mensaje = "Datos incompletos o formato incorrecto"
        except Exception as e: print(e)
        finally:
            self.response = {"estatus":codigo, "mensaje":mensaje}
            return self.response, codigo
        
class EliminarTodoEspacios(Resource):
    response: dict
    def post(self):
        if "sessionID" not in session:
            return {"mensaje":"No autorizado"},401
        
        codigo: int = 500
        mensaje: str = "Error desconocido"
        try:
            eliminarTodoEspacios() 
            codigo = 200
            mensaje = "Espacios eliminados"
        except KeyError:
            codigo = 400
            mensaje = "Datos incompletos o formato incorrecto"
        except Exception as e: print(e)
        finally:
            self.response = {"estatus":codigo, "mensaje":mensaje}
            return self.response, codigo
        
class CambiarEstadoEspacio(Resource):
    response = {"estatus": 500, "mensaje": "Estado no cambiado"}
    def post(self):
        if "sessionID" not in session:
            return {"mensaje":"No autorizado"},401

        espacioPOST = request.get_json()
        id = espacioPOST["no_cajon"]
        estado=espacioPOST["estado"]
       
        if (id):
            espacio = selectEspacio(id)
            if(estado!=1 and estado!=0):
                self.response["mensaje"] = "Estado no válido"
            elif(not espacio):
                self.response["mensaje"] = "El número de cajón no existe"
            elif(espacio[0][1]==estado):
                return {"estatus": 200, "mensaje": "El espacio ya tiene asignado dicho estado"}, 200
            else:
                fecha_hora = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
                ocupar_desocupar(id, estado, fecha_hora)
                
                espacio = selectEspacio(id)
                print(espacio)
                lugar = Lugar(espacio[0][0],espacio[0][1],espacio[0][2],
                              espacio[0][3],espacio[0][4],espacio[0][5],
                              espacio[0][6],espacio[0][7],espacio[0][8],
                              espacio[0][9])
                response = lugar.diccionario() 
                response["estado"] = estado
                return response
                
        return self.response, 500
      
class CambiarDiscapacitadoEspacio(Resource):
    response = {"estatus": 400, "mensaje": "Estado no cambiado"}
    def post(self):
        if "sessionID" not in session:
            return {"message":"No autorizado"},401

        espacioPOST = request.get_json()
        id = espacioPOST["no_cajon"]
        if (id):
            espacio = selectEspacio(id)
            if(not espacio):
                self.response["mensaje"] = "El ID no existe"
            else:
                
                updateDiscapacitado(id)
                
                espacio = selectEspacio(id)
                lugar = Lugar(espacio[0][0],espacio[0][1],espacio[0][2],
                              espacio[0][3],espacio[0][4],espacio[0][5],
                              espacio[0][6],espacio[0][7])
                response = lugar.diccionario() 
                return response
                
        return self.response, 400

class SelectEspacios(Resource):
    response = {"estatus": 404, "mensaje": "Estacionamientos no disponibles"}

    def get(self):
        if "sessionID" not in session:
            return {"mensaje":"No autorizado"},401

        id=request.args.get("no_cajon")
        #Seleccionar un espacio si se manda el valor de id url?id = ID de estacionamiento
        if id:
            espacio=selectEspacio(id)
            if espacio:
                lugar = Lugar(espacio[0][0],espacio[0][1],espacio[0][2],
                              espacio[0][3],espacio[0][4],espacio[0][5],
                              espacio[0][6],espacio[0][7],espacio[0][8],
                              espacio[0][9])
                response = lugar.diccionario() 
                return response
            else:
                self.response["mensaje"]="Ese estacionamiento no existe"
                return self.response,400
        #Seleccionar todos los espacios 
        espacios=selectEspacios()  
        if espacios:
            dict_list = []
            for i in range(len(espacios)):
               lugar = Lugar(espacios[i][0],espacios[i][1],espacios[i][2],
                             espacios[i][3],espacios[i][4],espacios[i][5],
                             espacios[i][6],espacios[i][7],espacios[i][8],
                             espacios[i][9])
               dict = lugar.diccionario() 
               dict_list.append(dict)
            return dict_list
        else:
            return [], 200
            
class DeleteEspacio(Resource):
    
    response = {"estatus": 404, "mensaje": "Estacionamiento no existe"}
    def post(self):
        if "sessionID" not in session:
            return {"mensaje":"No autorizado"},401
        
        espacioPOST = request.get_json()
        id = espacioPOST["no_cajon"]
        if(id):
            espacio = selectEspacio(id)
            if(espacio): 
                deleteEspacio(id)
                self.response["mensaje"] = f'Espacio {id} eliminado'
                self.response["estatus"] = 200
            else:
                self.response["mensaje"] = "Estacionamiento no existe"
                self.response["estatus"] = 404
                return self.response,400
        return self.response,200
                             
#Administrador 

class Admin():
    def __init__(self,nombre,RFC,CURP):
        self.nombre = nombre
        self.RFC = RFC
        self.CURP = CURP

    @classmethod
    def from_dict(cls, datos: dict):
        return cls( datos["nombre"], datos["RFC"], datos["CURP"] )
    
    #Convertir lugar en diccionario de python y asignarle nombres a los campos
    def diccionario(self):
        return {"nombre": self.nombre, "RFC": self.RFC,
                "CURP": self.CURP}

class SelectAdmin(Resource):
    #response = {"status": 404, "msj": "Administradores no disponibles"}
    def get(self):
        if "sessionID" not in session:
            return {"mensaje":"No autorizado"},401
        
        # Checar si recibimos un parametro "RFC"
        if 'RFC' in request.args:
            rfc: str = datos.args.get('RFC')
            datos = consultarAdmin(rfc)
            if datos:
                # Extraer tupla de la lista
                datos = datos[0]
                administrador = Admin(RFC=datos[0], nombre=datos[1], CURP=datos[2])
                return administrador.diccionario()
            else:
                return {"status": 404, "mensaje": "No encontrado"}, 404
        else:
            # Obtener todos los administradores
            datos = selectAllAdmin()
            if datos:
                response = []
                for i in datos:
                    administrador = Admin(RFC=i[0], nombre=i[1], CURP=i[2])
                    response.append(administrador.diccionario())
                return response
            else:
                return {"status": 404,
                        "mensaje": "No hay administradores registrados"}, 404
        
class InsertAdmin(Resource):
    def post(self):
        if "sessionID" not in session:
            return {"mensaje":"No autorizado"},401
        
        # Salimos si se supero el limite de administradores
        if(selectCountAdmin() >= 5):
                return {"estatus": 500,
                        "mensaje": "Limite de administradores alcanzado"}, 500
        data = request.get_json()
        if data:
            # Verificar si el RFC existe
            ### TODO: Utilizar un metodo distinto para consultar IDs
            if( consultarAdmin(data["RFC"])):
                return {"estatus":500, "mensaje":"RFC ya existe"}, 500
            
            if( validarNombre(data["nombre"])):
                return {"estatus":500, "mensaje":"Este nombre de usuario ya existe"}, 500
            
            newAdmin = Admin(RFC=data["RFC"], nombre=data["nombre"], CURP=data["CURP"])
            insertAdmin( data["RFC"], data["nombre"], data["passwd"], data["CURP"])

            print(f"Administrador agregado: {data['RFC']}")
            return newAdmin.diccionario(), 201
        return {"estatus":200, "mensaje":"No se recibieron datos"},200
    
class DeleteAdmin(Resource):
    response = {"estatus": 404, "mensaje": "RFC no proporcionado"}
    def post(self):
        if "sessionID" not in session:
            return {"mensaje":"No autorizado"},401

        espacioPOST = request.get_json()
        rfc = espacioPOST["RFC"]
        if(rfc):
            # Comprobar si existe el administrador
            espacio = consultarAdmin(rfc)
            if(espacio): 
                deleteAdmin(rfc)
                self.response["mensaje"] = f'Administrador con RFC: {rfc} eliminado'
                self.response["estatus"] = 200
            else:
                self.response["mensaje"] = "Admin no existe"
                self.response["estatus"] = 404
                return self.response,400
        return self.response,200
    
class UpdateAdmin(Resource):
    response: dict
    def post(self):
        if "sessionID" not in session:
            return {"mensaje":"No autorizado"},401
        
        codigo: int = 500
        mensaje: str = "Error desconocido"
        adminPOST = request.get_json()
        try:
            selectedAdmin = consultarAdmin( adminPOST["RFC"] )
            if not selectedAdmin:
                codigo = 404
                mensaje = "RFC no encontrado"
            else:
                if validarNombre(adminPOST["nombre"], selectedAdmin[0][1]):
                    codigo = 500
                    mensaje = "Este nombre de usuario ya existe"
                    return {"estatus":500, "mensaje":"Este nombre de usuario ya existe"}, 500
                updateAdmin( adminPOST["RFC"], adminPOST["nombre"], 
                             adminPOST["CURP"], adminPOST["nuevo_RFC"] ) 
                codigo = 200
                mensaje = f"Administrador con RFC: {adminPOST['RFC']} modificado"
        except KeyError:
            codigo = 400
            mensaje = "Datos incompletos o formato incorrecto"
        except Exception as e: print(e)
        finally:
            self.response = {"estatus":codigo, "mensaje":mensaje}
            return self.response, codigo

class UpdateAdminPassword(Resource):
    response: dict
    def post(self):
        if "sessionID" not in session:
            return {"mensaje":"No autorizado"},401
        
        codigo = 500
        mensaje = "Error desconocido"
        adminPOST = request.get_json()
        try:
            selectedAdmin = consultarAdmin( adminPOST["RFC"] )
            if not selectedAdmin:
                codigo = 404
                mensaje = "RFC no encontrado"
            else:
                admin = LoginAdmin(adminPOST["nombre"], adminPOST["passwd"])

                if not admin:
                    codigo = 500
                    mensaje = "Credenciales incorrectas"
                    return {"mensaje":"Credenciales incorrectas"},500
                
                if adminPOST["nueva_passwd"] != adminPOST["passwd_repeat"]:
                    codigo = 500
                    mensaje = "Las contraseñas no coinciden"
                    return {"mensaje":"Las contraseñas no coinciden"}, 500
                updateAdminPassword(adminPOST["nueva_passwd"], adminPOST["RFC"]) 
                codigo = 200
                mensaje = f"Administrador con RFC: {adminPOST['RFC']} modificado"
        except KeyError:
            codigo = 400
            mensaje = "Datos incompletos o formato incorrecto"
        finally:
            self.response = {"estatus":codigo, "mensaje":mensaje}
            return self.response, codigo

class Login(Resource):
    def post(self):
        if 'sessionID' in session:
            return {"mensaje":"Ya hay una sesión activa"},403
        
        login_parser = reqparse.RequestParser()
        login_parser.add_argument('nombre', help='Requerido', required=True)
        login_parser.add_argument('passwd', help='Requerido', required=True)

        data = login_parser.parse_args()
        admin = LoginAdmin(data["nombre"], data["passwd"])

        if not admin:
            return {"mensaje":"Credenciales incorrectas"},401
        
        # Generamos un token por medio del modulo secrets 
        sessionID = token_urlsafe(32) 
        session['sessionID'] = sessionID
        session['RFC'] = admin[0]

        return {"sessionID":sessionID},200
    
class ValidateSession(Resource):
    def post(self):
        if 'sessionID' in session:
            return {"mensaje": "Sesión activa"}, 200
        return {"mensaje": "Sesión expirada"}, 401
    
class logout(Resource):
    def post(self):
        if "sessionID" not in session:
            return {"mensaje":"No autorizado"},401
        session.pop('sessionID', None)
        session.pop('RFC', None)
        return {"mensaje": "Se ha cerrado sesión del usuario"},200

class ApartarLugar(Resource):
    def get(self):
        espacio = obtenerEspacio()
        if espacio[0]:
            make_ticket(espacio[0],"Normal")
            if sensores_disponibles: # Revisar si el arduino esta conectado
                if espacio[0] in lugares_sensor:
                    setAsignar(espacio[0], 1)
                else:
                    fecha_hora = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
                    ocupar_desocupar(espacio[0],1,fecha_hora)
                if not FAKESENSORS:
                    arduino.write(str(100).encode())
                print("[G]: Entrada con arduino")
            else:
                fecha_hora = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
                ocupar_desocupar(espacio[0],1,fecha_hora)
                print("[G]: Entrada sin arduino")
            return {"mensaje": f"Lugar: {espacio[0]} asignado"}
        else:
            return {"mensaje":"No hay espacios disponibles"}
            
class ApartarLugarDiscapacitado(Resource):
    def get(self):
        espacio = obtenerEspacioDiscapacitado()
        print(espacio)
        if espacio[0]:
            make_ticket(espacio[0],"Discapacitado")
            if sensores_disponibles: # Revisar si el arduino esta conectado
                if espacio[0] in lugares_sensor:
                    setAsignar(espacio[0], 1)
                else:
                    fecha_hora = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
                    ocupar_desocupar(espacio[0],1,fecha_hora)
                if not FAKESENSORS:
                    arduino.write(str(100).encode())
                print("[G]: Entrada con arduino")
            else:
                fecha_hora = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
                ocupar_desocupar(espacio[0],1,fecha_hora)
                print("[G]: Entrada sin arduino")
            return {"mensaje": f"Lugar: {espacio[0]} asignado"}
        else:
            return {"mensaje":"No hay espacios disponibles"}

class DesocuparLugar(Resource):
    def get(self, lugar: str):
        espacio = consultarEspacioAsignado(lugar)
        if sensores_disponibles:
            if lugar in lugares_sensor:
                if espacio[0][1] == 0:
                    return {"mensaje":"Ticket invalido"},400
                elif espacio[0][0] == 1:
                    return {"mensaje":"EL espacio sigue estado ocupado"}
                else:
                    setAsignar(lugar, 0)
                    if not FAKESENSORS:
                        arduino.write(str(100).encode()) 
                    print("[G]: Salida con arduino")
            else:
                if espacio[0][0] == 0:
                    return {"mensaje":"Ticket invalido"},400
                else:
                    ocupar_desocupar(lugar,0,None)
                    if not FAKESENSORS:
                        arduino.write(str(100).encode()) 
                    print("[?]: Salida sin sensores")
        else:
            if espacio[0][0] == 0:
                    return {"mensaje":"Ticket invalido"},400
            else:
                ocupar_desocupar(lugar,0,None)
                print("[!]: Salida sin arduino")
        return {"mensaje":"Salida permitida"}
        

# CRUD Estacionamiento
api.add_resource(SelectEspacios, "/espacios")
api.add_resource(InsertEspacio, "/espacios/crear")
api.add_resource(UpdateEspacio, "/espacios/actualizar")
api.add_resource(CambiarEstadoEspacio,"/espacios/estado")
api.add_resource(CambiarDiscapacitadoEspacio,"/espacios/discapacitado")
api.add_resource(DeleteEspacio,"/espacios/eliminar")
api.add_resource(EliminarTodoEspacios, "/espacios/eliminar_todo")

# CRUD Administrador
api.add_resource(SelectAdmin, "/administradores")
api.add_resource(InsertAdmin, "/administradores/crear")
api.add_resource(DeleteAdmin,"/administradores/eliminar")
api.add_resource(UpdateAdmin, "/administradores/actualizar")
api.add_resource(UpdateAdminPassword, "/administradores/actualizar_password")

# Login & logout
api.add_resource(Login, "/login")
api.add_resource(logout, "/logout")
api.add_resource(ValidateSession, "/validar_sesion")

# ui
api.add_resource(ApartarLugar, "/ui/obtener_lugar")
api.add_resource(ApartarLugarDiscapacitado, "/ui/obtener_lugar_discapacitado")
api.add_resource(DesocuparLugar, "/ui/desocupar_lugar/<string:lugar>")

if __name__ == "__main__":
    """
    if isMysqlRunning():
        setupMysql_docker()
    else:
        print("[Error]: No se pudo conectar con la base de datos (¿Esta activa?)")
        raise
    """
    try:
        try: # Arduino
            if FAKESENSORS:
                sensores_disponibles = True
            else:
                arduino = initSensores()
                if arduino:
                    sensores_disponibles = True
        except Exception as e:
            print(e)
            sensores_disponibles = False

        if sensores_disponibles:
            #espacios = espaciosSensor()
            lugares_sensor = ['A1','A2','A3']
            if FAKESENSORS:
                sensores1 = threading.Thread(target=fakevalidarEspacioOcupado, args=(lugares_sensor,DATABASE))
            else:
                sensores1 = threading.Thread(target=validarEspacioOcupado, args=(arduino, lugares_sensor,DATABASE))
            sensores1.daemon = True     # Hacemos que el hilo pare junto al principal
            sensores1.start()
        app.run()
        
    except KeyboardInterrupt:
        if sensores_disponibles:
            sensores1.join()
            exit()
        
