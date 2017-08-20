from PIL import Image, ImageFile, ImageChops,ImageOps,ImageDraw,ImageFont,  ImageSequence

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

def aspecto_normal(tamanno):
    """ Descripcion:
            Funcion que calcula el aspecto normal de la imagen (basado en dimensiones fijas)

        Args:
            *tamanno: tamanno real de la imagen
        *delta: la cantidad de espacio extra fuera de la imagen, para que no quede pegada a los bordes
    """
    delta = redondear_a_int(tamanno/40.0) #delta fijo (paso la aprobacion del equipo)
    return redondear_a_int(tamanno/3.0 - delta) 

def posicionar_imagen(imagen,cara_frente,cara_izquierda,cara_derecha,cara_atras):
    """ Descripcion:
            Funcion que posiciona las 4 caras del objeto en la imagen(mascara) -- basado en prototipo HolHo

        Args:
            *imagen: mascara donde se pegaran las 4 caras
            *caras_*: las 4 caras de la imagen
        Retorna la mascara con las imagenes pegadas
    """
    w,h = imagen.size
    tamanno_mascara = min(imagen.size)

    delta_imagenes = redondear_a_int( tamanno_mascara/3.0 - aspecto_normal(tamanno_mascara) )

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
    imagen.paste(cara_frente, ( mitad_w, pos_y_frente))
    imagen.paste(cara_izquierda, ( pos_x_izq , mitad_h ))
    imagen.paste(cara_derecha, (pos_x_der , mitad_h ))         
    imagen.paste(cara_atras, ( mitad_w, pos_y_atras))  
    return imagen

##-----------------CREAR LA IMAGEN---------------
def cargar_caras(im,current,frames,giro_imagen_gif_derecha=True):
    """ Descripcion:
            Funcion que carga las 4 caras de la imagen y las devuelve en una lista
            en orden de: cara frente, cara derecha, cara izquierda y cara atras

        Args:
            *im: imagen
            *current: actual frame
            *frames: cantidad de frames de la imagen
            *giro_imagen_gif_derecha: booleano indicando si el gif gira hacia la derecha
    """

    if giro_imagen_gif_derecha: #si gif gira a la derecha
        #por efecto mirrro queda alrevez 
        angulos = [0.0, 270.0, 90.0, 180.0] #frente, derecha, izq, atras
    else: #si gif gira a la izquierda
        angulos = [0.0, 90.0, 270.0, 180.0] #frente, derecha, izq, atras

    caras = []
    for angulo in angulos: #extraer 4 angulos a partir del current
        frame_angulo = (angulo_a_frame(angulo, frames )+current) % frames
        #print ("para angulo", angulo,"es necesario ir al frame ",frame_angulo)
        nueva_im = im[frame_angulo-1].copy()
        
        caras.append(nueva_im) #se ve choro asi ImageChops.invert(imagen_a_guardar)
    return list(caras)

def trim(imag): 
    """ Descripcion:
            Funcion que remueve bordes (o acerca) de una imagen hasta un cierto delta

        *delta: Es el espacio extra anndido alrededor del bbox
    """
    delta = np.min(imag.size)/5 #calibrar esto (paso aprobacion del equipo)

    bg = Image.new(imag.mode,imag.size,imag.getpixel((0,0)))
    diff = ImageChops.difference(imag,bg)
    bbox = diff.getbbox()

    if bbox:  
        tamanno_extra = ( bg.size[0] - bbox[2] , bg.size[1]- bbox[3] )
        if np.min(tamanno_extra) < delta: #no remueve bordes
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


ajustar_aspecto = True 
crop_caras = []

def ajustar_4caras():
    """ Descripcion:
            Funcion que cambia las variables globales para ajustar
            las 4 caras de la imagen proyectada
    """
    global ajustar_aspecto,crop_caras
    ajustar_aspecto = True
    del crop_caras[:] #vacia la lista

def centrar_4caras(caras): #centra
    """ Descripcion:
            Funcion que centra las 4 caras basado en el trim 
            y rellena la imagen para dejarla cuadrada
    """
    global ajustar_aspecto,crop_caras

    for i in range(len(caras)):
        cara = caras[i].copy()

        if ajustar_aspecto: #guarda las dimensiones para centrar de la primera cara
            crop_caras.append(trim(cara)) #para mantener el aspecto del primero
        dimensiones_trim = crop_caras[i]

        nueva_cara = cara.crop(dimensiones_trim) #achicar bordes (centra al centro xd)

        #IMAGENES CUADRADAS (rellena para dejar cuadrado) 
        if nueva_cara.size[0] != nueva_cara.size[1]:
            nuevo_size = np.max(nueva_cara.size)

            imagen_a_guardar = Image.new('RGB', (nuevo_size,nuevo_size), 'black')
            imagen_a_guardar.paste(nueva_cara, ( (nuevo_size - nueva_cara.size[0]) /2, (nuevo_size - nueva_cara.size[1])/2 ))
        else:
            imagen_a_guardar = nueva_cara

        caras[i].close()
        caras[i] = imagen_a_guardar

    if ajustar_aspecto:
        ajustar_aspecto=False


def redimensionar_zoom(caras,tamanno_mascara,zoom):
    """ Descripcion:
            Funcion que redimensiona las caras basado en el zoom actual 
            Ademas de ajustar si el zoom sobrepasa los limites de la iamgen

        Args:
            *caras: 4 imagenes
            *tamanno_mascara: dimensiones de la imagen a colocar las caras
            *zoom: zoom actual
    """
    #nuevo tamanno
    tamanno_actual = int( aspecto_normal(tamanno_mascara) * zoom )

    for i in range(len(caras)): ##---esto se podria paralelizar....
        nueva_im = caras[i].copy()
            
        #REDIMENSIONAR --fijo
        if nueva_im.size[0] >= tamanno_actual : #si tamanno es menor
            #si se ve muy mal probar Antialias
            nueva_im.thumbnail((tamanno_actual,tamanno_actual),Image.BICUBIC) #cara frente
            #thumbnail es un resize manteniendo su aspecto
        else:  #si el zoom supera el tamanno actual de la imagen
            nueva_im = nueva_im.resize((tamanno_actual,tamanno_actual),Image.ANTIALIAS) #cara frente

        ##---------------------------AJUSTAR---------------
        if zoom > 1: #si se sale de los limites del ratio base

            #tamanno seria de tamanno_actual*aspecto_normal para manternerlo
            tamanno = aspecto_normal(tamanno_mascara)

            #zoom al centro de la imagen
            x1 = x2= redondear_a_int( (tamanno_actual - tamanno)/2.0 )
            y1 = y2 = redondear_a_int( (tamanno_actual + tamanno)/2.0 )

            nueva_im = nueva_im.crop((x1, x2, y1, y2))
        elif zoom <1:

            imagen_fondo = Image.new('RGB', (aspecto_normal(tamanno_mascara),aspecto_normal(tamanno_mascara)),'black')
            imagen_fondo.paste(nueva_im, ((imagen_fondo.size[0] - nueva_im.size[0])/2 ,(imagen_fondo.size[1] - nueva_im.size[1])/2))
            nueva_im = imagen_fondo
        """
        w, h = imagen_a_guardar.size
        rad = w/3
        circle = Image.new('L', (rad * 2, rad * 2), 0)
        draw = ImageDraw.Draw(circle)
        draw.ellipse((0, 0, rad * 2, rad * 2), fill=255)
        alpha = Image.new('L', imagen_a_guardar.size, 255)
        alpha.paste(circle.crop((0, 0, rad, rad)), (0, 0))
        alpha.paste(circle.crop((0, rad, rad, rad * 2)), (0, h - rad))
        alpha.paste(circle.crop((rad, 0, rad * 2, rad)), (w - rad, 0))
        alpha.paste(circle.crop((rad, rad, rad * 2, rad * 2)), (w - rad, h - rad))
        imagen_a_guardar.putalpha(alpha)
        #imagen_a_guardar.show()
        #asd  

                    bigsize = (im.size[0] * 3, im.size[1] * 3)

            mask = Image.new('L', bigsize, 0)
            draw = ImageDraw.Draw(mask) 
            draw.ellipse((0, 0) + bigsize, fill=255)
            mask = mask.resize(imagen_a_guardar.size, Image.ANTIALIAS)

            imagen_a_guardar.putalpha(mask)
        """

        caras[i].close()
        caras[i] = nueva_im

def rotar_imagenes(caras,rotacion=0):
    """ Descripcion:
            Funcion que rota las 4 caras para dejarlas en 4 posiciones en la imagen

        Args:
            *caras: 4 caras
            *rotacion: nueva opcion agregada que rota el objeto respecto al plano
        *de_cabeza: 0 para proyeccion hacia arriba, 180 para proyeccion hacia abajo
    """     
    de_cabeza = 0 #para que este de cabeza probar con: 180
    nuevas_caras = list()

    #Image.BICUBIC es de mejor calidad pero se demora 0.02 (el biblinear se demora la nada)

    #actualizacion en rotar por efecto espejo
    if de_cabeza == 180:
        nuevas_caras.append( caras[3].rotate(180+de_cabeza+rotacion,Image.BILINEAR)) #,expand=True) )  #cara frente
    else:
        nuevas_caras.append( caras[0].rotate(180+rotacion,Image.BILINEAR)) #,expand=True) )  #cara frente

    nuevas_caras.append( caras[1].rotate(270 +de_cabeza+rotacion,Image.BILINEAR)) #,expand=True) )  #cara der
    nuevas_caras.append( caras[2].rotate(90+de_cabeza+rotacion,Image.BILINEAR)) #,expand=True))   #cara izq

    #actualizacion en rotar por efecto espejo
    if de_cabeza == 180:
        nuevas_caras.append( caras[0].rotate(0+de_cabeza+rotacion,Image.BILINEAR))#,expand=True))      #cara atras
    else:
        nuevas_caras.append( caras[3].rotate(0+rotacion,Image.BILINEAR))#,expand=True))      #cara atras
    return nuevas_caras


def crear_mascara():
    """ Descripcion:
            Funcion que crea la mascara
        *w,h: dimensiones para crear la mascara
    """
    w,h =  1280,720 #854,480 #(se demora como 0.2 y necesita imagenes con mayor resolucion 640x640) costoso? 
    return Image.new('RGB', (w,h), 'black')

def split_str(seq, chunk, skip_tail=False):
    lst = []
    if chunk <= len(seq):
        lst.extend([seq[:chunk]])
        lst.extend(split_str(seq[chunk:], chunk, skip_tail))
    elif not skip_tail and seq:
        lst.extend([seq])
    return lst


#####-------CODIGO PARA MOVER-----------------------
name_image = raw_input("Nombre de imagen GIF: ")

#Asumiendo que estan en la misma carpeta
im = Image.open("../imagenes/"+name_image+".gif")
print(im.format, im.size, im.mode)

frames = cantidad_frames(im)+1 #asumiendo que los frames da vuelta 360
print "La imagen tiene %d frames"%(frames)

giro_imagen_gif_derecha = True         
#para organo si (calibracion en base al giro por defecto de la imagen)
#para salto no (false)

import sys
todos_frames = [ImageOps.mirror(f) for f in ImageSequence.Iterator(im)]
im.close()
print "tmanno de la imagen leida " ,sys.getsizeof(im)
print "tmaanno de la imagen en formato lista ", sys.getsizeof(todos_frames)

#Movimiento de la imagen a traves de actual
current = 0 #frame en el momento (actual)--asociado al giro
zoom = 1.0  #zoom en el momento (actual)
rotacion = 0 #grado de rotacion (actual)

#--> MOSTRAR LA PRIMERA IMAGEN SIN REALIZAR NINGUNA ACCION

#con memoria (Si no realiza mov)
#Preproceso: Cargar->Centrar->rellenar->zoom
caras_memoria = cargar_caras(todos_frames,current,frames,giro_imagen_gif_derecha) #para que zoom sea mas rapido
centrar_4caras(caras_memoria) #con respecto al objeto (bbox) --solo cambia con derech e izq

print "tamanno de caras ",sys.getsizeof(caras_memoria)

#Para posicionar la imagen
#mascara = crear_mascara()

#tamanno_mascara = min(mascara.size)
#redimensionar_zoom(caras_memoria,tamanno_mascara,zoom)

#cara_frente,cara_izquierda,cara_derecha,cara_atras = rotar_imagenes(caras_memoria)
#imagen_Final = posicionar_imagen(mascara,cara_frente,cara_izquierda,cara_derecha,cara_atras)

#imagen_Final.show()

mostrar_primera = True

while(True):
    if mostrar_primera:
        opcion = '1'
        mostrar_primera=False

    else:
        opcion = raw_input("Girar: \n1 Derecha \n2 Izquierda \nZoom:\n3 Zoom in \n4 Zoom out\nRotar:\n5 Horario \n6 Antihorario \n7 Centrar\n8 Agregar texto\n")

    start_time = time.time()

    #CLIENTE MANDAA EL MENSAJE -> OPCION + CANTIDAD

    ##MAPEA LA OPERACION A LAS VARIABLES NECESARIAS
    if opcion == '1': # movimiento girar derecha
        giro_derecha = True
        cantidad = 1

    elif opcion == '2': #movimiento girar izquierda
        giro_derecha = False
        cantidad = 1

    elif opcion == '3': #hacer zoom
        zoom_in = True
        cantidad = 0.1

    elif opcion == '4': #quitar zoom
        zoom_in = False
        cantidad = 0.1

    elif opcion== '5': #rotar horario
        rotar_horario = True
        cantidad = 15 #grados

    elif opcion == '6': #rotar antihorario
        rotar_horario =False
        cantidad = 15 #grados

    ##FUNCIONES EXTRA AGREGADAS...
    elif opcion == '7': #calibrar
        print "funcion activada necesarioa agregarlo"
        ajustar_4caras() #ajusta para que la proxima cara mostrada este centrada

        #continue
    elif opcion == '8':
        texto_proyeccion = raw_input("Ingrese texto: ")

    elif opcion == 'algo':
        print "volver al principio... (reset)"
    else:
        print("Movimiento invalido")
        continue

    #**************configuracion de la operacion*******************

    if opcion == '1' or opcion == '2': #funcion giro
        funcion_giro = True
    else:
        funcion_giro = False

    if opcion == '3' or opcion == '4': #solo zoom
        funcion_zoom = True
        memoria = True
    else:
        funcion_zoom = False
        memoria = False

    if opcion == '5' or opcion == '6': #funcion rotar (Tambien tiene memoria)
        funcion_rotar = True
        memoria =True
    else:
        memoria = False
        funcion_rotar = False

    #TODO LO DE ARRIBA (HASTA EL WHILE) ES EL MENSAJE QUE MANDA EL CLIENTE 
    #TODO LO DE ABAJO ES LA OPERACION REALIZADA POR EL SERVER

    ##COMIENZA EL PROCESO. -------ASIGNAR MOVIMIENTO--------

    if funcion_giro:
        if not giro_imagen_gif_derecha: #gif gira a izquierda
            giro_derecha = not giro_derecha

        ##asignar movimiento
        if giro_derecha:       #derecha
            current-=cantidad
        elif not giro_derecha: #izquierda
            current+=cantidad
        current = current%frames

    if funcion_zoom:
        if zoom_in:
            zoom += cantidad
        else:
            zoom -=cantidad

        #tamanno maximo permitido (calibrar)
        tamanno_actual = int( aspecto_normal(tamanno_mascara) * zoom )
        if zoom <= 0 or tamanno_actual <= 20: #tamano minimo permitido
            texto_proyeccion = "!"
            texto_advertencia = True
            #remueve el zoom aplicado
            zoom+=cantidad
        elif tamanno_actual >= 1000: #tamanno maximo permitido
            texto_proyeccion = '!'
            texto_advertencia = True
            #remueve el zoom aplicado
            zoom-=cantidad

    if funcion_rotar:
        if rotar_horario:
            rotacion += cantidad #grados
        else:
            rotacion -= cantidad

    ##-----------------CREAR LA IMAGEN (CON MEMORIA---------------
    if memoria and not ajustar_aspecto: #si es que no ha centrado (ajustar aspecto agregado)
        print "utiliza memoria"
        #solo para zoom (utiliza la que tiene en memoria)
        caras = [cara.copy() for cara in caras_memoria] #ya que cada cara es una referencia

    else: #CARGAR nueva imagen y preprocesar -->> juntar cargar + centar + rellenar

        tiempo_cargar = time.time()

        ####-----------PREPROCESAR (CENTrAR + RELLENAR)---------------------
        caras = cargar_caras(todos_frames,current,frames,giro_imagen_gif_derecha)

        centrar_4caras(caras) #con respecto al objeto (bbox) --solo cambia con derech e izq

        print "TIEMPO DEMORADO EN CARGAR : ",time.time()-tiempo_cargar

        #---ACTUALIZA CARAS_MEMORIA POR REFERENCIa----
        #borrar referencia vieja
        for cara in caras_memoria:
            cara.close()
        del caras_memoria[:] #vacia la lista
        caras_memoria += [cara.copy() for cara in caras] #actualizar

    #centrar_4caras(caras)
    ##------------------PREPROCESAR CARAS (CENTRAR, RELLENAR, REDIMENSIONAR( + ajuste ZOOM) y ROTAR)----------------------------
    tiempo_crearmascara = time.time()
    mascara = crear_mascara()
    print "TIEMPO EN CREAR MASCARA: ",time.time()-tiempo_crearmascara

    tiempo_zoom = time.time()
    tamanno_mascara = min(mascara.size)
    redimensionar_zoom(caras,tamanno_mascara,zoom) #quizas ver esto que devuelva otra cosa
    print "TIEMPO DEMORADO EN ZOOM: ",time.time()-tiempo_zoom


    #agregar texto (**EXTRA**) --tambien para mensaje advertencia
    if 'texto_proyeccion' in locals(): #texto
        for cara in caras:

            imagen_texto = Image.new('RGB', cara.size,'black')
            fnt = ImageFont.truetype('/Pillow/Tests/fonts/DejaVuSans.ttf',20)#.load("arial.pil")#.truetype('/Pillow/Tests/fonts/DejaVuSans.ttf',15) #o FreeMono

            draw = ImageDraw.Draw(imagen_texto)
            w_draw, h_draw = draw.textsize(texto_proyeccion,font=fnt)

            if w_draw > imagen_texto.size[0]: #subdividir en textos
                veces = w_draw/imagen_texto.size[0]

                nuevo_string = split_str(texto_proyeccion,len(texto_proyeccion)/(veces+1))
                texto_proyeccion = '\n'.join(nuevo_string)
                w_draw, h_draw = draw.textsize(texto_proyeccion,font=fnt)

            if 'texto_advertencia' in locals(): #texto de advertencia en la esquina
                pos = ( w_draw/2 , 0)
            else:
                pos = ( (aspecto_normal(tamanno_mascara) - w_draw)/2, 0)

            draw.text(pos, texto_proyeccion,font=fnt, fill='white')
            draw.text((pos[0]+1,pos[1]+1), texto_proyeccion,font=fnt, fill='white')
            #draw.text((pos[0]-1,pos[1]-1), texto_proyeccion,font=fnt, fill='white')

            #para el efecto espejo del texto 
            imagen_texto = ImageOps.mirror(imagen_texto)

            nueva_cara = ImageChops.add(imagen_texto,cara) #probar add_modulo

            #actualizar referencia
            caras[caras.index(cara)] = nueva_cara
    
            #draw.line( (cara.size[0]/2, 0) + (cara.size[0]/2,cara.size[1]/2) ,fill='white')
            cara.close()
            imagen_texto.close()
            del draw

        del texto_proyeccion
        if 'texto_advertencia' in locals():
            del texto_advertencia

    tiempo_rotar = time.time()
    #ROTAR
    cara_frente,cara_derecha,cara_izquierda,cara_atras = rotar_imagenes(caras,rotacion)
    print "TIEMPO EN ROTAR: ",time.time()-tiempo_rotar

    #data = np.asarray(cara_frente,dtype='int32')
    #cara_frente = Image.fromarray(np.uint8(data),'RGB')

    ##-------------------------POSICIONAR IMAGEN EN 4 LUGARES-------------------  --fijo
    tiempo_posicionar = time.time()
    imagen_Final = posicionar_imagen(mascara,cara_frente,cara_izquierda,cara_derecha,cara_atras)
    print "TIEMPO EN POSICIONAR: ",time.time()-tiempo_posicionar

    #mostrar y guardar

    timeextra = time.time()
    imagen_Final.show()
    imagen_Final.save('imagen.png')

    print "TIEMPO DEMORADO EN GUARDAR Y MOSTRAR: ",time.time()-timeextra

    #data = np.asarray(mascara)
    #figura.set_array(data)
    
    #del cara_frente
    #del cara_atras
    #del cara_izquierda
    #del cara_derecha
    print "Demoro %f segundos en total"%(time.time() - start_time)
