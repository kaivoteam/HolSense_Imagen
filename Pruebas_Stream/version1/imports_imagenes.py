import time
from PIL import Image, ImageFile, ImageChops,ImageOps
import numpy as np

#####-------CODIGO PARA MOVER-----------------------
#annade: memoria
def hacer(im,frames,figura, current=0,zoom=1.0,memoria=False,caras_memoria=[]):
    de_cabeza = 0 #para que este de cabeza probar con: 180

    tamanno_original = min(im.size) 

    ##-----------------CREAR LA IMAGEN---------------
    #ver el tema de la resolucion de la imagen

        ##-----------------CREAR LA IMAGEN (CON MEMORIA UPDATED)---------------
    if memoria: #solo para zoom (utiliza la que tiene en memoria)
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

    #para imagenes no cuadradas podria cambiarse por resize
    caras[0].thumbnail((tamanno_actual,tamanno_actual),Image.ANTIALIAS) #cara frente
    cara_frente = caras[0].rotate(180)#,expand=True)
    caras[1].thumbnail((tamanno_actual,tamanno_actual),Image.ANTIALIAS) #cara izquierda
    cara_izquierda = caras[1].rotate(90)#,expand=True)
    caras[2].thumbnail((tamanno_actual,tamanno_actual),Image.ANTIALIAS) #cara derecha
    cara_derecha = caras[2].rotate(270)#,expand=True)
    caras[3].thumbnail((tamanno_actual,tamanno_actual),Image.ANTIALIAS) #cara atras
    cara_atras = caras[3].rotate(0)#,expand=True)

    ##---------------------AJUSTAR--------------------------
    if zoom > 1: #si se sale de los limites del ratio base
        #definir un zoom maximo ya que se ve mal si se hace mucho zoom
        # se pierde la imagen

        #tamanno seria de tamanno_actual*aspecto_normal para manternerlo
        tamanno = aspecto_normal(tamanno_mascara)

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

    #mostrar y guardar
    #mascara.show()
    #mascara.save('imagen.png')
    #guardar?
    data = np.asarray(mascara)
    figura.set_array(data)

    return caras_memoria

##-----------------CREAR LA IMAGEN---------------
#4 imagenes en 4 angulos
angulos = [0.0, 90.0, 180.0, 270.0]

def cargar_caras(im,current,frames):
    global angulos
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

        caras.append(imagen_a_guardar) #se ve choro asi ImageChops.invert(imagen_a_guardar)
    return list(caras)
    
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
    delta = 10.0
    return int( round(tamanno /3.0 - delta) )

# FUNCION QUE
def redondear_a_int(numero):
    return int(round(numero))