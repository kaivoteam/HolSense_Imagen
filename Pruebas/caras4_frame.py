from PIL import Image, ImageFile, ImageChops,ImageOps,ImageDraw

import time
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation

def cantidad_frames(imagen):
    cantidad_frames = 0
    try:
        while 1:
            imagen.seek(cantidad_frames) #va al frame 
            cantidad_frames+=1
    except EOFError:
        pass
    return cantidad_frames-1
def angulo_a_frame(angulo,frames):
    return int( round( angulo * frames / 360.0) )

#caracteristicas de calibracion
#aspecto_normal =    #0.2 # o 1/5
def aspecto_normal(tamanno):
    delta = 10.0 #delta fijo
    return int( round(tamanno/3.0 - delta) )

def redondear_a_int(numero):
    return int(round(numero))

def trim(imag): #remueve bordes (o acerca) hasta un cierto delta
    delta = 20 #calibrar esto (es el espacio extra anndido alrededor del bbox)

    bg = Image.new(imag.mode,imag.size,imag.getpixel((0,0)))
    diff = ImageChops.difference(imag,bg)
    bbox = diff.getbbox()

    if bbox:  
        tamanno_extra = ( bg.size[0] - bbox[2] , bg.size[1]- bbox[3] )
        if np.min(tamanno_extra) < delta: #no remueve bordes
            print "HOLA MUNDITO"
            return imag #para no agregar fondo extra a la imagen (bordes feos)

        else: #hace crop a las imagenes necesarias
            nuevo_bbox = tuple([bbox[0] - delta,
                                bbox[1] - delta,
                                bbox[2] + delta,
                                bbox[3] + delta ])
            return imag.crop(nuevo_bbox)
    else:
        print "Ocurrio un suceso inesperado"
        return imag

##-----------------CREAR LA IMAGEN---------------
def cargar_caras(im,current,frames):
    #ver el tema de la resolucion de la imagen
    caras = []
    for angulo in angulos: #extraer 4 angulos a partir del current
        frame_angulo = (angulo_a_frame(angulo, frames )+current) % frames
        #print ("para angulo", angulo,"es necesario ir al frame ",frame_angulo)
        im.seek(frame_angulo-1)
        nueva_im = im.copy()

        nueva_im = trim(nueva_im) #achicar bordes (centra al centro xd)

        #imagenes cuadradas (rellena para dejar cuadrado)
        nuevo_size = np.max(nueva_im.size)
        imagen_a_guardar = Image.new('RGB', (nuevo_size,nuevo_size), (0,0,0))
        imagen_a_guardar.paste(nueva_im, ( (nuevo_size - nueva_im.size[0]) /2, (nuevo_size - nueva_im.size[1])/2 ))

        """if nueva_im.size[0] != nueva_im.size[1]: #esto no las deja perfectamente cuadradas
            
            longer_side = np.max(nueva_im.size)
            horizontal_padding = (longer_side - nueva_im.size[0]) / 2.0
            vertical_padding = (longer_side - nueva_im.size[1]) / 2.0
            nueva_im = nueva_im.crop(
                (
                    -horizontal_padding,
                    -vertical_padding,
                    redondear_a_int( nueva_im.size[0] + horizontal_padding),
                    redondear_a_int( nueva_im.size[1] + vertical_padding)
                )
            )
            """
        
        ##---calcula centro de masa para posicionar la imagen... muy costoso------
        """
        immat = imagen_a_guardar.load()

        pixel = imagen_a_guardar.getpixel((0,0))
        m = np.zeros(imagen_a_guardar.size)
        (X,Y) = imagen_a_guardar.size
        for x in range(X):
            for y in range(Y):
                m[x,y] = immat[(x,y)] != pixel
        m = m/np.sum(np.sum(m))

        #marginal distribution
        dx = np.sum(m,1)
        dy = np.sum(m,0)

        #expected values
        cx = np.sum(dx * np.arange(X))
        cy = np.sum(dy * np.arange(Y))

        print imagen_a_guardar.size
        print "centro de masa: ",(cx,cy)
        """

        #hace un circulo pero se demora harto... mejor fondo negro nomas
        #bigsize = (imagen_a_guardar.size[0]*3, imagen_a_guardar.size[1] *3)
        #mask = Image.new('L',bigsize,0)
        #draw = ImageDraw.Draw(mask)
        #draw.ellipse((0,0)+bigsize,fill=255)
        #mask=mask.resize(imagen_a_guardar.size,Image.ANTIALIAS)
        #imagen_a_guardar.putalpha(mask)

        caras.append(imagen_a_guardar) #se ve choro asi ImageChops.invert(imagen_a_guardar)
    return list(caras)

#4 imagenes en 4 angulos
angulos = [0.0, 90.0, 180.0, 270.0]


#####-------CODIGO PARA MOVER-----------------------
name_image = raw_input("Nombre de imagen GIF: ")

#Asumiendo que estan en la misma carpeta
im = Image.open("../imagenes/"+name_image+".gif")
print(im.format, im.size, im.mode)

frames = cantidad_frames(im)+1 #asumiendo que los frames da vuelta 360
print "La imagen tiene %d frames"%(frames)

tamanno_original = min(im.size) #para imagenes cuadradas

#Movimiento de la imagen a traves de actual
current = 0 #frame en el momento (actual)
zoom = 1.0  #zoom en el momento (actual)

de_cabeza = 0 #para que este de cabeza probar con: 180

#con memoria (Si no realiza mov)
caras_memoria = cargar_caras(im,current,frames) #para que zoom sea mas rapido
print caras_memoria[0].size
#mostrar la imagen primera antes de alguna accion

while(True):
    opcion = raw_input("1 Derecha \n2 Izquierda \n3 Zoom in \n4 Zoom out\n")

    start_time = time.time()

    #asignar cantidad de mov
    #asignar un zoom maximo y zoom minimo

    if opcion == '1': # movimiento derecha
        current +=1 %frames

    elif opcion == '2': #movimiento izquierda
        current -=1 %frames
        if current <0: #ya que solo va en numeros positivos
            current += frames

    elif opcion == '3': #hacer zoom
        zoom+=0.1 #calibrar

    elif opcion == '4': #quitar zoom
        zoom-=0.1
    else:
        print("Movimiento invalido")
        continue

    ##-----------------CREAR LA IMAGEN (CON MEMORIA---------------
    if opcion == '3' or opcion == '4' : #solo para zoom (utiliza la que tiene en memoria)
        caras = [cara.copy() for cara in caras_memoria] #ya que cada cara es una referencia
    else:
        caras = cargar_caras(im,current,frames)
        caras_memoria = [cara.copy() for cara in caras]

    #calibrar esto
    w,h = 854,480 #1280,720 #quizas es muy pesada la imagen con esa resolucion
    mascara = Image.new('RGB', (w,h))
    tamanno_mascara = min(w,h)

    #nuevo tamanno
    tamanno_actual = int( aspecto_normal(tamanno_mascara) * zoom )

    ##----------------------ROTAR Y REDIMENSIONAR-------------------------------
    ##esto se podria paralelizar.. se demora unos 0.03 seg
    if caras[0].size[0] > tamanno_actual : 
        caras[0].thumbnail((tamanno_actual,tamanno_actual),Image.ANTIALIAS) #cara frente
        cara_frente = caras[0].rotate(180+de_cabeza)#,expand=True)
        caras[1].thumbnail((tamanno_actual,tamanno_actual),Image.ANTIALIAS) #cara izquierda
        cara_izquierda = caras[1].rotate(90+de_cabeza)#,expand=True)
        caras[2].thumbnail((tamanno_actual,tamanno_actual),Image.ANTIALIAS) #cara derecha
        cara_derecha = caras[2].rotate(270+de_cabeza)#,expand=True)
        caras[3].thumbnail((tamanno_actual,tamanno_actual),Image.ANTIALIAS) #cara atras
        cara_atras = caras[3].rotate(0+de_cabeza)#,expand=True)
    else:  #si el zoom supera el tamanno actual de la imagen
        cara_aux = caras[0].resize((tamanno_actual,tamanno_actual),Image.ANTIALIAS) #cara frente
        cara_frente = cara_aux.rotate(180+de_cabeza)#,expand=True)
        cara_aux = caras[1].resize((tamanno_actual,tamanno_actual),Image.ANTIALIAS) #cara izquierda
        cara_izquierda = cara_aux.rotate(90+de_cabeza)#,expand=True)
        cara_aux = caras[2].resize((tamanno_actual,tamanno_actual),Image.ANTIALIAS) #cara derecha
        cara_derecha = cara_aux.rotate(270+de_cabeza)#,expand=True)
        cara_aux = caras[3].resize((tamanno_actual,tamanno_actual),Image.ANTIALIAS) #cara atras
        cara_atras = cara_aux.rotate(0+de_cabeza)#,expand=True)

    #data = np.asarray(cara_frente,dtype='int32')
    #cara_frente = Image.fromarray(np.uint8(data),'RGB')
    
    ##---------------------------AJUSTAR-------------------------------
    if zoom > 1: #si se sale de los limites del ratio base
        #definir un zoom maximo ya que se ve mal si se hace mucho zoom
        # se pierde la imagen la calidad de la imagen

        #data = np.asarray(cara_frente)
        #coords = np.argwhere(data< 240)  #np.where(data < 240, data,0)
        #print coords
        #x1,y1,z1 = coords.min(axis=0)
        #x2,y2,z2 = coords.max(axis=0)+1

        #convierte los menores a valor en 0 (negro)
        #nueva_data = data[x1:x2, y1:y2,z1:z2] #cropped
        #print nueva_data
        #print nueva_data.shape
        #cara_frente = Image.fromarray(np.uint8(nueva_data),'RGB')

        #tamanno seria de tamanno_actual*aspecto_normal para manternerlo
        tamanno = aspecto_normal(tamanno_mascara)

        #zoom al centro de la imagen
        #modificar para que sea al centro del objeto (Costoso)
        x1 = x2= redondear_a_int( (tamanno_actual - tamanno)/2.0 )
        y1 = y2 = redondear_a_int( (tamanno_actual + tamanno)/2.0 )

        cara_frente = cara_frente.crop((x1, x2, y1, y2))
        cara_izquierda = cara_izquierda.crop((x1, x2, y1, y2))
        cara_derecha = cara_derecha.crop((x1, x2, y1, y2))
        cara_atras = cara_atras.crop((x1, x2, y1, y2))

    ##-------------------------POSICIONAR IMAGEN EN 4 LUGARES-------------------
    delta_imagenes = redondear_a_int( tamanno_mascara/3 - aspecto_normal(tamanno_mascara) )

    #Se presentan dos dimensiones por si se hace zoom y la dimension actual es menor a la normal
    dimension_normal = aspecto_normal(tamanno_mascara) + delta_imagenes # (quitarle el delta)dimension fija para situar las caras
    dimension_actual = min(cara_frente.size)           #dimension actual, despues de hacer zoom
    #con zoom = 1 ==> dimension_normal = dimension_actual

    #calibrar todo esto (basado en Holho y dejar un tamanno de imagen al medio)
    delta_dimensiones = (dimension_normal - dimension_actual)
    delta_dimensiones2 = w- dimension_actual
    delta_dimensiones3 =  h- dimension_actual

    pos_y_atras = redondear_a_int( delta_dimensiones/2.0) + delta_imagenes#primer tercio de la imagen superior
    pos_y_frente = redondear_a_int(  delta_dimensiones/2.0 + 2.0*dimension_normal) - delta_imagenes# desde la dos tercios de la imagen inferior

    pos_x_der = redondear_a_int( delta_dimensiones2/2.0 + dimension_normal ) - delta_imagenes
    pos_x_izq = redondear_a_int( delta_dimensiones2/2.0 - dimension_normal ) + delta_imagenes

    mitad_w = redondear_a_int(  delta_dimensiones2 /2.0 )
    mitad_h = redondear_a_int(  delta_dimensiones3/2.0 )

    #esto demora 0.05 aprox pero no se puede paralelizar ya que es I/O
    mascara.paste(cara_frente, ( mitad_w, pos_y_frente))
    mascara.paste(cara_izquierda, ( pos_x_izq , mitad_h ))
    mascara.paste(cara_derecha, (pos_x_der , mitad_h ))         
    mascara.paste(cara_atras, ( mitad_w, pos_y_atras))   

    #agregar texto (**EXTRA**)
    #draw = ImageDraw.Draw(mascara)
    #draw.text(( mitad_w+dimension_actual/2, pos_y_atras),name_image,fill='white')

    #mostrar y guardar
    mascara.show()
    mascara.save('imagen.png')
    #guardar?
    
    print "Demoro %f segundos en total"%(time.time() - start_time)
