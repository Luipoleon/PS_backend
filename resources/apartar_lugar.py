from parking import *
from flask_restful import Resource
from make_ticket import make_ticket
from datetime import datetime

class ApartarLugar(Resource):
    def get(self):
        espacio = obtenerEspacio()
        if espacio[0]:
            fecha_hora = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
            make_ticket(espacio[0],"Normal")
            ocupar_desocupar(espacio[0], 1, fecha_hora)
            return {"mensaje": f"Lugar: {espacio[0]} asignado"}
        else:
            return {"mensaje":"No hay espacios disponibles"}
            
class ApartarLugarDiscapacitado(Resource):
    def get(self):
        espacio = obtenerEspacioDiscapacitado()
        print(espacio)
        if espacio[0]:
            fecha_hora = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
            make_ticket(espacio[0],"Discapacitado")
            ocupar_desocupar(espacio[0], 1, fecha_hora)
            return {"mensaje": f"Lugar: {espacio[0]} asignado"}
        else:
            return {"mensaje":"No hay espacios disponibles"}

