import time
from PIL import Image, ImageFile, ImageChops,ImageOps

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

#####-------CODIGO PARA MOVER-----------------------

name_image = raw_input("Nombre de imagen GIF: ")

#Asumiendo que estan en la misma carpeta
im = Image.open("./imagenes/"+name_image+".gif")
print(im.format, im.size, im.mode)

frames = cantidad_frames(im)+1 #asumiendo que los frames da vuelta 360
print "La imagen tiene %d frames"%(frames)

#4 imagenes en 4 angulos
angulos = [0.0, 90.0, 180.0, 270.0]

tamanno_original = im.size[0] #para imagenes cuadradas

#caracteristicas de calibracion
aspecto_normal = 0.2 # o 1/5

#Movimiento de la imagen a traves de actual
current = 0 #frame en el momento (actual)
zoom = 1.0  #zoom en el momento (actual)

while(True):
    opcion = raw_input("1 Derecha \n2 Izquierda \n3 Zoom in \n4 Zoom out\n")

    #tamanno_actual = int(tamanno_original*aspecto_normal*zoom)

    start_time = time.time()

    #asignar cantidad de mov

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

    ##-----------------CREAR LA IMAGEN---------------
    caras = []
    for angulo in angulos: #extraer 4 angulos a partir del current
        frame_angulo = (angulo_a_frame(angulo, frames )+current) % frames
        print ("para angulo", angulo,"es necesario ir al frame ",frame_angulo)
        im.seek(frame_angulo-1)

        caras.append(im.copy())

    #calibrar esto
    w,h = 920,512#caras[0].size
    mascara = Image.new('RGB', (w,h))

    #nuevo tamanno
    tamanno_actual = int(tamanno_original*aspecto_normal*zoom)

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
        #imagenes cuadradas
        mitad = tamanno_actual/2

        #tamanno seria de tamanno_actual*aspecto_normal para manternerlo
        tamanno = int(tamanno_original*aspecto_normal)
        x1 = x2= mitad - tamanno/2
        y1 = y2 = mitad + tamanno/2

        cara_frente = cara_frente.crop((x1, x2, y1, y2))
        cara_izquierda = cara_izquierda.crop((x1, x2, y1, y2))
        cara_derecha = cara_derecha.crop((x1, x2, y1, y2))
        cara_atras = cara_atras.crop((x1, x2, y1, y2))


    dimension = cara_frente.size[0]#para juntar imagenes

    #calibrar todo esto
    #distancia en width
    pos_y_frente = h- h/4 - dimension/2  #-dimension/2 para centrar
    dist_y = h/2
    #distancia en height
    pos_x_der = w - w/3 - dimension/2
    dist_x = w/3


    mascara.paste(cara_frente, ( (w-dimension)/2, pos_y_frente))
    mascara.paste(cara_izquierda, ( pos_x_der - dist_x , (h - dimension)/2))
    mascara.paste(cara_derecha, (pos_x_der , (h - dimension)/2))         
    mascara.paste(cara_atras, ( (w-dimension)/2, pos_y_frente - dist_y))   

    #mostrar y guardar
    mascara.show()
    #guardar?
    
    print "Demoro %f segundos en total"%(time.time() - start_time)

   
#size = w/4
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
)"""