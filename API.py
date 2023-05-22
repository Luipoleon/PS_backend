from parking import *
from flask_restful import Api, Resource, request, reqparse
from flask import Flask, session
from flask_cors import CORS
from secrets import token_urlsafe
from datetime import datetime
from sensores import initSensores, validarEspacioOcupado
from multiprocessing import Process, Value
from resources.apartar_lugar import ApartarLugar, ApartarLugarDiscapacitado

FLASK_DEBUG=1

sensores_canales: list = []
lugares: list = []

sensores_disponibles: bool

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True # Requerido para no recibir codigo 500 por usar flask_restful
api = Api(app)
app.config['SECRET_KEY'] = '\xd9M\xe6\x05\xa1-\xe6\x18\x86q\x89\x86t\x16\x91>\x8c\xef\x97(\x1e\xd0an'
app.config["SESSION_PERMANENT"] = False
CORS(app)


#Lugares de estacionamiento

class Lugar():
    def __init__(self,numCajon,estado,fecha_hora,direccion,tipo,discapacitado,x_pos,y_pos):
        self.numCajon = numCajon
        self.estado = estado
        self.fecha_hora = fecha_hora
        self.direccion = direccion
        self.tipo = tipo
        self.discapacitado = discapacitado
        self.x = x_pos
        self.y = y_pos
    #Convertir lugar en diccionario de python y asignarle nombres a los campos
    def diccionario(self):
        return {"no_cajon": self.numCajon, "estado": self.estado,
                "fecha_hora": self.fecha_hora, "direccion":self.direccion, "tipo":self.tipo,
                "discapacitado":self.discapacitado, "x":self.x, "y": self.y }
       
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
                              espacioNuevo[0][6],espacioNuevo[0][7])
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
                lugar = Lugar(espacio[0][0],espacio[0][1],espacio[0][2],
                              espacio[0][3],espacio[0][4],espacio[0][5],
                              espacio[0][6],espacio[0][7])
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
                              espacio[0][6],espacio[0][7])
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
                             espacios[i][6],espacios[i][7])
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
                
                
#Aministrador 

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

# TODO: Rewrite this to support reqparser
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


class Test(Resource):
    def get(self):
        if "sessionID" in session:
            return {"mensaje":"Estas autorizado!"},200
        return {"mensaje":"No autorizado"},401

class TestSensores(Resource):
    def get(self):
        if sensores_disponibles:
            return {"Sensor1":sensores_canales[0].value,
                    "Sensor2":sensores_canales[1].value,
                    "Sensor3":sensores_canales[2].value,}
        else:
            return {"mensaje":"No disponible"},503


class DesocuparLugar(Resource):
    def get(self, lugar: str):
        mensaje: str = ""
        codigo: int = 200
        espacio = consultarEspacio(lugar)
        if espacio[0][0] == 0:
            #return {"mensaje":f"Ticket invalido"},400
            mensaje = "Ticket invalido"
            codigo = 400
        
        elif sensores_disponibles and (lugar in lugares): # Revisar si es un lugar con sensor
            sensor = lugares.index(lugar)
            if sensores_canales[sensor] == 1:
                #return {"mensaje":f"El lugar {lugar} sigue estado ocupado."}
                mensaje = f"El espacio {lugar} sigue estado ocupado."
            else:
                ocupar_desocupar(lugar,0,None)
                #return {"mensaje":f"Espacio: {lugar} desocupado."}
                mensaje = f"El espacio {lugar} ha sido desocupado."
        else:
            ocupar_desocupar(lugar,0,None)
            #return {"mensaje":f"Espacio: {lugar} desocupado."}
            mensaje = f"El espacio {lugar} ha sido desocupado."

        return {"codigo":codigo,"mensaje":mensaje}, codigo

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
api.add_resource(Test, "/Test")

# ui
#api.add_resource(lectorQR, "/ui/qr") # No sirve jajajaj
api.add_resource(ApartarLugar, "/ui/obtener_lugar")
api.add_resource(ApartarLugarDiscapacitado, "/ui/obtener_lugar_discapacitado")
api.add_resource(DesocuparLugar, "/ui/desocupar_lugar/<string:lugar>")

# sensores
api.add_resource(TestSensores, "/Test/sensores")

if __name__ == "__main__":
    try:
        try: # Arduino
            arduino = initSensores()
            if arduino:
                sensores_disponibles = True
        except Exception as e:
            print(f"[WARNING]:  No se pudo establecer conexíon con el arduino")
            print(e)
            sensores_disponibles = False

        if sensores_disponibles:
            espacios = espaciosSensor()
            for _ in espacios:
                sensores_canales.append(Value('i', 0))
            lugares = espacios
            sensores = Process(target=validarEspacioOcupado, args=(arduino, espacios, sensores_canales,))
            sensores.start()
        app.run()
    except KeyboardInterrupt:
        if sensores_canales:
            sensores.terminate()
            arduino.close()
            exit()
    
        
    #app.run()
