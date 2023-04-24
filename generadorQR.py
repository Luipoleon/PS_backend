import qrcode    #GENERADOR QR
from PIL import Image   #GENERADOR DE IMAGEN desde pillow

espacio_asignado = 'A3'

imagen = qrcode.make(espacio_asignado)     #SE GENERA EL CODIGO QR CON EL ESPACIO DADO
            
archivo = open('Espacio.png','wb')  #CREA EL ARCHIVO CON EL NOMBRE DE LA IMAGEN
imagen.save(archivo)    #GUARDA EL QR EN EL ARCHIVO DE LA IMAGEN
archivo.close()         

ruta_img = './'+'Espacio.png'   #SE GENERA LA RUTA
Image.open(ruta_img).show()  #SE MUESTRA LA IMAGEN CON EL QR 

