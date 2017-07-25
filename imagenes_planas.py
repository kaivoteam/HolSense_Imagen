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
        

    w,h = 920,512#caras[0].size
    mascara = Image.new('RGB', (w,h))
                            
    #achicarlos tamanno
    size = w/5

    caras[0].thumbnail((size,size)) #cara frente
    cara_frente = caras[0].rotate(180)#,expand=True)

    caras[1].thumbnail((size,size)) #cara izquierda
    cara_izquierda = caras[1].rotate(90)#,expand=True)
    #cara_izquierda = cara_izquierda.resize((size,size),Image.ANTIALIAS)
    print cara_izquierda.size

    caras[2].thumbnail((size,size)) #cara derecha
    cara_derecha = caras[2].rotate(270)#,expand=True)
    print cara_derecha.size

    caras[3].thumbnail((size,size)) #cara atras
    cara_atras = caras[3].rotate(0)#expand=True)

    #calibrar todo esto
    #size_w, size_h = caras[0].size
    #distancia en width
    pos_y_frente = h- h/4 - size/2  #-size/2 para centrar
    dist_y = h/2
    #distancia en height
    pos_x_der = w - w/3 - size/2
    dist_x = w/3

    mascara.paste(cara_frente, ( (w-size)/2, pos_y_frente))
    if rotacion == -1:
        mascara.paste(cara_izquierda, ( pos_x_der - dist_x , (h - size)/2))
        mascara.paste(cara_derecha, (pos_x_der , (h - size)/2))         
    #if rotacion == 1:
    #   mascara.paste(caras[1], (w-w/3, h/2)) #cara izquierda
    #   mascara.paste(caras[2], (w/3, h/2))   #cara derecha
    mascara.paste(cara_atras, ( (w-size)/2, pos_y_frente - dist_y))   
    #mascara.show()
    #mascara.save("imagen.png")

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