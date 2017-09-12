from PIL import Image, ImageFile, ImageChops,ImageOps,ImageDraw,ImageFont,  ImageSequence

import time
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

    im = Image.open("./imagenes/"+nombre_imagen+".gif")
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

    imagen_Final.show()


#####-------CODIGO PARA MOVER-----------------------
def hacer(opcion,cantidad=0,texto_proyectar=""):
    global current,zoom,rotacion,giro_imagen_gif_derecha,frames
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

    elif opcion== '5': #rotar horario-antihorario
        funcion_rotar = True


    elif opcion== '-': #reset total
        reset('0')
        memoria = False

    elif opcion == '0': #Nueva funcion: reset
        tipo_reset = raw_input("Ingrese tipo:\n1 Giro\n2 Zoom\n3 Rotacion\n0 Todas\n")
        reset(tipo_reset)
        memoria = False

    elif opcion == '7': #nueva funcion: centrar
        ajustar_4caras()

    ##COMIENZA EL PROCESO. -------ASIGNAR MOVIMIENTO--------
    if funcion_rotar:
        rotacion += 180 #da vuelta de cabeza
        rotacion = rotacion % 360

    if funcion_giro:
        if not giro_imagen_gif_derecha: #gif gira a izquierda
            giro_derecha = not giro_derecha

        if rotacion == 180: #objeto de cabeza
            giro_derecha = not giro_derecha

        ##asignar movimiento
        if giro_derecha:       #derecha
            current-= redondear_a_int(cantidad*frames)
        elif not giro_derecha: #izquierda
            current+= redondear_a_int(cantidad*frames)
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
            texto_proyectar = "zoom minimo"
            #remueve el zoom aplicado
            zoom+=cantidad
        elif tamanno_actual >= 1000: #tamanno maximo permitido
            limite=True
            texto_proyectar = "zoom maximo"
            #remueve el zoom aplicado
            zoom-=cantidad

    realizar_operacion(current,zoom,rotacion,memoria,limite,texto_proyectar)


def realizar_operacion(current=0,zoom=1.0,rotacion=0,memoria=False,limite=False,texto_proyectar=""):
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
    if texto_proyectar != "" or limite: #texto
        colocar_texto(caras,texto_proyectar,limite)
    
    cara_frente,cara_derecha,cara_izquierda,cara_atras = rotar_imagenes(caras,rotacion)

    imagen_Final = posicionar_imagen(mascara,cara_frente,cara_izquierda,cara_derecha,cara_atras)

    imagen_Final.show()


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
    
    if rotacion == 180: #se dan vuelta las caras
        nuevas_caras.append( caras[2].rotate(90+de_cabeza,Image.BILINEAR)  )#cara izq

    nuevas_caras.append( caras[1].rotate(270 +de_cabeza,Image.BILINEAR)) #,expand=True) )  #cara der
    
    if rotacion != 180:
        nuevas_caras.append( caras[2].rotate(90+de_cabeza+rotacion,Image.BILINEAR)) #,expand=True))   #cara izq

    #actualizacion en rotar por efecto espejo 
    if de_cabeza == 180: #se dan vuelta las caras
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

## Nuevas funciones:

def reset(tipo):
    """ Descripcion:
            Funcion que resetea los indices de la imagen (volviendo al comienzo)

        Args:
            *tipo:  0: Todas (reset completo)
                    1: Giro
                    2: Zoom
                    3: Rotacion
    """
    global current,zoom,rotacion
    if tipo == '0' or tipo == 0:
        current =rotacion=0
        zoom =1
    elif tipo == '1' or tipo ==1:
        current = 0
    elif tipo == '2' or tipo ==2:
        zoom = 1
    elif tipo == '3' or tipo == 3:
        rotacion = 0

def colocar_texto(caras,texto,limite=False):
    """ Descripcion:
            Funcion que posiciona el texto en las 4 caras,
            si es limite anota texto de advertencia. (actualiza por referencia)

        Args:
            *caras: lista de las 4 caras
            *texto: Texto a colocar en la imagen
            *limite: si el texto es de advertencia
    """  
    if limite:
        texto += " alcanzado" 
    for cara in caras:
        if limite:
            tamanno = 18
            color = 'yellow' # or red
        else:
            tamanno = 20
            color = 'white'

        imagen_texto = Image.new('RGB', cara.size,'black')
        try:
            fnt = ImageFont.truetype('/Pillow/Tests/fonts/DejaVuSans.ttf',size=tamanno)
        except:
            try:
                fnt = ImageFont.truetype("arial.ttf", size=tamanno)
            except:
                #cargar fuente por defecto
                fnt = ImageFont.load_default()

        draw = ImageDraw.Draw(imagen_texto)
        w_draw, h_draw = draw.textsize(texto,font=fnt)

        if w_draw > imagen_texto.size[0]: #subdividir en textos
            veces = w_draw/imagen_texto.size[0]

            nuevo_string = split_str(texto,len(texto)/(veces+1))
            texto = '\n'.join(nuevo_string)
            w_draw, h_draw = draw.textsize(texto,font=fnt)

        if limite:
            pos = ( 0, 0) #texto de advertencia en la esquina
        else:
            pos = ( (aspecto_normal(tamanno_mascara_min()) - w_draw)/2, 0)

        draw.text(pos, texto,font=fnt, fill=color)
        draw.text((pos[0]+1,pos[1]+1), texto,font=fnt, fill=color)
        #draw.text((pos[0]-1,pos[1]-1), texto,font=fnt, fill=color)

        #para el efecto espejo del texto 
        imagen_texto = ImageOps.mirror(imagen_texto)

        nueva_cara = ImageChops.add(imagen_texto,cara) #probar add_modulo

        #actualizar referencia
        caras[caras.index(cara)] = nueva_cara

        #draw.line( (cara.size[0]/2, 0) + (cara.size[0]/2,cara.size[1]/2) ,fill='white')
        cara.close()
        imagen_texto.close()
        del draw
