import time
from PIL import Image, ImageFile, ImageChops,ImageOps

from imports_imagenes import * #del codigo imports_imagenes.py

##------------------DATOS NECESARIOS-----------------------------
##esto vendria definido de antemano (variables globales)

#4 imagenes en 4 angulos
angulos = [0.0, 90.0, 180.0, 270.0]

name_image = raw_input("Nombre de imagen GIF: ")

#Asumiendo que estan en la misma carpeta
im = Image.open("./imagenes/"+name_image+".gif")
print(im.format, im.size, im.mode)

frames = cantidad_frames(im)+1 #asumiendo que los frames da vuelta 360
print "La imagen tiene %d frames"%(frames)
##------------------DATOS NECESARIOS-----------------------------



##donde va la cantidad de movimiento (Girar o zoom) ?cliente o server?

#####-------CLIENTE (INDICA QUE ACCION REALIZAR)-----------------------
if __name__ == "__main__":

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

	    #>>>>>>> REALIZAR ACCION >>>>>>>
	    #imagen, frames y angulos vienen de server?
	    hacer(im, frames, angulos,current,zoom) ##funcion dentro de imports_imagenes
	    
	    print "Demoro %f segundos en total"%(time.time() - start_time)