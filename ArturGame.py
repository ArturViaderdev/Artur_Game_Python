import random, pygame, sys
import threading

from playsound import playsound
from pygame.locals import *
from multiprocessing import Process

# Declaración de constantes y variables
WHITE = (255, 255, 255)

# Función principal del juego
# Array de sonics que vienen volando haciendo la rueda
sonics=[]
# Array de sonics muertos en la animación de morir
sonicsmuertos=[]
#Array de disparos
disparos=[]

#Define si la partida está activa o se ha acabado
partida = True

#Reproduce el sonido de pasarse el nivel
def fxnivelpasado():
   playsound('nivelpasado.wav', False)

#Reproduce la música de marble zone
def musicasonicmarblednb():
   pygame.mixer.music.load('musicasonicmarblednb.mp3')

   pygame.mixer.music.play(0)

#Reproduce la música del robotnik
def musicarobotnik1():
   pygame.mixer.music.load('robotnikmusic1.mp3')
   pygame.mixer.music.play(0)

#Música del game over
def musicagameover():
   pygame.mixer.music.load('gameover.mp3')
   pygame.mixer.music.play(0)

#Clase que se utiliza para devolver la puntuación, el número de vidas y si se ha pasado un nivel
class Status():
   def __init__(self):
      self.puntuacion = 0
      self.vidas = 5
      self.pasado = False

#Clase disparo, almacena la posición del disparo y el rect
class DisparoA(pygame.sprite.Sprite):
   def __init__(self,x,y):
      pygame.sprite.Sprite.__init__(self)
      self.x = x
      self.y = y
      self.rect = pygame.Rect(self.x, self.y,3,3)
   def updateposition(self):
      self.rect = pygame.Rect(self.x,self.y,3,3)

#Almacena un sonic en animación de morir, su posición y velocidad inicial hacia arriba
class Sonicmuerto(pygame.sprite.Sprite):
   def __init__(self,x,y):
      pygame.sprite.Sprite.__init__(self)
      self.x = x
      self.y = y
      self.velocidad = -10

#Almacena un sonic que viene volando haciendo la rueda
#Su posición, su punto de destino (donde estaba la nave al aparecer)
class Sonic(pygame.sprite.Sprite):
   def __init__(self,destx,desty,nivel):
      pygame.sprite.Sprite.__init__(self)
      #Posición X, la inicial es siempre 370 fuera de la pantalla por la derecha
      self.x = 370
      #Posición y se decide aleatoriamente al crear el sonic
      self.y = random.randrange(1,224)
      #Posición del recorte de la animación del sprite empieza en 0
      self.possonic = 0
      #Coordenada x de destino de la trayectoria
      self.destx = destx
      #Coordenada y de destino de la trayectoria
      self.desty = desty
      #Rectángulo de colisión 50x50
      self.rect = pygame.Rect(self.x,self.y,50,50)
      #En el nivel 2 también existe la componente velocidad que se decide aleatoriamente
      if nivel==2:
         self.velocidady = random.randrange(-10,10)
         self.velocidadx = random.randrange(-5,-1)
   #Actualiza el rectángulo de colisión
   def updateposition(self):
      self.rect = pygame.Rect(self.x,self.y,50,50)

#Almacena un robotnik
class Robotnik(pygame.sprite.Sprite):
   def __init__(self):
      #posición x
      self.x = 500
      #posición y se decide aleatoriamente
      self.y = random.randrange(0,80)
      #velocidad hacia la izquierda
      self.velocidady = 100
      #Rectángulo de colisión de 50 x 50
      self.rect = pygame.Rect(self.x,self.y,50,50)
      #Velocidad horizontal
      self.velocidadx = 0
      #vida del robotnik
      self.vida = 64
   def updateposition(self):
      self.rect = pygame.Rect(self.x,self.y,50,50)

#Almacena el sonic en el nivel de sonic
class Sonicuno(pygame.sprite.Sprite):
   def __init__(self):
      pygame.sprite.Sprite.__init__(self)
      #posición anterior x
      self.xanterior=125
      #posición
      self.x = 125
      self.y = 148
      #velocidad
      self.velocidadx = 0
      self.velocidady = 0
      #si mira hacia la izquierda o hacia la derecha
      self.sentido = False
      #Frame del sonic actual mientras corre 0 si está parado
      self.estado = 0
      #Si el sonic está saltando
      self.saltando = False
      #Frame del salto
      self.estadosaltando = 0
      #Rectángulo de colisión 50x50
      self.rect = pygame.Rect(self.x,self.y,50,50)
   #Actualiza el rectángulo de colisión
   def updateposition(self):
      self.rect = pygame.Rect(self.x,self.y,50,50)
   #Mueve el sonic según la velocidad en un frame
   def mueve(self):
      self.x += self.velocidadx
   #Cambia el sentido del sonic
   def cambiasentido(self,sentido):
      self.sentido = sentido
   #Cambia el estado o frame al caminar
   def cambiaestado(self):
      if self.estado==6:
         self.estado = 1
      else:
         self.estado += 1
   #Cambia el estado al saltar o frames
   def cambiaestadosaltando(self):
      if self.estadosaltando == 4:
         self.estadosaltando = 0
      else:
         self.estadosaltando += 1
   #Pone el sonic parado
   def ponparado(self):
      self.estado = 0

#Clase que almacena la nave
class Nave(pygame.sprite.Sprite):
   def __init__(self):
      pygame.sprite.Sprite.__init__(self)
      self.x = 10
      self.y = 10
      self.posnave = 44
      self.rect = pygame.Rect(self.x,self.y,5,5)
   def updateposition(self):
      self.rect = pygame.Rect(self.x,self.y,5,5)

#Borra un sonic
def borrasonic(pos):
   sonics.pop(pos)
#Borra un sonic muerto al caer debajo
def borrasonicmuerto(pos):
   sonicsmuertos.pop(pos)
#Borra un disparo
def borradisparo(pos):
   disparos.pop(pos)
#Crea un sonic enemigo nuevo
def creasonic(personaje_x, personaje_y, nivel):
   sonics.append(Sonic(personaje_x,personaje_y, nivel))
#Crea un disparo
def creadisparo(x,y):
   disparos.append(DisparoA(x,y))
#Fin de la partida
def gameover(screen):
   clock = pygame.time.Clock()
   continua = False
   imagengameover = pygame.image.load('gameover.png').convert()
   musicagameover()
   cont=0
   while not continua:
      clock.tick(60)
      if cont<100:
         cont+=1
      screen.blit(imagengameover, (0, 0))

      for event in pygame.event.get():

         if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit(0)
         if event.type == pygame.KEYDOWN:
            if cont==100:
               if event.key == pygame.K_SPACE:
                  continua = True
               elif event.key == pygame.K_q:
                  pygame.quit()
                  sys.exit(0)
      pygame.display.update()

#Muestra que el nivel está pasado
def muestrapasado(screen):
   clock = pygame.time.Clock()
   black = 0, 0, 0
   cont = 0
   screen.fill(black)
   font = pygame.font.Font(pygame.font.get_default_font(), 12)
   continua = False

   while not continua:
      clock.tick(60)
      textsurface = font.render('Congratulations Game Completed ', False, (255, 255, 255))
      screen.blit(textsurface,(70,70))
      textsurface = font.render('Developed by: Artur Viader Mataix ', False, (255, 255, 255))
      screen.blit(textsurface,(70,140))
      
      if cont<100:
         cont+=1
      for event in pygame.event.get():

         if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit(0)
         if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
               if cont==100:
                  continua = True
            if event.key == pygame.K_q:
               pygame.quit()
               sys.exit(0)
      pygame.display.update()

#Nivel de sonic
def fasesonic(screen,nivel,status):
   partida = True
   sonicimagen = pygame.image.load("sonic.gif").convert()
   sonicimageni = pygame.transform.flip(sonicimagen,True,False)
   robotniki = pygame.image.load("robotnik.gif").convert()
   imagenitems = pygame.image.load("items.gif").convert()
   pressed_up = False
   pressed_down = False
   pressed_left = False
   pressed_right = False
   clock = pygame.time.Clock()
   fondo = pygame.image.load('fondo2.png').convert()
   posfondox = 2
   pygame.font.init()
   font = pygame.font.Font(pygame.font.get_default_font(), 10)
   robotniks=[]
   personaje = Sonicuno()
   contavariavelocidad = 0
   contapierdevelocidad = 0
   contcambiaestado = 0
   empiezarobotniks = False
   robotnikshechos = False
   frecuenciarobotniks = 100
   controbotniks = 10
   controbotniks = 0
   posbandera = 8000
   girandobandera = False
   recortebandera = 275
   contabandera = 1
   puntuacion = status.puntuacion
   vidas = status.vidas

   contaralentizabandera = 0
   personaje.updateposition()
   fxrobotnikimpacto = pygame.mixer.Sound('S1_AC.wav')
   fxsonicsalto = pygame.mixer.Sound("S1_A0.wav")
   while partida:
      clock.tick(60)

      screen.blit(fondo, (posfondox, -4))
      if(posbandera<=320 or posbandera >=0):
         if girandobandera:
            if contaralentizabandera == 4:
               contaralentizabandera = 0
               recortebandera += 50 * contabandera
               contabandera+=1
               if contabandera == 16:
                  partida = False
            else:
               contaralentizabandera += 1
         screen.blit(imagenitems, (posbandera, 148), (recortebandera, 29, 50, 50))

      if posbandera <= 160:
         girandobandera = True


      contarobotniks = 0
      while contarobotniks<len(robotniks):
         robotniks[contarobotniks].x += -5 + personaje.velocidadx


         screen.blit(robotniki, (robotniks[contarobotniks].x, robotniks[contarobotniks].y), (0, 0, 60, 60))


         robotniks[contarobotniks].updateposition()

         if pygame.sprite.collide_rect(personaje,robotniks[contarobotniks]):
            robotniks.remove(robotniks[contarobotniks])
            puntuacion += 100
            fxrobotnikimpacto.play()
         else:
            contarobotniks+= 1
      if controbotniks == frecuenciarobotniks:
         robotniks.append(Robotnik())
         frecuenciarobotniks -= 1
         controbotniks = 0
         if frecuenciarobotniks == 0:
            empiezarobotniks = False
            robotnikshechos = True
      else:
         controbotniks += 1
      if personaje.y <148:
         personaje.velocidady += 1
      else:
         personaje.velocidady = 0
         personaje.saltando = False

      if personaje.velocidadx > 0:
         contcambiaestado += 1
         if contcambiaestado >= 11 - (personaje.velocidadx):
            contcambiaestado =0
            personaje.cambiaestado()
         personaje.cambiasentido(False)
      elif personaje.velocidadx<0:
         contcambiaestado += 1
         if contcambiaestado >= 11 - (personaje.velocidadx * -1):
            contcambiaestado =0
            personaje.cambiaestado()
         personaje.cambiasentido(True)
      else:
         personaje.ponparado()

      if personaje.saltando:
         personaje.updateposition()
         screen.blit(sonicimagen, (personaje.x, personaje.y), (personaje.estadosaltando * 48, 144, 50, 50))

         personaje.cambiaestadosaltando()
      else:
         if personaje.sentido:
            if personaje.estado == 0:
               screen.blit(sonicimagen, (personaje.x, personaje.y), (284, 0, 50, 50))
            else:
               screen.blit(sonicimagen, (personaje.x, personaje.y), (48*personaje.estado, 0, 50, 50))
         else:
            if personaje.estado == 0:
               screen.blit(sonicimageni,(personaje.x, personaje.y), (188,0,50,50))
            else:
               screen.blit(sonicimageni, (personaje.x, personaje.y), (48*11 - 48*personaje.estado, 0, 50, 50))

      textsurface = font.render('Score ' + str(puntuacion), False, (0, 0, 255))
      screen.blit(textsurface,(0,0))
      textsurface = font.render('VIDAS ' + str(vidas), False, (0, 255, 255))
      screen.blit(textsurface,(275   ,200))

      for event in pygame.event.get():
         if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit(0)

         if event.type == pygame.KEYDOWN:  # check for key presses
            if event.key == pygame.K_LEFT:  # left arrow turns left
               pressed_left = True
               posanterior = personaje.x
            elif event.key == pygame.K_RIGHT:  # right arrow turns right
               pressed_right = True
               posanterior = personaje.x
            elif event.key == pygame.K_UP:  # up arrow goes up
               pressed_up = True
            elif event.key == pygame.K_DOWN:  # down arrow goes down
               pressed_down = True
            elif event.key == pygame.K_SPACE:
               if not personaje.saltando:
                  fxsonicsalto.play()
                  personaje.saltando = True
                  personaje.velocidady = -15
                  personaje.possaltando = 0
            elif event.key == pygame.K_q:
               pygame.quit()
               sys.exit(0)
         elif event.type == pygame.KEYUP:  # check for key releases
            if event.key == pygame.K_LEFT:  # left arrow turns left
               contavariavelocidad = 0
               contapierdevelocidad = 0
               pressed_left = False
            elif event.key == pygame.K_RIGHT:  # right arrow turns right
               contavariavelocidad = 0
               contapierdevelocidad = 0
               pressed_right = False
            elif event.key == pygame.K_UP:  # up arrow goes up
               pressed_up = False
            elif event.key == pygame.K_DOWN:  # down arrow goes down
               pressed_down = False
      #if pressed_up == True:

      #if pressed_down == True:
      if contavariavelocidad == 0:
         if pressed_right == True:
            if posbandera <0:
               personaje.ponparado()
               personaje.velocidadx = 0
            else:
               if personaje.velocidadx>=-12:
                  personaje.velocidadx -= 1
                  contavariavelocidad = 4
         if pressed_left == True:

            if posbandera >= 8200:
               personaje.ponparado()
               personaje.velocidadx = 0
            else:
               if personaje.velocidadx<=12:
                  personaje.velocidadx += 1
                  contavariavelocidad = 4
      else:
         contavariavelocidad -= 1

      if contapierdevelocidad == 0:
         if pressed_left == False and pressed_right == False:
            if personaje.velocidadx>0:
               personaje.velocidadx -=1
            elif personaje.velocidadx<0:
               personaje.velocidadx +=1
            contapierdevelocidad = 5
      else:
         contapierdevelocidad -= 1
      posbandera += personaje.velocidadx
      posfondox += personaje.velocidadx
      personaje.y += personaje.velocidady

      if posfondox<-3073:
         if not robotnikshechos:
            empiezarobotniks = True
         posfondox=0
      elif posfondox>0:
         if not robotnikshechos:
            empiezarobotniks = True
         posfondox=-3073;
      #personaje.mueve()
      personaje.xanterior = personaje.x

      personaje.updateposition()

      pygame.display.update()
   status.puntuacion = puntuacion
   status.pasado = True
   return status

#Nivel normal
def fase(screen,nivel,status):
   partida = True
   sonics.clear()
   sonicsmuertos.clear()
   disparos.clear()
   naveimagen = pygame.image.load("nave.png").convert()
   sonicimagen = pygame.image.load("sonic.gif").convert()
   robotniki = pygame.image.load("robotnik.gif").convert()
   robotnik = Robotnik()
   #Cambia el fondo según el nivel
   if nivel==1:
      fondo = pygame.image.load('fondo.jpeg').convert()
   elif nivel ==2:
      fondo = pygame.image.load('fondo2.png').convert()
   elif nivel == 4:
      fondo = pygame.image.load('fondov.jpg').convert()
   frecsonics = 35

   contsonics=0
   vidas = status.vidas
   puntuacion = status.puntuacion
   clock = pygame.time.Clock()
   pygame.font.init()
   font = pygame.font.Font(pygame.font.get_default_font(), 10)
   izquierdapulsado=0
   derechapulsado=0
   arribapulsado=0
   abajopulsado=0
   nave = Nave()

   # Bucle principal
   cont=0
   contasonic=0
   contcreasonic=0
   contmostrando = 0
   mostrandonave = False
   pressed_up = False
   pressed_down = False
   pressed_left = False
   pressed_right = False
   parpadeando = False
   contparpadeo = 0
   #música según el nivel
   if nivel == 1:
      musicasonicmarblednb()
   elif nivel == 4:
      musicarobotnik1()
   contcolisiones = 0
   maxcolisiones = 0
   pasado = False
   #Carga sonidos fx en memoria
   disparoa = pygame.mixer.Sound('disparoa.wav');
   sonicmuere = pygame.mixer.Sound('sonicmuere.wav');
   fxpierdevida = pygame.mixer.Sound('S1_A6.wav');
   fxmuere = pygame.mixer.Sound('S1_B9.wav')
   fxrobotnikimpacto = pygame.mixer.Sound('S1_AC.wav')
   maxfondo = 0
   if nivel == 1 or nivel == 2:
      maxfondo = -3320

   while partida:
      clock.tick(60)
      # 1.- Se dibuja la pantalla
      #screen.fill(WHITE)

      if nivel==1:
         screen.blit(fondo, (cont, 0))
      elif nivel ==2:
         screen.blit(fondo, (cont, -5))
      elif nivel ==4:
         screen.blit(fondo, (-nave.x * 1.2, -nave.y*1.2))


         screen.blit(robotniki, (robotnik.x, robotnik.y),(0,0,60,60))
         robotnik.velocidadx = (nave.x- robotnik.x) / 200
         robotnik.velocidady = (nave.y - robotnik.y) /200
         robotnik.x += robotnik.velocidadx
         robotnik.y += robotnik.velocidady

         robotnik.updateposition()
         if parpadeando == False:
            if pygame.sprite.collide_rect(robotnik,nave):
               vidas -= 1
               if vidas == 0:
                  fxmuere.play()
               else:
                  fxpierdevida.play()
               parpadeando = True
               contparpadeo = 90
               if vidas == 0:
                  partida = False

      if parpadeando:
         if contparpadeo == 0:
            parpadeando = False
         else:
            contparpadeo -= 1
            if mostrandonave:
               screen.blit(naveimagen, (nave.x, nave.y),(0,nave.posnave,35,22))
            if contmostrando == 4:
               contmostrando = 0
               if mostrandonave:
                  mostrandonave = False
               else:
                  mostrandonave = True
            else:
               contmostrando += 1
      else:
         screen.blit(naveimagen, (nave.x, nave.y),(0,nave.posnave,35,22))

      contsonics=0
      while contsonics<len(sonics):

         if sonics[contsonics].x < -50:
            borrasonic(contsonics)
         else:
            if nivel == 1:
               sonics[contsonics].x -=2
               if contasonic == 2:
                  if sonics[contsonics].y > nave.y:
                     sonics[contsonics].y -=1
                  elif sonics[contsonics].y < nave.y:
                     sonics[contsonics].y +=1

            elif nivel == 2:
               sonics[contsonics].y += sonics[contsonics].velocidady
               if sonics[contsonics].y<0 or sonics[contsonics].y>224:
                  sonics[contsonics].velocidady = sonics[contsonics].velocidady * -1
                  if sonics[contsonics].velocidady > 0:
                     sonics[contsonics].velocidady += 1
                  else:
                     sonics[contsonics].velocidady -= 1
               sonics[contsonics].x += sonics[contsonics].velocidadx
            posactual = sonics[contsonics].possonic
            if contasonic == 2:
               if posactual < int(148):
                  sonics[contsonics].possonic = sonics[contsonics].possonic + 50
               else:
                  sonics[contsonics].possonic = 0

            sonics[contsonics].updateposition()

            if parpadeando == False:
               if pygame.sprite.collide_rect(sonics[contsonics],nave):

                  vidas -= 1
                  if vidas == 0:
                     fxmuere.play()
                  else:
                     fxpierdevida.play()
                  parpadeando = True
                  contparpadeo = 90
                  if vidas == 0:
                     partida = False
            sal = False
            encontrado = False
            contdisparos = 0
            while sal==False:
                  if contdisparos<len(disparos):
                     if pygame.sprite.collide_rect(sonics[contsonics],disparos[contdisparos]):
                        puntuacion += 10

                        if contcolisiones == maxcolisiones:
                           if contcreasonic == frecsonics:
                              contcreasonic -=1
                           frecsonics -= 1
                           if frecsonics == 1:
                              maxcolisiones = 10
                           elif frecsonics == 20:
                              maxcolisiones = 1
                           if frecsonics == 0:
                              frecsonics -= 1
                           contcolisiones = 0
                        else:
                           contcolisiones += 1
                        borradisparo(contdisparos)
                        sonicsmuertos.append(Sonicmuerto(sonics[contsonics].x,sonics[contsonics].y))
                        borrasonic(contsonics)
                        #fxsonicmuere()
                        sonicmuere.play()
                        encontrado = True
                        sal = True
                     else:
                        contdisparos += 1
                  else:
                     sal = True
            if(encontrado == False):
               screen.blit(sonicimagen, (sonics[contsonics].x, sonics[contsonics].y), (sonics[contsonics].possonic, 145, 50, 50))
               contsonics +=1
      contdisparos = 0
      while contdisparos<len(disparos):
         if(disparos[contdisparos].x < 320):
            disparos[contdisparos].x += 3
            disparos[contdisparos].updateposition()
            screen.blit(naveimagen, (disparos[contdisparos].x, disparos[contdisparos].y), (189, 184, 16, 16))
            if pygame.sprite.collide_rect(robotnik,disparos[contdisparos]):
               fxrobotnikimpacto.play()
               screen.blit(robotniki, (robotnik.x, robotnik.y),(0,185,60,60))
               puntuacion += 100
               robotnik.vida -=1
               borradisparo(contdisparos)
               if robotnik.vida == 0:
                  partida = False
                  pasado = True
         
            contdisparos +=1
         else:
            borradisparo(contdisparos)
      contsonicsmuertos = 0
      while contsonicsmuertos<len(sonicsmuertos):
         if sonicsmuertos[contsonicsmuertos].y>224:
            borrasonicmuerto(contsonicsmuertos)
         else:
            sonicsmuertos[contsonicsmuertos].y += sonicsmuertos[contsonicsmuertos].velocidad
            sonicsmuertos[contsonicsmuertos].velocidad += 1
            screen.blit(sonicimagen, (sonicsmuertos[contsonicsmuertos].x, sonicsmuertos[contsonicsmuertos].y), (240, 145, 50, 50))
            contsonicsmuertos += 1




      if cont<maxfondo:
         cont=0
      else:
         if nivel == 1:
            cont -=1
         elif nivel ==2:
            cont -=3
         elif nivel == 4:
            cont -=2
      if nivel ==1:

         textsurface = font.render('Score ' + str(puntuacion), False, (255, 255, 255))
         screen.blit(textsurface,(0,0))
         textsurface = font.render('VIDAS ' + str(vidas), False, (255, 255, 255))
         screen.blit(textsurface,(275   ,200))
      elif nivel == 2:
         textsurface = font.render('Score ' + str(puntuacion), False, (0, 0, 255))
         screen.blit(textsurface,(0,0))
         textsurface = font.render('VIDAS ' + str(vidas), False, (0, 255, 255))
         screen.blit(textsurface,(275   ,200))
      elif nivel == 4:
         textsurface = font.render('Score ' + str(puntuacion), False, (0, 0, 0))
         screen.blit(textsurface,(0,0))
         textsurface = font.render('VIDAS ' + str(vidas), False, (0, 0, 0))
         screen.blit(textsurface,(275   ,200))
   # 2.- Se comprueban los eventos

      for event in pygame.event.get():

         if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit(0)

         if event.type == pygame.KEYDOWN:  # check for key presses
            if event.key == pygame.K_LEFT:  # left arrow turns left
               pressed_left = True
            elif event.key == pygame.K_RIGHT:  # right arrow turns right
               pressed_right = True
            elif event.key == pygame.K_UP:  # up arrow goes up
               pressed_up = True
            elif event.key == pygame.K_DOWN:  # down arrow goes down
               pressed_down = True
            elif event.key == pygame.K_SPACE:
               creadisparo(nave.x + 30, nave.y+5)
               disparoa.play()
            elif event.key == pygame.K_q:
               pygame.quit()
               sys.exit(0)
         elif event.type == pygame.KEYUP:  # check for key releases
            if event.key == pygame.K_LEFT:  # left arrow turns left
               pressed_left = False
            elif event.key == pygame.K_RIGHT:  # right arrow turns right
               pressed_right = False
            elif event.key == pygame.K_UP:  # up arrow goes up
               pressed_up = False
            elif event.key == pygame.K_DOWN:  # down arrow goes down
               pressed_down = False


      if pressed_up == True:
         if nave.y > 0:
            nave.y -=1
            nave.updateposition()
         nave.posnave = 22

      if pressed_down == True:

         if nave.y<202:
            nave.y +=1
            nave.updateposition()
         nave.posnave = 0
      if pressed_left == True:
         if nave.x>0:
            nave.x -= 1
            nave.updateposition()
      if pressed_right == True:
         if nave.x<285:
            nave.x +=1
            nave.updateposition()
      if pressed_up == False and pressed_down == False:
         nave.posnave = 44

      if contcreasonic == frecsonics:
         creasonic(nave.x, nave.y, nivel)
         contcreasonic =0
      else:
         if contcreasonic > 500:
            partida = False
            pasado = True
            fxnivelpasado()
         contcreasonic +=1
      if contasonic == 2:
         contasonic = 0
      else:
         contasonic +=1


      # 3.- Se actualiza la pantalla
      pygame.display.update()
   status.vidas = vidas
   status.puntuacion = puntuacion
   status.pasado = pasado
   return status
def muestranivel(screen,nivel):
   clock = pygame.time.Clock()
   black = 0, 0, 0
   cont = 0
   screen.fill(black)
   font = pygame.font.Font(pygame.font.get_default_font(), 24)

   while cont<120:
      clock.tick(60)
      textsurface = font.render('Level ' + str(nivel), False, (255, 255, 255))
      screen.blit(textsurface,(70,70))
      pygame.display.update()
      cont += 1

def main():
   # Se inicializa el juego

   pygame.init()
   pygame.display.set_caption("Título del juego")
   nivel = 1
   flags = FULLSCREEN | DOUBLEBUF
   #flags = DOUBLEBUF
   screen = pygame.display.set_mode((320,224),flags,8)
   screen.set_alpha(None)
   status = Status()
   #intro(screen)
   while True:
      muestranivel(screen,nivel)
      if nivel!=3:
         status = fase(screen, nivel, status)
      else:
         status = fasesonic(screen, nivel, status)
      if status.pasado:
         nivel += 1
         if nivel > 4:
            muestrapasado(screen)
            status.vidas = 5
            status.puntuacion = 0
            nivel = 1
      else:
         gameover(screen)
         status.vidas = 5
         status.puntuacion = 0
         nivel = 1


# Este fichero es el que ejecuta el juego principal
if __name__ == '__main__':
   main()



