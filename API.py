
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
    def __init__(self,numCajon,seccion,estado,fecha_hora):
        self.numCajon = numCajon
        self.seccion = seccion
        self.estado = estado
        self.fecha_hora = fecha_hora
    #Convertir lugar en diccionario de python y asignarle nombres a los campos
    def diccionario(self):
        return {"numCajon": self.numCajon, "seccion":self.seccion,"estado": self.estado,
                            "fecha_hora": self.fecha_hora}
       
#CRUD lugares

class InsertEspacio(Resource):
    response = {"estatus": 400, "mensaje": "Espacio no creado"}

    def post(self):
        espacioPOST = request.get_json()
        id = espacioPOST["ID"]
        if(id and len(id)>=2):
            espacio = selectEspacio(id)
            if(not espacio):
                insertEspacio(id)
                self.response["estatus"] = 201
                self.response["mensaje"] = "Espacio creado exitosamente"
                espacioNuevo = selectEspacio(id)
                lugar = Lugar(espacioNuevo[0][0],espacioNuevo[0][1],espacioNuevo[0][2],
                              espacioNuevo[0][3])
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
                              espacio[0][3])
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
                lugar = Lugar(espacio[0][0],espacio[0][1],espacio[0][2],espacio[0][3])
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
               lugar = Lugar(espacios[i][0],espacios[i][1],espacios[i][2],espacios[i][3])
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
                print(datos)
                # Extraer tupla de la lista
                datos = datos[0]
                administrador = Admin(RFC=datos[0], nombre=datos[1], CURP=datos[2])
                return administrador.diccionario()
            else:
                return {"status": 400, "mensaje": "No encontrado"}, 400
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
    #response = {"status": 400, "mensaje": "Adminstrador no creado"}
    def post(self):
        # Salimos si se supero el limite de administradores
        if(selectCountAdmin() >= 5):
                return {"status": 201,
                        "mensaje": "Limite de administradores alcanzado"},201
        data = request.get_json()
        if data:
            # Verificar si el RFC existe
            ### TODO: Utilizar un metodo distinto para consultar IDs
            if( consultarAdmin(data["RFC"]) ):
                return {"status":201, "mensaje":"RFC ya existe"},201
            # Creamos modelo
            newAdmin = Admin(RFC=data["RFC"], nombre=data["nombre"], CURP=data["CURP"])

            insertAdmin( data["RFC"], data["nombre"], data["passwd"], data["CURP"])

            print(f"Administrador agregado: {data['RFC']}")
            return newAdmin.diccionario(), 201
        return {"status":400, "mensaje":"No se recibieron datos"},400
class DeleteAdmin(Resource):
    response = {"estatus": 404, "mensaje": "RFC no proporcionado"}
    def post(self):
        
        espacioPOST = request.get_json()
        rfc = espacioPOST["RFC"]
        if(rfc):
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
    


api.add_resource(SelectEspacios, "/espacios")
api.add_resource(InsertEspacio, "/espacios/crear")
api.add_resource(CambiarEstadoEspacio,"/espacios/estado")
api.add_resource(DeleteEspacio,"/espacios/eliminar")
api.add_resource(SelectAdmin, "/administradores")
api.add_resource(InsertAdmin, "/administradores/add")
api.add_resource(DeleteAdmin,"/administradores/eliminar")





if __name__ == "__main__":
    app.run()
