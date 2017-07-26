from PIL import Image
import time

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
def frame_a_angulo(frame,frames):
	return int( round( frame* 360.0 / frames))

#name_image = raw_input("Nombre de imagen + extension: ")

#Asumiendo que estan en la misma carpeta
im = Image.open("out.gif")
current = 0
im.seek(current)

print(im.format, im.size, im.mode)

frames = cantidad_frames(im)+1 #asumiendo que los frames da vuelta 360

while(True):
	movimiento = raw_input("1 Derecha \n2 Izquierda \n")

	#asignar cantidad de mov en
	#angulo = bla
	#frame_angulo = (angulo_a_frame(angulo, frames )+indice) % frames
	#print ("para angulo", angulo,"es necesario ir al frame ",frame_angulo)
	#im.seek(frame_angulo-1)

	start_time = time.time()

	if movimiento == '1': #derecha
		current +=1 %frames

	elif movimiento == '2': #izquierda
		current -=1 %frames
		if current <0:
			current += frames

	else:
		print("Movimiento invalido")
		continue

	print("El movimiento deja la imagen en el angulo %f respecto al defecto"%frame_a_angulo(current,frames))
	im.seek(current)
	im.show()
	print "Demoro %f segundos en total"%(time.time() - start_time)