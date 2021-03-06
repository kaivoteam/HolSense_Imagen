from PIL import Image, ImageFile, ImageChops,ImageOps,ImageDraw,ImageFont,  ImageSequence

import time,matplotlib
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation
##ejecutar esto en un proceso para que se guarden las variables...

##------------------DATOS NECESARIOS-----------------------------
frames = 0
imagen_trabajada = None

#Movimiento de la imagen a traves de actual
current = 0 #frame en el momento (actual)
zoom = 1.0  #zoom en el momento (actual)
rotacion = 0 #grado de rotacion (actual)

caras_memoria= None #se guarda en server

#definir en base al diccionario
giro_imagen_gif_derecha = True


def inicializar(nombre_imagen):
    global frames,imagen_trabajada,caras_memoria,current,zoom,rotacion

    im = Image.open("../../imagenes/"+nombre_imagen+".gif")
    print(im.format, im.size, im.mode)

    frames = cantidad_frames(im)+1 #asumiendo que los frames da vuelta 360

    imagen_trabajada = [ImageOps.mirror(f) for f in ImageSequence.Iterator(im)]
    im.close()

    caras_memoria = cargar_caras(imagen_trabajada,current,frames)
    centrar_4caras(caras_memoria)

    mascara = crear_mascara()
    tamanno_mascara = min(mascara.size)

    redimensionar_zoom(caras_memoria,tamanno_mascara,zoom)
    cara_frente,cara_derecha,cara_izquierda,cara_atras = rotar_imagenes(caras_memoria,rotacion)
    imagen_Final = posicionar_imagen(mascara,cara_frente,cara_izquierda,cara_derecha,cara_atras)

    fig, ax = plt.subplots()

    data = np.asarray(imagen_Final)
    return fig,ax.imshow(data, animated=True)



#####-------CODIGO PARA MOVER-----------------------
def hacer(opcion,cantidad,texto_proyectar="",figura=None):
    global current,zoom,rotacion,giro_imagen_gif_derecha,frames

    #time.sleep(1000)
    #figura.ion()
    #input("Ingrese texto: ")
    #definir cual es el mensaje de "opcion" que se manda

    memoria = True
    limite = False

    ##MAPEA LA OPERACION A LAS VARIABLES NECESARIAS
    funcion_giro = False
    funcion_zoom = False
    funcion_rotar = False
    if opcion == '1': # movimiento girar viendo la derecha del oobjeto
        funcion_giro = True
        giro_derecha = True
        memoria = False

    elif opcion == '2': #movimiento gira viendo la izquierda del objeto
        funcion_giro = True
        giro_derecha = False
        memoria = False

    elif opcion == '3': #hacer zoom
        funcion_zoom = True
        zoom_in = True

    elif opcion == '4': #quitar zoom
        funcion_zoom = True
        zoom_in = False

    elif opcion== '5': #rotar horario
        funcion_rotar = True
        rotar_horario = True

    elif opcion == '6': #rotar antihorario
        funcion_rotar = True
        rotar_horario =False

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
        tamanno_mascara = tamanno_mascara_min()
        tamanno_actual = int( aspecto_normal(tamanno_mascara) * zoom )
        if zoom <= 0 or tamanno_actual <= 20: #tamano minimo permitido
            limite = True
            #remueve el zoom aplicado
            zoom+=cantidad
        elif tamanno_actual >= 1000: #tamanno maximo permitido
            limite=True
            #remueve el zoom aplicado
            zoom-=cantidad

    if funcion_rotar:
        if rotar_horario:
            rotacion += cantidad #grados
        else:
            rotacion -= cantidad

    realizar_operacion(current,zoom,rotacion,memoria,limite,texto_proyectar,figura)


def realizar_operacion(current=0,zoom=1.0,rotacion=0,memoria=False,limite=False,texto_proyectar="",figura=None):
    global imagen_trabajada,caras_memoria,frames,giro_imagen_gif_derecha #variables almacenadas

    ##-----------------CREAR LA IMAGEN (CON MEMORIA---------------
    if memoria and not ajustar_aspecto: #si es que no ha centrado (ajustar aspecto agregado)
        #solo para zoom (utiliza la que tiene en memoria)
        caras = [cara.copy() for cara in caras_memoria] #ya que cada cara es una referencia

    else: #CARGAR nueva imagen y preprocesar -->> juntar cargar + centar + rellenar
        caras = cargar_caras(imagen_trabajada,current,frames,giro_imagen_gif_derecha)
        centrar_4caras(caras) #con respecto al objeto (bbox) --solo cambia con derech e izq

        #---ACTUALIZA CARAS_MEMORIA POR REFERENCIa----
        #borrar referencia vieja
        for cara in caras_memoria:
            cara.close()
        del caras_memoria[:] #vacia la lista
        caras_memoria += [cara.copy() for cara in caras] #actualizar

    ##------------------PREPROCESAR CARAS (CENTRAR, RELLENAR, REDIMENSIONAR( + ajuste ZOOM) y ROTAR)----------------------------
    mascara = crear_mascara()

    tamanno_mascara = min(mascara.size)
    redimensionar_zoom(caras,tamanno_mascara,zoom) #quizas ver esto que devuelva otra cosa

    #agregar texto (**EXTRA**) --tambien para mensaje advertencia
    if limite:
        texto_proyectar = "!"

    if texto_proyectar != "": #texto
        asd
        for cara in caras:

            imagen_texto = Image.new('RGB', cara.size,'black')
            fnt = ImageFont.truetype('/Pillow/Tests/fonts/DejaVuSans.ttf',20)#.load("arial.pil")#.truetype('/Pillow/Tests/fonts/DejaVuSans.ttf',15) #o FreeMono

            draw = ImageDraw.Draw(imagen_texto)
            w_draw, h_draw = draw.textsize(texto_proyectar,font=fnt)

            if w_draw > imagen_texto.size[0]: #subdividir en textos
                veces = w_draw/imagen_texto.size[0]

                nuevo_string = split_str(texto_proyectar,len(texto_proyectar)/(veces+1))
                texto_proyectar = '\n'.join(nuevo_string)
                w_draw, h_draw = draw.textsize(texto_proyectar,font=fnt)

            if limite: #texto de advertencia en la esquina
                pos = ( w_draw/2 , 0)
            else:
                pos = ( (aspecto_normal(tamanno_mascara) - w_draw)/2, 0)

            draw.text(pos, texto_proyectar,font=fnt, fill='white')
            draw.text((pos[0]+1,pos[1]+1), texto_proyectar,font=fnt, fill='white')
            #draw.text((pos[0]-1,pos[1]-1), texto_proyectar,font=fnt, fill='white')

            #para el efecto espejo del texto 
            imagen_texto = ImageOps.mirror(imagen_texto)

            nueva_cara = ImageChops.add(imagen_texto,cara) #probar add_modulo

            #actualizar referencia
            caras[caras.index(cara)] = nueva_cara
    
            cara.close()
            imagen_texto.close()
            del draw

        del texto_proyectar
        #if 'texto_advertencia' in locals():
         #   del texto_advertencia  #probar limite cambiar a false


    cara_frente,cara_derecha,cara_izquierda,cara_atras = rotar_imagenes(caras,rotacion)

    imagen_Final = posicionar_imagen(mascara,cara_frente,cara_izquierda,cara_derecha,cara_atras)

    data = np.asarray(imagen_Final)
    figura.set_array(data)
    #plt.imshow(imagen_Final)



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
def cargar_caras(todos_frames,current,frames,giro_imagen_gif_derecha=True):
    """ Descripcion:
            Funcion que carga las 4 caras de la imagen y las devuelve en una lista
            en orden de: cara frente, cara derecha, cara izquierda y cara atras

        Args:
            *todos_frames: todos los frames de la imagen (en una lista)
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
        nueva_im = todos_frames[frame_angulo-1].copy()
        
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

def tamanno_mascara_min():
    w,h =  1280,720
    return min([w,h])

def split_str(seq, chunk, skip_tail=False):
    lst = []
    if chunk <= len(seq):
        lst.extend([seq[:chunk]])
        lst.extend(split_str(seq[chunk:], chunk, skip_tail))
    elif not skip_tail and seq:
        lst.extend([seq])
    return lst