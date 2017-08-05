from PIL import Image, ImageFile, ImageChops,ImageOps,ImageDraw,ImageFont

import time
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation

def redondear_a_int(numero):
    """ Descripcion:
            Funcion que redondea el numero al entero mas cercano
    """
    return int(round(numero))

def cantidad_frames(imagen):
    """ Descripcion:
            Funcion que calcula la cantidad de frames en una imagen
    """
    cantidad_frames = 0
    try:
        while 1:
            imagen.seek(cantidad_frames) #va al frame 
            cantidad_frames+=1
    except EOFError:
        pass
    return cantidad_frames-1

def angulo_a_frame(angulo,frames):
    """ Descripcion:
            Funcion que calcula el frame correspondiente a un angulo

        Args:
            *angulo: angulo a buscar el frame
            *frames: cantidad de frames de la imagen
    """
    return redondear_a_int( float(angulo) * frames / 360.0)

#caracteristicas de calibracion
def aspecto_normal(tamanno):
    """ Descripcion:
            Funcion que calcula el aspecto normal de la imagen (basado en dimensiones fijas)

        Args:
            *tamanno: tamanno real de la imagen
        *delta: la cantidad de espacio extra fuera de la imagen, para que no quede pegada a los bordes
    """
    delta = redondear_a_int(tamanno/40.0) #delta fijo
    #delta = redondear_a_int(0.3*40.0) #delta fijo
    return redondear_a_int(tamanno/3.0 - delta) 

def trim(imag): 
    """ Descripcion:
            Funcion que remueve bordes (o acerca) de una imagen hasta un cierto delta

        *delta: Es el espacio extra anndido alrededor del bbox
    """
    delta = 50 #calibrar esto

    bg = Image.new(imag.mode,imag.size,imag.getpixel((0,0)))
    diff = ImageChops.difference(imag,bg)
    bbox = diff.getbbox()

    if bbox:  
        tamanno_extra = ( bg.size[0] - bbox[2] , bg.size[1]- bbox[3] )
        if np.min(tamanno_extra) < delta: #no remueve bordes
            print "HOLA MUNDO"
            return tuple([0,0, bg.size[0], bg.size[1]] ) #imag #para no agregar fondo extra a la imagen (bordes feos)

        else: #hace crop a las imagenes necesarias
            nuevo_bbox = tuple([bbox[0] - delta,
                                bbox[1] - delta,
                                bbox[2] + delta,
                                bbox[3] + delta ])
            return nuevo_bbox#imag.crop(nuevo_bbox)
    else:
        print "Ocurrio un suceso inesperado"
        return False#imag

##-----------------CREAR LA IMAGEN---------------
#4 imagenes en 4 angulos
angulos = [0.0, 90.0, 180.0, 270.0]
def cargar_caras(im,current,frames):
    """ Descripcion:
            Funcion que carga las 4 caras de la imagen y las devuelve en una lista

        Args:
            *im: imagen
            *current: actual frame
            *frames: cantidad de frames de la imagen
    """
    global angulos

    caras = []
    for angulo in angulos: #extraer 4 angulos a partir del current
        frame_angulo = (angulo_a_frame(angulo, frames )+current) % frames
        #print ("para angulo", angulo,"es necesario ir al frame ",frame_angulo)
        im.seek(frame_angulo-1)
        nueva_im = im.copy()
        
        caras.append(nueva_im) #se ve choro asi ImageChops.invert(imagen_a_guardar)
    return list(caras)

def centrar_4caras(caras):
    for i in range(len(caras)):
        cara = caras[i]
        nueva_cara = cara.crop(trim(cara))#achicar bordes (centra al centro xd)

        caras[i].close()
        del cara
        caras[i] = nueva_cara
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


        #otra forma de hacerlo
        (X,Y) = imagen_a_guardar.size


        m = np.sum(np.asarray(imagen_a_guardar), -1) < 255*3
        m = m/ np.sum(np.sum(m))

        dx = np.sum(m,0)
        dy = np.sum(m,1)

        #expected values
        cx = np.sum(dx * np.arange(X))
        cy = np.sum(dy * np.arange(Y))

        print imagen_a_guardar.size
        print "centro de masa: ",(cx,cy)

        """

#####-------CODIGO PARA MOVER-----------------------
name_image = raw_input("Nombre de imagen GIF: ")

#Asumiendo que estan en la misma carpeta
im = Image.open("../imagenes/"+name_image+".gif")
print(im.format, im.size, im.mode)

frames = cantidad_frames(im)+1 #asumiendo que los frames da vuelta 360
print "La imagen tiene %d frames"%(frames)

tamanno_original = min(im.size) 

#Movimiento de la imagen a traves de actual
current = 0 #frame en el momento (actual)
zoom = 1.0  #zoom en el momento (actual)

de_cabeza = 0 #para que este de cabeza probar con: 180

#hacer trim al primer frame y mantener ese aspectoo.. (para no tener que cambiar si el objeto cambia al darlo vuelta)
#im.seek(0)
#dimensiones_trim = trim( im.copy()) #achicar bordes (centra al centro xd)

#con memoria (Si no realiza mov)
caras_memoria = cargar_caras(im,current,frames) #para que zoom sea mas rapido

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
        #---ACTUALIZA CARAS_MEMORIA POR REFERENCIa----
        #borrar referencia vieja
        for cara in caras_memoria:
            cara.close()
        del caras_memoria[:] #vacia la lista
        caras_memoria += [cara.copy() for cara in caras] #actualizar

    #calibrar esto
    w,h = 854,480 #1280,720 #(se demora como 0.2 y necesita imagenes con mayor resolucion 640x640) costoso? 
    mascara = Image.new('RGB', (w,h))
    tamanno_mascara = min(w,h)

    #nuevo tamanno
    tamanno_actual = int( aspecto_normal(tamanno_mascara) * zoom )

    ##------------------PREPROCESAR CARAS (CENTRAR, RELLENAR, REDIMENSIONAR( + ajuste ZOOM) y ROTAR)----------------------------
    #CENTRAR
    centrar_4caras(caras) #con respecto al objeto (bbox)

    for i in range(len(caras)): ##---esto se podria paralelizar....
        nueva_im = caras[i].copy()

        #IMAGENES CUADRADAS(rellena para dejar cuadrado)
        if nueva_im.size[0] != nueva_im.size[1]:
            nuevo_size = np.max(nueva_im.size)
            imagen_a_guardar = Image.new('RGB', (nuevo_size,nuevo_size), (0,0,0))
            imagen_a_guardar.paste(nueva_im, ( (nuevo_size - nueva_im.size[0]) /2, (nuevo_size - nueva_im.size[1])/2 ))

        #REDIMENSIONAR
        if imagen_a_guardar.size[0] > tamanno_actual : 
            imagen_a_guardar.thumbnail((tamanno_actual,tamanno_actual),Image.ANTIALIAS) #cara frente
        else:  #si el zoom supera el tamanno actual de la imagen
            imagen_a_guardar = imagen_a_guardar.resize((tamanno_actual,tamanno_actual),Image.ANTIALIAS) #cara frente

        ##---------------------------AJUSTAR-------------------------------
        if zoom > 1: #si se sale de los limites del ratio base
            #definir un zoom maximo ya que se ve mal si se hace mucho zoom
            # se pierde la imagen la calidad de la imagen

            #tamanno seria de tamanno_actual*aspecto_normal para manternerlo
            tamanno = aspecto_normal(tamanno_mascara)

            #zoom al centro de la imagen
            x1 = x2= redondear_a_int( (tamanno_actual - tamanno)/2.0 )
            y1 = y2 = redondear_a_int( (tamanno_actual + tamanno)/2.0 )

            imagen_a_guardar = imagen_a_guardar.crop((x1, x2, y1, y2))
            #cara_izquierda = cara_izquierda.crop((x1, x2, y1, y2))
            #cara_derecha = cara_derecha.crop((x1, x2, y1, y2))
            #cara_atras = cara_atras.crop((x1, x2, y1, y2))

        #hace un circulo pero se demora harto... mejor fondo negro nomas
        #bigsize = (imagen_a_guardar.size[0]*3, imagen_a_guardar.size[1] *3)
        #mask = Image.new('L',bigsize,0)
        #draw = ImageDraw.Draw(mask)
        #draw.ellipse((0,0)+bigsize,fill=255)
        #mask=mask.resize(imagen_a_guardar.size,Image.ANTIALIAS)
        #imagen_a_guardar.putalpha(mask)

        caras[i].close()
        del nueva_im
        caras[i] = imagen_a_guardar

    #agregar texto (**EXTRA**)
    for cara in caras:
        fnt = ImageFont.truetype('/Pillow/Tests/fonts/FreeMono.ttf',20)
        draw = ImageDraw.Draw(cara)
        pos = ( cara.size[0]/2 - cara.size[0]/7, -5)
        draw.text(pos, name_image,font=fnt, fill='white')
        draw.line( (cara.size[0]/2, -5) + (cara.size[0]/2,cara.size[1]/2) ,fill='white')
        del draw

    #ROTAR .---esto se podria paralelizar.. se demora unos 0.03 seg
    cara_frente = caras[0].rotate(180+de_cabeza)#,expand=True)
    cara_izquierda = caras[1].rotate(90+de_cabeza)#,expand=True)
    cara_derecha = caras[2].rotate(270+de_cabeza)#,expand=True)
    cara_atras = caras[3].rotate(0+de_cabeza)#,expand=True)

    #data = np.asarray(cara_frente,dtype='int32')
    #cara_frente = Image.fromarray(np.uint8(data),'RGB')

    ##-------------------------POSICIONAR IMAGEN EN 4 LUGARES-------------------
    delta_imagenes = redondear_a_int( tamanno_mascara/3 - aspecto_normal(tamanno_mascara) )

    #Se presentan dos dimensiones por si se hace zoom y la dimension actual es menor a la normal (de las caras)
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

    #mostrar y guardar
    mascara.show()
    mascara.save('imagen.png')
    #guardar?

    #data = np.asarray(mascara)
    #figura.set_array(data)
    
    print "Demoro %f segundos en total"%(time.time() - start_time)
