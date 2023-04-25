
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
               lugar = Lugar(espacios[i][0],espacios[i][1],espacios[i][2],espacios[0][3])
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
        return {"nombre": self.id, "RFC": self.estado,
                "CURP": self.CURP,
                "RFC": self.RFC}


        
    
api.add_resource(SelectEspacios, "/espacios")
api.add_resource(InsertEspacio, "/espacios/crear")
api.add_resource(CambiarEstadoEspacio,"/espacios/estado")
api.add_resource(DeleteEspacio,"/espacios/eliminar")







if __name__ == "__main__":
    app.run()
