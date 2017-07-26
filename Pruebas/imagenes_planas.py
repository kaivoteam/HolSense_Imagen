from PIL import Image
import time

# write GIF animation
from PIL import Image, ImageFile, ImageChops
from PIL.GifImagePlugin import _imaging_gif, RAWMODE, _convert_mode, getheader, getdata, get_interlace, _get_local_header

def save_sequence(ims, filename):
    im = ims[0]
    fp = open(filename, 'wb')

    if hasattr(im, 'encoderinfo'):
        im.encoderinfo.update(im.info)
    if _imaging_gif:
        # call external driver
        try:
            _imaging_gif.save(im, fp, filename)
            return
        except IOError:
            pass  # write uncompressed file

    if im.mode in RAWMODE:
        im_out = im.copy()
    else:
        im_out = _convert_mode(im, True)

    # header
    if hasattr(im, 'encoderinfo'):
        try:
            palette = im.encoderinfo["palette"]
        except KeyError:
            palette = None
            im.encoderinfo["optimize"] = im.encoderinfo.get("optimize", True)
    else:
        palette = None
        im.encoderinfo = {}

    save_all = True
    if save_all:
        previous = None

        first_frame = None
        for im_frame in ims:
            im_frame = _convert_mode(im_frame)

            # To specify duration, add the time in milliseconds to getdata(),
            # e.g. getdata(im_frame, duration=1000)
            if not previous:
                # global header
                first_frame = getheader(im_frame, palette, im.encoderinfo)[0]
                first_frame += getdata(im_frame, (0, 0), **im.encoderinfo)
            else:
                if first_frame:
                    for s in first_frame:
                        fp.write(s)
                    first_frame = None

                # delta frame
                delta = ImageChops.subtract_modulo(im_frame, previous.copy())
                bbox = delta.getbbox()

                if bbox:
                    # compress difference
                    for s in getdata(im_frame.crop(bbox),
                                     bbox[:2], **im.encoderinfo):
                        fp.write(s)
                else:
                    # FIXME: what should we do in this case?
                    pass
            previous = im_frame
        if first_frame:
            save_all = False
    if not save_all:
        header = getheader(im_out, palette, im.encoderinfo)[0]
        for s in header:
            fp.write(s)

        flags = 0

        if get_interlace(im):
            flags = flags | 64

        # local image header
        _get_local_header(fp, im, (0, 0), flags)

        im_out.encoderconfig = (8, get_interlace(im))
        ImageFile._save(im_out, fp, [("gif", (0, 0)+im.size, 0,
                                      RAWMODE[im_out.mode])])

        fp.write(b"\0")  # end of image data

    fp.write(b";")  # end of file

    if hasattr(fp, "flush"):
        fp.flush()

def cantidad_frames(imagen):
    cantidad_frames = 0
    try:
        while 1:
            im.seek(cantidad_frames) #va al frame 
            cantidad_frames+=1
    except EOFError:
        pass
    return cantidad_frames-1
def angulo_a_frame(angulo,frames):
    return int( round( angulo * frames / 360.0) )

def aspecto_normal(tamanno):
    delta = 0.0 #se modificara
    return int( round(tamanno /3.0 - delta) )

def redondear_a_int(numero):
    return int(round(numero))

###---------------CODIGOO--------------------

name_image = raw_input("Nombre de imagen + extension: ")

start_time = time.time()
#Asumiendo que estan en la misma carpeta
im = Image.open("./imagenes/"+name_image)
print(im.format, im.size, im.mode)

frames = cantidad_frames(im)+1 #asumiendo que los frames da vuelta 360

secuencia = []
tiempos_crear_frames =[]
for i in range(frames):
    tiempo1 = time.time()
    caras = []

    #el movimiento de la imagen seria a traves del indice
    indice = i
    #im.seek(indice)
    print("En base al indice: ",indice)

    rotacion = -1 #hacia la izquierda


    if frames == 1: #imagen plana
        for i in range(4): #repeticion de la misma cara
            caras.append(im)
    
    if frames > 1: #gif
        #4 imagenes en 4 angulos
        angulos = [0.0, 90.0, 180.0, 270.0]

        for angulo in angulos: #extraer 4 angulos
            frame_angulo = (angulo_a_frame(angulo, frames )+indice) % frames
            print ("para angulo", angulo,"es necesario ir al frame ",frame_angulo)
            im.seek(frame_angulo-1)
        
            caras.append(im.copy())
        
    if caras[0].size[0] != caras[0].size[1]: #imagenes no cuadradas
        for i in range(len(caras)):
            im = caras[i]
            longer_side = max(im.size)
            horizontal_padding = (longer_side - im.size[0]) / 2
            vertical_padding = (longer_side - im.size[1]) / 2
            nueva_im = im.crop(
                (
                    -horizontal_padding,
                    -vertical_padding,
                    im.size[0] + horizontal_padding,
                    im.size[1] + vertical_padding
                )
            )
            caras[i] = nueva_im

    #calibrar esto
    w,h = 854,480 #1280,720 #quizas es muy pesada la imagen con esa resolucion
    mascara = Image.new('RGB', (w,h))
    tamanno_mascara = min(w,h)

    #nuevo tamanno
    tamanno_actual = int( aspecto_normal(tamanno_mascara) )

    #para imagenes no cuadradas podria cambiarse por resize
    caras[0].thumbnail((tamanno_actual,tamanno_actual),Image.ANTIALIAS) #cara frente
    cara_frente = caras[0].rotate(180)#,expand=True)
    caras[1].thumbnail((tamanno_actual,tamanno_actual),Image.ANTIALIAS) #cara izquierda
    cara_izquierda = caras[1].rotate(90)#,expand=True)
    caras[2].thumbnail((tamanno_actual,tamanno_actual),Image.ANTIALIAS) #cara derecha
    cara_derecha = caras[2].rotate(270)#,expand=True)
    caras[3].thumbnail((tamanno_actual,tamanno_actual),Image.ANTIALIAS) #cara atras
    cara_atras = caras[3].rotate(0)#,expand=True)


    ##-------------------------SITUAR IMAGEN EN 4 POSICIONES-------------------
    #Se presentan dos dimensiones por si se hace zoom y la dimension actual es menor a la normal
    dimension_normal = aspecto_normal(tamanno_mascara) #dimension fija para situar las caras
    dimension_actual = min(cara_frente.size)           #dimension actual, despues de hacer zoom

    #calibrar todo esto (basado en Holho y dejar un tamanno de imagen al medio)
    delta_dimensiones = (dimension_normal - dimension_actual)
    delta_dimensiones2 = w- dimension_actual
    delta_dimensiones3 =  h- dimension_actual

    pos_y_atras = redondear_a_int( delta_dimensiones/2.0 ) #primer tercio de la imagen superior
    pos_y_frente = redondear_a_int(  delta_dimensiones/2.0 + 2.0*dimension_normal  ) # desde la dos tercios de la imagen inferior

    pos_x_der =  redondear_a_int( delta_dimensiones2/2.0 + dimension_normal ) 
    pos_x_izq =  redondear_a_int( delta_dimensiones2/2.0 - dimension_normal )

    mitad_w = redondear_a_int(  delta_dimensiones2 /2.0 )
    mitad_h = redondear_a_int(  delta_dimensiones3/2.0 )

    mascara.paste(cara_frente, ( mitad_w, pos_y_frente))
    mascara.paste(cara_izquierda, ( pos_x_izq , mitad_h ))
    mascara.paste(cara_derecha, (pos_x_der , mitad_h ))         
    mascara.paste(cara_atras, ( mitad_w, pos_y_atras))   


    secuencia.append(mascara.copy())
    tiempos_crear_frames.append(time.time()-tiempo1)

#mostrar y guardar ultima
mascara.show()
mascara.save("imagen.png")

#guardar secuencia
if len(secuencia)>1:
    save_sequence(secuencia, 'out.gif')

import numpy as np
print "Demoro %f segundos en promedio por frame"%(np.mean(tiempos_crear_frames))
print "Demoro %f segundos en total"%(time.time() - start_time)