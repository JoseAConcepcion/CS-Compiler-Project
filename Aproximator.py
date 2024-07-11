from Definitions import *

#--Main Inits--#
ventx, venty = init_graf(800, 800, ifullscreen=False, iunit=50)
caption = "Graficator"

def mysin(x):
	#Reduce x
	x_reduced = x
	if x < 0:
		while x_reduced > 2*math.pi or x_reduced < 0:
			x_reduced = x_reduced+2*math.pi
	else:
		while x_reduced > 2*math.pi or x_reduced < 0:
			x_reduced = x_reduced-2*math.pi
	
	#Taylor
	result = 0
	i = 0
	coef = 1
	x_to_the_i = 1
	sign_mult = 1
	while i < 8:
		x_taylor = x_to_the_i*x_to_the_i*x_reduced
		
		coef = sign_mult/math.factorial(2*i+1)
		result += coef*x_taylor

		i += 1
		sign_mult *= -1
		x_to_the_i *= x_reduced
	
	return result

def mycos(x):
	#Reduce x
	x_reduced = x
	if x < 0:
		while x_reduced > 2*math.pi or x_reduced < 0:
			x_reduced = x_reduced+2*math.pi
	else:
		while x_reduced > 2*math.pi or x_reduced < 0:
			x_reduced = x_reduced-2*math.pi
	
	#Taylor
	result = 0
	i = 0
	coef = 1
	x_to_the_i = 1
	sign_mult = 1
	while i < 10:
		x_taylor = x_to_the_i*x_to_the_i
		
		coef = sign_mult/math.factorial(2*i)
		result += coef*x_taylor

		i += 1
		sign_mult *= -1
		x_to_the_i *= x_reduced
	
	return result

def myexp(x):
	#Reduce x
	x_reduced = x
	t = 0
	while x_reduced > 1 or x_reduced < -1:
		x_reduced = x_reduced/2
		t += 1

	#Taylor the reduced
	result_taylor = 0
	i = 0
	x_to_the_i = 1
	while i < 10:
		coef = 1/math.factorial(i)
		result_taylor += coef*x_to_the_i
		x_to_the_i = x_to_the_i*x_reduced
		i += 1
	
	#Augment the reduced taylor
	i = 0
	result = result_taylor
	while i < t:
		result *= result
		i += 1

	return result

def mylog(x):
	#Reduce x
	x_reduced = x
	t = 0
	while x_reduced > 1 or x_reduced < -1:
		x_reduced = x_reduced/2
		t += 1

	x_reduced = x_reduced - 1

	#Taylor the reduced
	result_taylor = 0
	i = 0
	x_to_the_ip1 = x_reduced
	sign_mult = 1
	while i < 10:
		result_taylor += sign_mult * x_to_the_ip1/(i+1)
		
		x_to_the_ip1 = x_to_the_ip1*x_reduced
		i += 1
		sign_mult = sign_mult*(-1)
	
	return result_taylor + t*math.log(2)

#--Bucle principal--#
while True:
	#--Código específico--#
	vent.fill((0,0,0))
	draw_grid()


	ss = lambda x: math.log(x)

	draw_function(ss, color=(255,0,0))
	draw_function(mylog,color=(0,255,0))

	#--Events--#
	for event in pygame.event.get():
		basic_controls(event)
	
	#--Display update--#
	clock.tick(0)
	pygame.display.set_caption(caption + f" - {int(clock.get_fps())} fps")
	pygame.display.update()
