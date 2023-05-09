
from parking import *
from flask_restful import Api, Resource,request
from flask import Flask
from flask_cors import CORS


FLASK_DEBUG=1


app = Flask(__name__)
api = Api(app)
CORS(app)


#Lugares de estacionamiento

class Lugar():
    def __init__(self,numCajon,seccion,estado,fecha_hora,direccion,tipo,discapacitado,x_pos,y_pos):
        self.numCajon = numCajon
        self.seccion = seccion
        self.estado = estado
        self.fecha_hora = fecha_hora
        self.direccion = direccion
        self.tipo = tipo
        self.discapacitado = discapacitado
        self.x = x_pos
        self.y = y_pos
    #Convertir lugar en diccionario de python y asignarle nombres a los campos
    def diccionario(self):
        return {"no_cajon": self.numCajon, "seccion":self.seccion,"estado": self.estado,
                "fecha_hora": self.fecha_hora, "direccion":self.direccion, "tipo":self.tipo,
                "discapacitado":self.discapacitado, "x":self.x, "y": self.y }
       
#CRUD lugares

class InsertEspacio(Resource):
    response = {"estatus": 400, "mensaje": "Espacio no creado"}

    def post(self):
        espacioPOST = request.get_json()
        id = espacioPOST["ID"]
        if(id and len(id)>=2):
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
                              espacioNuevo[0][6],espacioNuevo[0][7],espacioNuevo[0][8])
                response = lugar.diccionario() 
                return response, 201
            else:
                self.response["estatus"] = 201
                self.response["mensaje"] = "El ID no esta disponible"
                
        else:
            self.response["estatus"] = 400
            self.response["mensaje"] = "ID no válido"
        return self.response, 400
        
    
class CambiarEstadoEspacio(Resource):
    response = {"estatus": 400, "mensaje": "Estado no cambiado"}
    def post(self):
        espacioPOST = request.get_json()
        id = espacioPOST["ID"]
        estado=espacioPOST["estado"]
       
        if (id and estado):
            espacio = selectEspacio(id)
            if(estado!="1" and estado!="0"):
                self.response["mensaje"] = "Estado no válido"
            elif(not espacio):
                self.response["mensaje"] = "El ID no existe"
            else:
                ocupar_desocupar(id,estado)
                
                lugar = Lugar(espacio[0][0],espacio[0][1],espacio[0][2],
                              espacio[0][3],espacio[0][4],espacio[0][5],
                              espacio[0][6],espacio[0][7],espacio[0][8])
                response = lugar.diccionario() 
                response["estado"] = estado
                return response
                
        return self.response, 400
      
class SelectEspacios(Resource):
    response = {"estatus": 404, "mensaje": "Estacionamientos no disponibles"}

    def get(self):
        id=request.args.get("id")
        #Seleccionar un espacio si se manda el valor de id url?id = ID de estacionamiento
        if id:
            espacio=selectEspacio(id)
            if espacio:
                lugar = Lugar(espacio[0][0],espacio[0][1],espacio[0][2],
                              espacio[0][3],espacio[0][4],espacio[0][5],
                              espacio[0][6],espacio[0][7],espacio[0][8])
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
                             espacios[i][6],espacios[i][7],espacios[i][8])
               dict = lugar.diccionario() 
               dict_list.append(dict)
            return dict_list
        else:
            return self.response, 400
        
        
class DeleteEspacio(Resource):
    
    response = {"estatus": 404, "mensaje": "Estacionamiento no existe"}
    def post(self):
        
        espacioPOST = request.get_json()
        id = espacioPOST["ID"]
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

class SelectAdmin(Resource):
    #response = {"status": 404, "msj": "Administradores no disponibles"}
    def get(self):
        # Checar si recibimos un parametro "RFC"
        if 'RFC' in request.args:
            rfc: str = request.args.get('RFC')
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
        # Salimos si se supero el limite de administradores
        if(selectCountAdmin() >= 5):
                return {"estatus": 400,
                        "mensaje": "Limite de administradores alcanzado"}, 401
        data = request.get_json()
        if data:
            # Verificar si el RFC existe
            ### TODO: Utilizar un metodo distinto para consultar IDs
            if( consultarAdmin(data["RFC"]) ):
                return {"estatus":400, "mensaje":"RFC ya existe"},400
            
            newAdmin = Admin(RFC=data["RFC"], nombre=data["nombre"], CURP=data["CURP"])
            insertAdmin( data["RFC"], data["nombre"], data["passwd"], data["CURP"])

            print(f"Administrador agregado: {data['RFC']}")
            return newAdmin.diccionario(), 201
        return {"estatus":200, "mensaje":"No se recibieron datos"},200
    

class DeleteAdmin(Resource):
    response = {"estatus": 404, "mensaje": "RFC no proporcionado"}
    def post(self):
        
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
        codigo: int
        mensaje: str
        adminPOST = request.get_json()
        try:
            selectedAdmin = consultarAdmin( adminPOST["RFC"] )
            if not selectedAdmin:
                codigo = 404
                mensaje = "RFC no encontrado"
            else:
                updateAdmin( adminPOST["RFC"], adminPOST["nombre"], 
                             adminPOST["passwd"], adminPOST["CURP"] ) 
                codigo = 200
                mensaje = f"Administrador con RFC: {adminPOST['RFC']} modificado"
        except KeyError:
            codigo = 400
            mensaje = "Datos incompletos o formato incorrecto"
        finally:
            self.response = {"estatus":codigo, "mensaje":mensaje}
            return self.response, codigo

# CRUD Estacionamiento
api.add_resource(SelectEspacios, "/espacios")
api.add_resource(InsertEspacio, "/espacios/crear")
api.add_resource(CambiarEstadoEspacio,"/espacios/estado")
api.add_resource(DeleteEspacio,"/espacios/eliminar")

# CRUD Administrador
api.add_resource(SelectAdmin, "/administradores")
api.add_resource(InsertAdmin, "/administradores/crear")
api.add_resource(DeleteAdmin,"/administradores/eliminar")
api.add_resource(UpdateAdmin, "/administradores/actualizar")




if __name__ == "__main__":
    app.run()
