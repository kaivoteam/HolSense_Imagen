import time
from PIL import Image, ImageFile, ImageChops,ImageOps,ImageSequence

from imports_imagenes import * #del codigo imports_imagenes.py

import time
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import animation

##donde va la cantidad de movimiento (Girar o zoom) ?cliente o server?

#####-------CLIENTE (INDICA QUE ACCION REALIZAR)-----------------------
def funcion_principal(i):
    global current,zoom
    opcion = raw_input("1 Derecha \n2 Izquierda \n3 Zoom in \n4 Zoom out\n")

    start_time = time.time()

    #asignar cantidad de mov
    #asignar un zoom maximo y zoom minimo

    if opcion == '1': # movimiento derecha
        current +=1 
        current = current%frames

    elif opcion == '2': #movimiento izquierda
        current -=1 
        current = current %frames
        #if current <0: #ya que solo va en numeros positivos
         #   current += frames
    elif opcion == '3': #hacer zoom
        zoom+=0.1 #calibrar

    elif opcion == '4': #quitar zoom
        zoom-=0.1
    else:
        print("Movimiento invalido")
        return

    #>>>>>>> REALIZAR ACCION >>>>>>>
    #imagen, frames y angulos vienen de server?

    #annade: memoria
    if opcion =='3' or opcion == '4': #para opciones que solo redimensionan (zoom)
    	memoria = True
    else:
    	memoria = False

    global caras_memoria,todos_frames,figura #se modifica por referencia
    hacer(todos_frames, frames,figura,current,zoom,memoria=memoria,caras_memoria =caras_memoria) ##funcion dentro de imports_imagenes

    print "Demoro %f segundos en total"%(time.time() - start_time)

    return figura,

if __name__ == "__main__":
    ##------------------DATOS NECESARIOS-----------------------------
    ##esto vendria definido de antemano (variables globales)

    name_image = raw_input("Nombre de imagen GIF: ")

    #Asumiendo que estan en la misma carpeta
    im = Image.open("../../imagenes/"+name_image+".gif")
    print(im.format, im.size, im.mode)

    frames = cantidad_frames(im)+1 #asumiendo que los frames da vuelta 360
    print "La imagen tiene %d frames"%(frames)

    todos_frames = [ImageOps.mirror(f) for f in ImageSequence.Iterator(im)]
    im.close()
    ##------------------DATOS NECESARIOS-----------------------------


    #Movimiento de la imagen a traves de actual
    current = 0 #frame en el momento (actual)
    zoom = 1.0  #zoom en el momento (actual)

    #esto se annade por la memoria del archivo
    caras_memoria = cargar_caras(todos_frames,current,frames)
    centrar_4caras(caras_memoria)

    #antes aca iba while

    #MOSTRAR PRIMERA CARA
    mascara = crear_mascara()
    tamanno_mascara = min(mascara.size)
    redimensionar_zoom(caras_memoria,tamanno_mascara,zoom)
    cara_frente,cara_izquierda,cara_derecha,cara_atras = rotar_imagenes(caras_memoria)
    imagen_Final = posicionar_imagen(mascara,cara_frente,cara_izquierda,cara_derecha,cara_atras)


    data = np.asarray(imagen_Final)


    fig, ax = plt.subplots()
    figura = ax.imshow(data, animated=True)

    #plt.show()
    #hacer(im, frames,figura,current,zoom,memoria=False)
    #app = QtGui.QApplication(sys.argv)
    #plt.ion()
    #plt.close()
    if matplotlib.__version__ == '2.0.2':
        ani = animation.FuncAnimation(fig, funcion_principal, interval=0, blit=True)
    else:
        ani = animation.FuncAnimation(fig,funcion_principal,interval=0) #esta funcion hace el loop
    plt.show()
    #sys.exit(app.exec_())
