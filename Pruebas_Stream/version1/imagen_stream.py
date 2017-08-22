import matplotlib
import matplotlib.pyplot as plt
from matplotlib import animation

import time
from imports_imagenes import * #del codigo imports_imagenes.py


##donde va la cantidad de movimiento (Girar o zoom) ?cliente o server?

#####-------CLIENTE (INDICA QUE ACCION REALIZAR)-----------------------
def funcion_principal(i):

    #opcion = raw_input("Girar: \n1 Derecha \n2 Izquierda \nZoom:\n3 Zoom in \n4 Zoom out\nRotar:\n5 Horario \n6 Antihorario \n7 Centrar\n8 Agregar texto\n")
    opcion = "1"
    start_time = time.time()

    #asignar cantidad de mov
    #asignar un zoom maximo y zoom minimo

    texto_proyectar = ""
    
    if opcion == '1': # movimiento girar derecha
        cantidad = 1

    elif opcion == '2': #movimiento girar izquierda
        cantidad = 1

    elif opcion == '3': #hacer zoom
        cantidad = 0.1

    elif opcion == '4': #quitar zoom
        cantidad = 0.1

    elif opcion== '5': #rotar horario
        cantidad = 15 #grados

    elif opcion == '6': #rotar antihorario
        cantidad = 15 #grados

    elif opcion == '7':
        print "por ver"

    elif opcion == '8':
        texto_proyectar = raw_input("Ingrese texto: ")

    global figura
    hacer(opcion,cantidad,texto_proyectar,figura) ##mucho mas simplificado (todo lo configura el server) texto_proyeccion = "" para vacio

    print "Demoro %f segundos en total"%(time.time() - start_time)

    return figura,

if __name__ == "__main__":
    ##------------------DATOS NECESARIOS-----------------------------
    name_image = raw_input("Nombre de imagen GIF: ")

    fig,figura = inicializar(name_image)

    #plt.show()
    #hacer(im, frames,figura,current,zoom,memoria=False)
    #app = QtGui.QApplication(sys.argv)
    #plt.ion()
    #plt.close()
    if matplotlib.__version__ == '2.0.2':
        ani = animation.FuncAnimation(fig, funcion_principal, interval=10, blit=True)
    else:
        ani = animation.FuncAnimation(fig,funcion_principal,interval=0) #esta funcion hace el loop

    print "llega"
    plt.show()
    #sys.exit(app.exec_())
