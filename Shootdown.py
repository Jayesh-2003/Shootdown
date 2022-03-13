# Constants are written in all capital



import enum
import pygame
from pygame import mixer
import os
import random
import csv

mixer.init()
pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Shootdown")

# Setting a Frame Limit
clock = pygame.time.Clock()
FPS = 60

# defining game variables
GRAVITY = 0.75
SCROLL_THRESH = 200
ROWS = 16
COLS = 150
TILE_SIZE=SCREEN_HEIGHT//ROWS
TILE_TYPES=21
MAX_LEVELS=2
screen_scroll=0
bg_scroll=0
level = 1
start_game= False #Act as a trigger to start game
start_intro=False

# Defining player action Variables
# -- for now all will be false and toggled when needed
moving_left = False
moving_right = False
shoot = False
grenade = False
grenade_thrown = False

#Load music and sounds
pygame.mixer.music.load("audio/music.mp3")
pygame.mixer.music.set_volume(0.3)
pygame.mixer.music.play(-1,0.0,5000)
jump_fx = pygame.mixer.Sound("audio/jump.mp3")
jump_fx.set_volume(0.3)
shot_fx = pygame.mixer.Sound("audio/shot.mp3")
shot_fx.set_volume(2)
grenade_fx = pygame.mixer.Sound("audio/grenade.mp3")
grenade_fx.set_volume(0.6)
jump_fx = pygame.mixer.Sound("audio/jump.mp3")
jump_fx.set_volume(0.6)
start_fx = pygame.mixer.Sound("audio/player.mp3")
start_fx.set_volume(0.8)
death_fx = pygame.mixer.Sound("audio/death.mp3")
death_fx.set_volume(0.8)
portal_fx = pygame.mixer.Sound("audio/portal.mp3")
portal_fx.set_volume(0.8)

# Loading Images
sky_img = pygame.image.load("img/Background/Sky.png").convert_alpha()
BG_img = pygame.image.load("img/Background/BG_Decor.png").convert_alpha()
middle_img = pygame.image.load("img/Background/Middle_Decor.png").convert_alpha()
Foreground_img = pygame.image.load("img/Background/Foreground.png").convert_alpha()
ground_img = pygame.image.load("img/Background/Ground.png").convert_alpha()

#loading images for main menu
main_menu =pygame.image.load("img/main_menu.jpg").convert_alpha()
start_img =pygame.image.load("img/start_btn.png").convert_alpha()
exit_img =pygame.image.load("img/exit_btn.png").convert_alpha()
restart_img =pygame.image.load("img/restart_btn.png").convert_alpha()


#Tiles in list
img_list = []
for x in range(TILE_TYPES):
    img=pygame.image.load(f"img/Tile/{x}.png").convert_alpha()
    img=pygame.transform.scale(img,(TILE_SIZE , TILE_SIZE))
    img_list.append(img)

# bullet
bullet_img = pygame.image.load("img/icons/bullet.png").convert_alpha()
# Grenade
grenade_img = pygame.image.load("img/icons/grenade.png").convert_alpha()
# Pick up boxes
health_box_img = pygame.image.load("img/icons/health_box.png").convert_alpha()
ammo_box_img = pygame.image.load("img/icons/ammo_box.png").convert_alpha()
grenade_box_img = pygame.image.load(
    "img/icons/grenade_box.png").convert_alpha()
item_boxes = {
    "Health": health_box_img,
    "Ammo": ammo_box_img,
    "Grenade": grenade_box_img
}


# Defining Background Colour
BG = (144, 201, 120)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
PINK = (235,65 ,54)
# defining fonts
font = pygame.font.SysFont("Futura", 30)


def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

# Making BG function


def draw_bg():
    screen.fill(BG)
    for x in range(5):
        screen.blit(sky_img,((x*800)-bg_scroll*0.2,0))
        screen.blit(BG_img,((x*800)-bg_scroll*0.4,0))
        screen.blit(middle_img,((x*800)-bg_scroll*0.4,0))
        screen.blit(Foreground_img,((x*800)-bg_scroll*0.6,0))
        screen.blit(ground_img,((x*800)-bg_scroll*0.8,0))

#func to restart
def reset_level():
    grenade_group.empty()
    enemy_group.empty()
    explosion_group.empty()
    bullet_group.empty()
    lava_group.empty()
    item_box_group.empty()
    exit_group.empty()
    decoration_group.empty()

    #For resetting level
    data = []
    for row in range(ROWS):
        r=[-1]*COLS
        data.append(r)
    return data

# Making class for sprites
class Soldier(pygame.sprite.Sprite):

    # Function to initilize the player and enemy
    def __init__(self, char_type, x, y, scale, speed, ammo, grenades):

        # Initilize pygame with this sprite
        pygame.sprite.Sprite.__init__(self)
        # To assign arguments as instance variable
        self.alive = True  # To stop actions when player is dead
        self.char_type = char_type
        self.speed = speed
        self.ammo = ammo
        self.start_ammo = ammo
        self.shoot_cooldown = 0  # to make a cooldown time for player shooting bullet
        self.grenades = grenades
        self.health = 100  # For making Health
        self.max_health = self.health
        self.direction = 1  # setting direction in +ve x-axis initially
        self.vel_y = 0  # Setting velocity in y axis
        self.jump = False
        self.in_air = True  # To avoid double jump
        self.flip = False  # The facing of sprites
        self.animation_list = []
        self.frame_index = 0
        self.action = 0  # To access different animation with different values of action var
        # To track the last time program updated animation
        self.update_time = pygame.time.get_ticks()

        # AI specific Variables
        self.move_counter = 0
        # 3rd attribute is of vision length (how far) Rect created will conduct th vision of enemy
        self.vision = pygame.Rect(0, 0, 150, 20)
        self.idling = False
        self.idling_counter = 0
        # Loading Images for Animation
        animation_types = ["Idle", "Run", "Jump", "Death"]
        for animation in animation_types:
            # Reset temp list of images
            temp_list = []
            # Counting number of images in folder
            num_of_frames = len(os.listdir(f"img/{char_type}/{animation}"))

            for i in range(num_of_frames):  # To load all images in a python list
                # Loading images with loops
                img = pygame.image.load(
                    f"img/{char_type}/{animation}/{i}.png").convert_alpha()
                img = pygame.transform.scale(
                    img, (img.get_width()*scale, img.get_height()*scale))
                # add the image in a temporary list (append)
                temp_list.append(img)
            self.animation_list.append(temp_list)

        # Adding respective images to respective actions
        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width=self.image.get_width()
        self.height=self.image.get_height()

    def update(self):
        self.update_animation()
        self.check_alive()
        # update cooldown
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
    # Function to toggle movement of sprites to Right or Left

    def move(self, moving_left, moving_right):

        # First we have to reset the movement of sprites
        screen_scroll=0
        dx = 0
        dy = 0

        # Assigning movement to moving left or right
        if moving_left:
            dx = -self.speed
            self.flip = True
            self.direction = -1

        if moving_right:
            dx = self.speed
            self.flip = False
            self.direction = 1

        # Assigning Jump var
        if self.jump == True and self.in_air == False:  # To avoid double jump
            self.vel_y = -11  # -ve bec origin is at top left corner
            self.jump = False
            self.in_air = True

        # Apply gravity
        self.vel_y += GRAVITY  # Gravity will decrese velocity in y
        if self.vel_y > 10:
            self.vel_y
        dy += self.vel_y

        #Check for overall collosion
        for tile in world.obstacle_list:
            #check collosion in x direction
            if tile[1].colliderect(self.rect.x + dx, self.rect.y,self.width,self.height):
                dx=0
                #if ai hit wall then turn 
                if self.char_type=="enemy":
                        self.direction *= -1
                        self.move_counter=0

            #check for y collosion
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width,self.height):
                #check if below the ground for jumping
                if self.vel_y<0:
                    self.vel_y=0
                    dy=tile[1].bottom - self.rect.top
                #check for falling
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    self.in_air = False
                    dy=tile[1].top - self.rect.bottom

        #collosion with lava
        if pygame.sprite.spritecollide(self, lava_group, False):
            self.health=0
        
        #collosion with portal
        level_complete=False
        if pygame.sprite.spritecollide(self, exit_group, False):
            portal_fx.play()
            level_complete = True
        
        #check fall of map
        if self.rect.bottom>SCREEN_HEIGHT:
            self.health=0



        #checck if going of the edge 
        if self.char_type=="player":
            if self.rect.left +dx < 0 or self.rect.right+dx > SCREEN_WIDTH:
                dx=0

        # Updating the rect position of sprite
        self.rect.x += dx
        self.rect.y += dy

        #update scroll accc to position
        if self.char_type=="player":
            if (self.rect.right > SCREEN_WIDTH-SCROLL_THRESH and bg_scroll< (world.level_length * TILE_SIZE)-SCREEN_WIDTH) \
                or (self.rect.left< SCROLL_THRESH and bg_scroll > abs(dx)):
                self.rect.x -= dx
                screen_scroll = -dx
        return screen_scroll, level_complete


    # defining shoot for soldier

    def shoot(self):
        # to don't allow player to shoot multiple bullets at same time
        if self.shoot_cooldown == 0 and self.ammo > 0:
            self.shoot_cooldown = 20
            bullet = Bullet(
                self.rect.centerx + (0.72*self.rect.size[0] * self.direction), self.rect.centery, self.direction)
            bullet_group.add(bullet)
            # reduce ammo
            self.ammo -= 1
            shot_fx.play()

    # Defining a AI for enemy
    def ai(self):
        # Checking if player is alive also ai(enemy)
        if self.alive and player.alive:

            # Adding a probablity of being idle
            if self.idling == False and random.randint(1, 150) == 50:
                self.update_action(0)
                self.idling = True
                self.idling_counter = 50  # When counter ends , enemy start run again

        # vision of ai trigger shooting
            if self.vision.colliderect(player.rect):
                # Stop the running action and just face player
                self.update_action(0)  # Idel
                # And Shoot
                self.shoot()
            else:
                if self.idling == False:

                    if self.direction == 1:  # If direction is one its +ve x else -ve
                        ai_moving_right = True
                    else:
                        ai_moving_right = False
                    # Offcorse moving left is not equal to moving right therefor when moving right is true left is false
                    ai_moving_left = not ai_moving_right
                    # use of move function
                    self.move(ai_moving_left, ai_moving_right)
                    self.update_action(1)  # for running
                    self.move_counter += 1
                    # Update vision of AI
                    self.vision.center = (
                        self.rect.centerx + 75 * self.direction, self.rect.centery)

                    if self.move_counter > TILE_SIZE:
                        self.direction *= -1
                        self.move_counter *= -1
                else:
                    self.idling_counter -= 1
                    if self.idling_counter <= 0:  # to start running again
                        self.idling = False
        #scroll ai 
        self.rect.x += screen_scroll
    # function to update animation

    def update_animation(self):
        ANIMATION_COOLDOWN = 100
        # updating image depending on current working image
        self.image = self.animation_list[self.action][self.frame_index]
        # checking if the required time is passed due last update
        # By comparing time
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            # updating time before updating image
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1  # updating the image bu adding plus 1

        # To restart animation soon as it closes or images rendered
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == 3:
                self.frame_index = len(self.animation_list[self.action]) - 1
                self.kill()
                
            else:
                self.frame_index = 0  # this resets animation to start

    def update_action(self, new_action):
        # accessing new action to change animation
        if new_action != self.action:
            self.action = new_action
            # Update animation setting according to time
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    # Just chect if soldire is alive or dead
    def check_alive(self):
        if self.health <= 0:
            self.health = 0
            self.speed = 0
            self.alive = False
            self.update_action(3)
            
            

    # Function to Blit(Draw) Anything on screen

    def draw(self):
        screen.blit(pygame.transform.flip(
            self.image, self.flip, False), self.rect)

#Makeing of the map of game
class World():
    def __init__(self):
        self.obstacle_list = []
    
    def process_data(self,data):
        self.level_length = len(data[0])
        #looping through each avlue in level data file
        for y,row in enumerate(data):
            for x,tile in enumerate(row):
                if tile >=0: #the -1 mean empty space
                    img = img_list[tile]
                    img_rect = img.get_rect()
                    img_rect.x = x* TILE_SIZE
                    img_rect.y = y* TILE_SIZE
                    tile_data=(img,img_rect)
                    if tile >=0 and tile <= 8 :
                        self.obstacle_list.append(tile_data)
                    elif tile>=9 and tile<= 10:
                        lava = Lava(img, x*TILE_SIZE, y*TILE_SIZE)
                        lava_group.add(lava)
                    elif tile>=11 and tile<=14:
                        decoration = Decoration(img, x*TILE_SIZE, y*TILE_SIZE)
                        decoration_group.add(decoration)
                    elif tile == 15 : #Create a player
                        player = Soldier("player", x*TILE_SIZE, y*TILE_SIZE, 1.65, 5, 20, 5)  # Initilizing function
                        # Health Bar of player
                        health_bar = HealthBar(10, 10, player.health, player.health)
                    elif tile==16 : #create enemy
                        enemy = Soldier("enemy",  x*TILE_SIZE, y*TILE_SIZE, 1.65, 2, 20, 0)  # Enemy
                        enemy_group.add(enemy)
                    elif tile == 17 : # Ammo Box
                        item_box = ItemBox("Ammo", x*TILE_SIZE, y*TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 18 : # Grenade Box
                        item_box = ItemBox("Grenade", x*TILE_SIZE, y*TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 17 : # Health Box
                        item_box = ItemBox("Health", x*TILE_SIZE, y*TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile==20 : # Portal
                        exit = Exit(img, x*TILE_SIZE, y*TILE_SIZE)
                        exit_group.add(exit)
        
        return player,health_bar            
    #blitting obstacles
    def draw(self):
        for tile in self.obstacle_list:
            tile[1][0]+=screen_scroll #moving or scrolling map
            screen.blit(tile[0],tile[1])

class Decoration(pygame.sprite.Sprite):
    # initilize the decoration constructor
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x +TILE_SIZE//2,y+(TILE_SIZE-self.image.get_height()))
    def update(self):
        self.rect.x +=screen_scroll
class Lava(pygame.sprite.Sprite):
    # initilize the decoration constructor
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x +TILE_SIZE//2,y+(TILE_SIZE-self.image.get_height()))
    def update(self):
        self.rect.x +=screen_scroll
class Exit(pygame.sprite.Sprite):
    # initilize the decoration constructor
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x +TILE_SIZE//2,y+(TILE_SIZE-self.image.get_height()))
    def update(self):
        self.rect.x +=screen_scroll
# Defining class for collecting items
class ItemBox(pygame.sprite.Sprite):
    # initilize the Collectible items constructor
    def __init__(self, item_type, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.item_type = item_type
        self.image = item_boxes[self.item_type]
        self.rect = self.image.get_rect()
        self.rect.midtop = (x+TILE_SIZE // 2, y +
                            (TILE_SIZE - self.image.get_height()))

    def update(self):
        #scroll
        
        self.rect.x +=screen_scroll
        # checking if player has picked up the box
        if pygame.sprite.collide_rect(self, player):
            # checking which box is picked
            if self.item_type == "Health":
                player.health += 25
                if player.health > player.max_health:
                    player.health = player.max_health
            if self.item_type == "Ammo":
                player.ammo += 12
            if self.item_type == "Grenade":
                player.grenades += 2
            # after picking up delete that object
            self.kill()
# class for health bar


class HealthBar():
    # Creating a constructor
    def __init__(self, x, y, health, max_health):
        self.x = x
        self.y = y
        self.health = health
        self.max_health = max_health

    def draw(self, health):
        # update with new health
        self.health = health
        # calculate new health ratio
        ratio = self.health / self.max_health
        pygame.draw.rect(screen, BLACK, (self.x-2, self.y-2, 154, 24))
        pygame.draw.rect(screen, RED, (self.x, self.y, 150, 20))
        pygame.draw.rect(screen, GREEN, (self.x, self.y, 150*ratio, 20))


# Defining Class for Bullet movements and other stuff
class Bullet(pygame.sprite.Sprite):
    # initilize the bullet constructor
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 10  # here speed is not changing so kept it constant
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction

    def update(self):

        # for moving bullet
        self.rect.x += (self.direction * self.speed) +screen_scroll
        # Vanishing bullet as it collide or go out of screen
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()
        
        #Check for collosion with tiles
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect):
                self.kill()

        if pygame.sprite.spritecollide(player, bullet_group, False):
            if player.alive:
                player.health -= 5
                self.kill()
        for enemy in enemy_group:
            if pygame.sprite.spritecollide(enemy, bullet_group, False):
                if enemy.alive:
                    enemy.health -= 25
                    self.kill()
# Making a class for Granades and Projectiles


class Grenade(pygame.sprite.Sprite):
    # initilize the grenade constructor
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.timer = 100
        self.vel_y = -11  # here its vertical speed
        self.speed = 7  # here its horizontal speed
        self.image = grenade_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width=self.image.get_width()
        self.height=self.image.get_height()
        self.direction = direction

    def update(self):
        # for updating movement of grenade
        self.vel_y += GRAVITY
        dx = self.direction*self.speed
        dy = self.vel_y

        #check for collosion with tile
        for tile in world.obstacle_list:
              # Vanishing bullet as it collide or go out of screen
            if tile[1].colliderect(self.rect.x+dx,self.rect.y,self.width,self.height):
                self.direction *= -1
                dx = self.direction*self.speed
         #check for y collosion
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width,self.height):
                self.speed=0
                #check if below the ground
                if self.vel_y<0:
                    self.vel_y=0
                    dy=tile[1].bottom - self.rect.top
                #check for falling
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    dy=tile[1].top - self.rect.bottom
                    

        # update grenade position
        self.rect.x += dx +screen_scroll
        self.rect.y += dy

        # couting the timer
        self.timer -= 1
        if self.timer <= 0:
            self.kill()
            explosion = Explosion(self.rect.x, self.rect.y, 0.5)
            explosion_group.add(explosion)

            # checking Damage to anyone in radius
            # For player
            if abs(self.rect.centerx - player.rect.centerx) < TILE_SIZE*2 and \
                    abs(self.rect.centerx - player.rect.centerx) < TILE_SIZE*2:
                player.health -= 50
            # For every enemy in enemy Group
            for enemy in enemy_group:
                if abs(self.rect.centerx - enemy.rect.centerx) < TILE_SIZE*2 and \
                        abs(self.rect.centerx - enemy.rect.centerx) < TILE_SIZE*2:
                    enemy.health -= 100

# Class for Explosion


class Explosion(pygame.sprite.Sprite):
    # initilize the explosion constructor
    def __init__(self, x, y, scale):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        for num in range(1, 6):
            img = pygame.image.load(
                f"img/explosion/exp{num}.png").convert_alpha()
            img = pygame.transform.scale(
                img, (int(img.get_width()*scale), int(img.get_height()*scale)))
            self.images.append(img)
        self.frame_index = 0
        self.image = self.images[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.counter = 0
    # Updating the animation

    def update(self):
        #scroll
        self.rect.x += screen_scroll
        
        EXPLOSION_SPEED = 1
        # Update explosion animation
        self.counter += 1
        if self.counter <= EXPLOSION_SPEED:
            self.counter = 0
            self.frame_index += 1
            # If the animation is complete then delete animation
            if self.frame_index >= len(self.images):
                self.kill()
            else:
                self.image = self.images[self.frame_index]
#class for button

class Button():
	def __init__(self,x, y, image, scale):
		width = image.get_width()
		height = image.get_height()
		self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
		self.rect = self.image.get_rect()
		self.rect.topleft = (x, y)
		self.clicked = False #toggle for mouse press

	def draw(self, surface):
		action = False

		#get mouse position
		pos = pygame.mouse.get_pos()

		#check mouseover and clicked conditions
		if self.rect.collidepoint(pos):
			if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
				action = True
				self.clicked = True

		if pygame.mouse.get_pressed()[0] == 0:
			self.clicked = False

		#draw button
		surface.blit(self.image, (self.rect.x, self.rect.y))

		return action
#for a fading effect
class ScreenFade():
    def __init__(self,direction,colour,speed):
        self.direction=direction
        self.colour = colour
        self.speed=speed
        self.fade_counter=0
    
    def fade(self):
        fade_complete=False
        self.fade_counter+=self.speed
        if self.direction==1:
            pygame.draw.rect(screen,self.colour,(0-self.fade_counter,0,SCREEN_WIDTH//2,SCREEN_HEIGHT))
            pygame.draw.rect(screen,self.colour,(SCREEN_WIDTH//2+self.fade_counter,0,SCREEN_WIDTH,SCREEN_HEIGHT))
            pygame.draw.rect(screen,self.colour,(0,0-self.fade_counter,SCREEN_WIDTH,SCREEN_HEIGHT//2))
            pygame.draw.rect(screen,self.colour,(0,SCREEN_HEIGHT//2 + self.fade_counter,SCREEN_WIDTH,SCREEN_HEIGHT))
        if self.direction==2:#vertical fade down
            pygame.draw.rect(screen ,self.colour,(0,0,SCREEN_WIDTH,0+self.fade_counter))
        if self.fade_counter>= SCREEN_WIDTH:
            fade_complete=True
        return fade_complete
#creating fades
intro_fade = ScreenFade(1,BLACK,4)
death_fade = ScreenFade(2,PINK,4)   




#create button  
start_button =Button(SCREEN_WIDTH//2-100,SCREEN_HEIGHT//2-44 , start_img,1)     
exit_button =Button(SCREEN_WIDTH//2+150,SCREEN_HEIGHT//2 -44 , exit_img,1.6)     
restart_button =Button(SCREEN_WIDTH//2+100,SCREEN_HEIGHT//2 -50 , restart_img,1)     

# Grouping the sprites
enemy_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
grenade_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
item_box_group = pygame.sprite.Group()
decoration_group = pygame.sprite.Group()
lava_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()





#creating empty list
world_data = []
for row in range(ROWS):
    r=[-1]*COLS
    world_data.append(r)

#Load level dataand creat world
with open(f"level{level}_data.csv", newline="")as csvfile: #opening file
    reader=csv.reader(csvfile,delimiter=",")
    for x, row in enumerate(reader): #Enumerate to keep an account of coordinates
        for y, tile in enumerate(row):
            world_data[x][y] = int(tile)
world =World()
player,health_bar =world.process_data(world_data)

run = True
while run:

    # Limit the Frame-rate so to make game accessable low end pc too
    clock.tick(FPS)

    if start_game==False:
        #draw menu
        screen.blit(main_menu,(0,0))

        #addding butttons
        if start_button.draw(screen):
            start_game=True
            start_intro=True
            start_fx.play()
        if exit_button.draw(screen):
            run=False
       
    else:
        #update bg of menu
        draw_bg()  # Blitting Background


        #draw mam
        world.draw()
        health_bar.draw(player.health)  # for blitting health bar
        # Displaying Ammo
        draw_text("AMMO: ", font, WHITE, 10, 35)
        for i in range(player.ammo):
            screen.blit(bullet_img, (90 + (i*10), 38))
        # Displaying Grenade
        draw_text("GRENADE :", font, WHITE, 10, 55)
        for i in range(player.grenades):
            screen.blit(grenade_img, (130 + (i*20), 58))
        # Displaying Health
        draw_text(f"{player.health}", font, WHITE, 74, 12)

        player.update()
        player.draw()  # Blitting sprites

        # Adding enemy updation in enemy group
        for enemy in enemy_group:
            enemy.ai()
            enemy.update()
            enemy.draw()  # Blitting sprites

        # Updating and drawing Groups
        bullet_group.update()
        grenade_group.update()
        explosion_group.update()
        item_box_group.update()
        decoration_group.update()
        lava_group.update()
        exit_group.update()
        bullet_group.draw(screen)
        grenade_group.draw(screen)
        explosion_group.draw(screen)
        item_box_group.draw(screen)
        decoration_group.draw(screen)
        lava_group.draw(screen)
        exit_group.draw(screen)

        #show intro
        if start_intro==True:
            if intro_fade.fade():
                start_intro=False
                intro_fade.fade_counter=0
        # update actions of player
        if player.alive:
            # shoot Bullets
            if shoot:
                player.shoot()
            # Throw grenades
            elif grenade and grenade_thrown == False and player.grenades > 0:
                grenade = Grenade(player.rect.centerx + (0.5 * player.rect.size[0] * player.direction),
                                player.rect.top, player.direction)
                grenade_group.add(grenade)
                grenade_thrown = True
                grenade_fx.play()
                # Reducing grenade
                player.grenades -= 1
            if player.in_air:
                player.update_action(2)  # Action 2 is Jump
            elif moving_left or moving_right:
                player.update_action(1)  # Action 1 is running

            else:
                player.update_action(0)  # Action 0 is idle
            screen_scroll,level_complete=player.move(moving_left, moving_right)  # Movement of Sprites
            bg_scroll -= screen_scroll
            
            #checking completing game
            if level_complete:
                start_intro=True
                level +=1
                bg_scroll=0
                world_data=reset_level()
                if level<=MAX_LEVELS:
                    #Load level dataand creat world
                    with open(f"level{level}_data.csv", newline="")as csvfile: #opening file
                        reader=csv.reader(csvfile,delimiter=",")
                        for x, row in enumerate(reader): #Enumerate to keep an account of coordinates
                            for y, tile in enumerate(row):
                                world_data[x][y] = int(tile)
                    world =World()
                    player,health_bar =world.process_data(world_data)
        else:
            
            screen_scroll=0 #relative to player
            #blitting fade
            if death_fade.fade():
            
                if restart_button.draw(screen):
                    death_fade.fade_counter=0
                    start_intro=True
                    bg_scroll=0 # universal background
                    world_data=reset_level()
                    #Load level dataand creat world
                    with open(f"level{level}_data.csv", newline="")as csvfile: #opening file
                        reader=csv.reader(csvfile,delimiter=",")
                        for x, row in enumerate(reader): #Enumerate to keep an account of coordinates
                            for y, tile in enumerate(row):
                                world_data[x][y] = int(tile)
                    world =World()
                    player,health_bar =world.process_data(world_data)
    
    for event in pygame.event.get():
        # For quitting game from x button
        if event.type == pygame.QUIT:
            run = False
        # When Key on Keyboard is pressed the moving toggle changes to True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                moving_left = True
            if event.key == pygame.K_d:
                moving_right = True
            if event.key == pygame.K_LCTRL:
                shoot = True
            if event.key == pygame.K_LALT:
                grenade = True
                grenade_thrown = False  # To not allow player to spam grenade
            if event.key == pygame.K_SPACE and player.alive:
                player.jump = True
            if event.key == pygame.K_w and player.alive:
                player.jump = True
                jump_fx.play()

        # When Key on Keyboard is Released the moving toggle change to False
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                moving_left = False
            if event.key == pygame.K_d:
                moving_right = False
            if event.key == pygame.K_LCTRL:
                shoot = False
            if event.key == pygame.K_LCTRL:
                grenade = False

        # Toggles for mouse for shoot
        LEFT = 1
        RIGHT = 3
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == LEFT:
            shoot = True
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == RIGHT:
            grenade = True                        
        if event.type == pygame.MOUSEBUTTONUP and event.button == LEFT:
            shoot = False
        if event.type == pygame.MOUSEBUTTONUP and event.button == RIGHT:
            grenade = False
            grenade_thrown = False

    pygame.display.update()
pygame.quit()
