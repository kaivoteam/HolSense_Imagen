import time
from PIL import Image, ImageFile, ImageChops,ImageOps

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
    delta = 0.0
    return int( round(tamanno /3.0 - delta) )

def redondear_a_int(numero):
    return int(round(numero))

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

    ##-----------------CREAR LA IMAGEN---------------
    #ver el tema de la resolucion de la imagen

    caras = []
    for angulo in angulos: #extraer 4 angulos a partir del current
        frame_angulo = (angulo_a_frame(angulo, frames )+current) % frames
        print ("para angulo", angulo,"es necesario ir al frame ",frame_angulo)
        im.seek(frame_angulo-1)

        #imagenes cuadradas
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

        caras.append(nueva_im.copy())

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

    ##-------------------------SITUAR IMAGEN EN 4 POSICIONES-------------------
    #Se presentan dos dimensiones por si se hace zoom y la dimension actual es menor a la normal
    dimension_normal = aspecto_normal(tamanno_mascara) #dimension fija para situar las caras
    dimension_actual = min(cara_frente.size)           #dimension actual, despues de hacer zoom
    #con zoom = 1 ==> dimension_normal = dimension_actual

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

    #mostrar y guardar
    mascara.show()
    mascara.save('imagen.png')
    #guardar?
    
    print "Demoro %f segundos en total"%(time.time() - start_time)
