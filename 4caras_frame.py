import time

# write GIF animation
from PIL import Image, ImageFile, ImageChops,ImageOps
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
"""
name_image = raw_input("Nombre de imagen GIF: ")

#Asumiendo que estan en la misma carpeta
im = Image.open("./imagenes/"+name_image+".gif")

print(im.format, im.sizes, im.mode)

frames = cantidad_frames(im)+1 #asumiendo que los frames da vuelta 360

print "La imagen tiene %d frames"%(frames)
current_frame = raw_input("Frame a extraer para generar 4 caras: ")

#el movimiento de la imagen seria a traves del indice
indice = int(current_frame)

#4 imagenes en 4 angulos
angulos = [0.0, 90.0, 180.0, 270.0]

start_time = time.time()

caras = []
for angulo in angulos: #extraer 4 angulos
    frame_angulo = (angulo_a_frame(angulo, frames )+indice) % frames
    print ("para angulo", angulo,"es necesario ir al frame ",frame_angulo)
    im.seek(frame_angulo-1)

    caras.append(im.copy())


w,h = 920,512#caras[0].size
mascara = Image.new('RGB', (w,h))
                        
#achicarlos 1/6 del tamanno
size = w/5
caras[0].thumbnail((size,size)) #cara frente
cara_frente = caras[0].rotate(180)
caras[1].thumbnail((size,size)) #cara izquierda
cara_izquierda = caras[1].rotate(90)
caras[2].thumbnail((size,size)) #cara derecha
cara_derecha = caras[2].rotate(270)
caras[3].thumbnail((size,size)) #cara atras
cara_atras = caras[3].rotate(0)

#calibrar todo esto
#distancia en width
pos_y_frente = h- h/4 - size/2  #-size/2 para centrar
dist_y = h/2
#distancia en height
pos_x_der = w - w/3 - size/2
dist_x = w/3

mascara.paste(cara_frente, ( (w-size)/2, pos_y_frente))
mascara.paste(cara_izquierda, ( pos_x_der - dist_x , (h - size)/2))
mascara.paste(cara_derecha, (pos_x_der , (h - size)/2))         
#if rotacion == 1:
#   mascara.paste(caras[1], (w-w/3, h/2)) #cara izquierda
#   mascara.paste(caras[2], (w/3, h/2))   #cara derecha
mascara.paste(cara_atras, ( (w-size)/2, pos_y_frente - dist_y))   

#mostrar y guardar
mascara.show()
mascara.save("imagen.png")

print "Demoro %f segundos en total"%(time.time() - start_time)
"""

#####-------CODIGO PARA MOVER-----------------------

name_image = raw_input("Nombre de imagen GIF: ")

#Asumiendo que estan en la misma carpeta
im = Image.open("./imagenes/"+name_image+".gif")
print(im.format, im.size, im.mode)

frames = cantidad_frames(im)+1 #asumiendo que los frames da vuelta 360
print "La imagen tiene %d frames"%(frames)

#4 imagenes en 4 angulos
angulos = [0.0, 90.0, 180.0, 270.0]
#Movimiento de la imagen a traves de current
current = 0

#caracteristicas de calibracion
aspecto_normal = 0.2 # o 1/5

while(True):
    movimiento = raw_input("1 Derecha \n2 Izquierda \n")

    #asignar cantidad de mov

    start_time = time.time()

    if movimiento == '1': #derecha
        current +=1 %frames
    elif movimiento == '2': #izquierda
        current -=1 %frames
    else:
        print("Movimiento invalido")
        continue

    if current <0: #ya que solo va en numeros positivos
        current += frames

    caras = []
    for angulo in angulos: #extraer 4 angulos a partir del current
        frame_angulo = (angulo_a_frame(angulo, frames )+current) % frames
        print ("para angulo", angulo,"es necesario ir al frame ",frame_angulo)
        im.seek(frame_angulo-1)

        caras.append(im.copy())

    #calibrar esto
    w,h = 920,512#caras[0].size
    mascara = Image.new('RGB', (w,h))

    print "hola mundo"
                            
    #achicarlos 1/5 del tamanno
    size = int(w*aspecto_normal)
    caras[0].thumbnail((size,size)) #cara frente
    cara_frente = caras[0].rotate(180)#,expand=True)
    caras[1].thumbnail((size,size)) #cara izquierda
    cara_izquierda = caras[1].rotate(90)#,expand=True)
    caras[2].thumbnail((size,size)) #cara derecha
    cara_derecha = caras[2].rotate(270)#,expand=True)
    caras[3].thumbnail((size,size)) #cara atras
    cara_atras = caras[3].rotate(0)#,expand=True)

    #calibrar todo esto
    #distancia en width
    pos_y_frente = h- h/4 - size/2  #-size/2 para centrar
    dist_y = h/2
    #distancia en height
    pos_x_der = w - w/3 - size/2
    dist_x = w/3


    mascara.paste(cara_frente, ( (w-size)/2, pos_y_frente))
    mascara.paste(cara_izquierda, ( pos_x_der - dist_x , (h - size)/2))
    mascara.paste(cara_derecha, (pos_x_der , (h - size)/2))         
    #if rotacion == 1:
    #   mascara.paste(caras[1], (w-w/3, h/2)) #cara izquierda
    #   mascara.paste(caras[2], (w/3, h/2))   #cara derecha
    mascara.paste(cara_atras, ( (w-size)/2, pos_y_frente - dist_y))   

    #mostrar y guardar
    mascara.show()

    #im.seek(current)
    #im.show()
    print "Demoro %f segundos en total"%(time.time() - start_time)


    ##zoom
    zoom = raw_input("1 zoom in \n2 zoom out \n")

    w,h = 920,512#caras[0].size
    mascara = Image.new('RGB', (w,h))
                            
    #aplicar zoom
    #definir un maximo pequenno y grande
    if zoom == '1':
        size = w/4
        #y crop...
        #100px * 100px, starting centro
        #half_the_width = caras[0].size[0] / 2
        #half_the_height = caras[0].size[1] / 2

        #tamanno seria de size*aspecto_normal para manternerlo

        #img2 = img.crop((0, 0, 100, 100))

        #para imagenes no cuadradas
        """ Pad the image to a square
        longer_side = max(img.size)
        horizontal_padding = (longer_side - img.size[0]) / 2
        vertical_padding = (longer_side - img.size[1]) / 2
        img5 = img.crop(
            (
                -horizontal_padding,
                -vertical_padding,
                img.size[0] + horizontal_padding,
                img.size[1] + vertical_padding
            )
        )

"""
    elif zoom == '2':
        size=w/7
    else:
        print("Zoom invalido")
        continue

    caras = []
    for angulo in angulos: #extraer 4 angulos a partir del current
        frame_angulo = (angulo_a_frame(angulo, frames )+current) % frames
        im.seek(frame_angulo-1)

        caras.append(im.copy())

    caras[0].thumbnail((size,size),Image.ANTIALIAS) #cara frente
    print cara_frente.size
    print size
    cara_frente = caras[0].rotate(180)#,expand=True)
    caras[1].thumbnail((size,size),Image.ANTIALIAS) #cara izquierda
    cara_izquierda = caras[1].rotate(90)#,expand=True)
    caras[2].thumbnail((size,size),Image.ANTIALIAS) #cara derecha
    cara_derecha = caras[2].rotate(270)#,expand=True)
    caras[3].thumbnail((size,size),Image.ANTIALIAS) #cara atras
    cara_atras = caras[3].rotate(0)#,expand=True)

    #calibrar todo esto
    #distancia en width
    pos_y_frente = h- h/4 - size/2  #-size/2 para centrar
    dist_y = h/2
    #distancia en height
    pos_x_der = w - w/3 - size/2
    dist_x = w/3

    mascara.paste(cara_frente, ( (w-size)/2, pos_y_frente))
    mascara.paste(cara_izquierda, ( pos_x_der - dist_x , (h - size)/2))
    mascara.paste(cara_derecha, (pos_x_der , (h - size)/2))         
    mascara.paste(cara_atras, ( (w-size)/2, pos_y_frente - dist_y))   

    #mostrar y guardar
    mascara.show()

