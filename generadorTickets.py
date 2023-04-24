import datetime as dt  #FECHA, HORA SISTEMA
from fpdf import FPDF  #GENERADOR DE PDF

#Se genera el PDF del ticket con la imagen del QR creado del espacio
espacio_asignado = 'A3'
secc = 'Normal'

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

