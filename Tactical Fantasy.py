# *****~~~~****~~~***~~**~ MODULE IMPORTS ~**~~***~~~****~~~~*****
import pygame
from pygame.locals import (K_a, K_s, K_d, K_w,
    K_UP, K_DOWN, K_LEFT, K_RIGHT,
    K_RETURN, K_SPACE, K_ESCAPE,
    KEYDOWN, MOUSEBUTTONDOWN, QUIT)
import time
import datetime
import random
import math
import copy

# *****~~~~****~~~***~~**~ COLORS (16-bit, 5-gray)  ~**~~***~~~****~~~~*****
White, Black = (255, 255, 255), (0, 0, 0)
Gray1, Gray2, Gray3 = (180, 180, 180), (125, 125, 125), (70, 70, 70)
Red1, Red2 = (255, 0, 0), (125, 0, 0)
Orange1, Orange2 = (255, 140, 0), (125, 60, 0)
Yellow1, Yellow2 = (255, 255, 0), (130, 120, 0)
Green1, Green2 = (0, 255, 0), (0, 125, 0)
Cyan1, Cyan2 = (0, 255, 255), (0, 125, 125)
Blue1, Blue2 = (50, 50, 255), (0, 0, 140)
Purple1, Purple2 = (240, 0, 240), (125, 0, 125)
Pink1, Pink2 = (255, 125, 200), (130, 60, 100)

# *****~~~~****~~~***~~**~ INITIALIZE PYGAME MODULE ~**~~***~~~****~~~~*****
pygame.init()

# ***---***---***-- DEFINE SCREEN & SYSTEM SETTINGS --***---***---***
screen = pygame.display.set_mode((1920,1080))
#screen_icon = pygame.image.load("LogoDragon.png")
#pygame.display.set_icon(screen_icon)
pygame.display.set_caption("Tactical Fantasy")
screen_x = pygame.display.Info().current_w #1920
screen_y = pygame.display.Info().current_h #1080
clock = pygame.time.Clock() # Stabilizes framerate
FPS = 30
FRAME = 0

# ***---***---***-- DEFINE PRINT FUNCTION --***---***---***
font_size = [0, int(screen_x/60), int(screen_x/40),
    int(screen_x/25), int(screen_x/16), int(screen_x/16)]
def Print(font, text, color, pos_x, pos_y):
    if font not in range(1, 6): font = 2
    font_type = pygame.font.SysFont(None, font_size[font])
    font_text = font_type.render(text, True, color)
    text_x = pygame.font.Font.size(font_type, text)[0]
    text_y = pygame.font.Font.size(font_type, text)[1]
    if pos_x == "center": pos_x = (screen_x - text_x) / 2
    if pos_y == "center": pos_y = (screen_y - text_y) / 2
    screen.blit(font_text, (pos_x, pos_y))

# ***---***---***-- DEFINE BUTTON FUNCTION --***---***---***
# Button: .text(font, text, color, pad_x, pad_y)
# Button: .box(color, color2, width, height, border, border_c)
# Button: .draw(pos_x, pos_y)
class Button():
    def __init__(self):
        pass
    def text(self, font, text, color, pad_x=0, pad_y=0):
        font_type = pygame.font.SysFont(None, font_size[font])
        self.render = font_type.render(text, True, color)
        self.font = font_type
        self.text = text
        self.pad_x = pad_x
        self.pad_y = pad_y
    def box(self, color, color2, width=0, height=0, border=0, border_c=Black):
        if width == 0: width = pygame.font.Font.size(self.font, self.text)[0]
        if height == 0: height = pygame.font.Font.size(self.font, self.text)[1]
        if color2 == "same": color2 = color
        self.width = width
        self.height = height
        self.color = color
        self.color2 = color2
        self.border = border
        self.border_c = border_c
    def draw(self, pos_x, pos_y):
        pos_x2 = pos_x + self.width
        pos_y2 = pos_y + self.height
        if pos_x <= mouse_x <= pos_x2 and pos_y <= mouse_y <= pos_y2:
            self.click = True
            color = self.color2
        else:
            self.click = False
            color = self.color
        if self.pad_x == "center":
            pad_x = pygame.font.Font.size(self.font, self.text)[0]
            pad_x = (self.width - pad_x) / 2
        else: pad_x = self.pad_x
        if self.pad_y == "center":
            pad_y = pygame.font.Font.size(self.font, self.text)[1]
            pad_y = (self.height - pad_y) / 2
        else: pad_y = self.pad_y
        POS = (pos_x, pos_y, self.width, self.height)
        POS_B = (pos_x - self.border, pos_y - self.border,
            self.width + (self.border*2), self.height + (self.border*2))
        POS_T = (pos_x + pad_x, pos_y + pad_y)
        pygame.draw.rect(screen, self.border_c, POS_B)
        pygame.draw.rect(screen, color, POS)
        screen.blit(self.render, POS_T)

# *****~~~~****~~~***~~**~ INITIATE GAME VARIABLES   ~**~~***~~~****~~~~*****
Squad_Size = 3
Enemy_Size = 4
Round = 0
Start_Menu = True
Quit_Menu = False
move_x = move_y = 0
neighbours = [[-1,0], [1,0], [0,-1], [0,1]] # left, right, up, down
all_new = [] # Selector pathfinding nodes
Walls = []
NODE = 48
Node_Spacing = 1
Select_Size = NODE - 2

Grid_Start = [143, 31]
Grid_Size = [20, 20]
Grid_Border = 5
Grid_Width = ((Grid_Size[0]) * (NODE + Node_Spacing)) + (Grid_Border * 2)
Grid_Height = ((Grid_Size[1]) * (NODE + Node_Spacing)) + (Grid_Border * 2)
Grid_End = [Grid_Start[0] + ((Grid_Size[0] - 1) * (NODE + Node_Spacing)),
    Grid_Start[1] + ((Grid_Size[1] - 1) * (NODE + Node_Spacing))]
Map_Size = [Grid_Size[0] * (NODE + Node_Spacing),
    Grid_Size[1] * (NODE + Node_Spacing)]

# *****~~~~****~~~***~~**~ Battle Grid ~**~~***~~~****~~~~*****
# Define the grid and load a map image to fit the grid size
class Battle_Grid():
    def __init__(self, map):
        self.map = pygame.image.load(map).convert()
        self.map = pygame.transform.scale(self.map, (Map_Size[0], Map_Size[1]))
        self.grid = []
        # Create grid coordinates based on height and width, add to grid list
        for x in range (0, Grid_Size[0]):
            for y in range (0, Grid_Size[1]):
                self.grid.append([x, y])
    def draw(self):
        # Generate a background based on the provided height and width
        # = (total size of nodes & space between nodes) + (left & right border)
        pygame.draw.rect(screen, Black, (Grid_Start[0] - Grid_Border,
                                         Grid_Start[1] - Grid_Border,
                                         Grid_Width, Grid_Height))
        for i in range (0, len(self.grid)):
            x = self.grid[i][0]
            y = self.grid[i][1]
            node_x = (x * (NODE + Node_Spacing)) + Grid_Start[0]
            node_y = (y * (NODE + Node_Spacing)) + Grid_Start[1]
            if [x,y] not in Walls:
                pygame.draw.rect(screen, Gray1, (node_x, node_y, NODE, NODE))
        screen.blit(self.map, (Grid_Start[0], Grid_Start[1]))
    def edge(self, pos):
        return pos[0] >= 0 and pos[1] >= 0 and pos[0] < Grid_Width and pos[1] < Grid_Height
        # return pos[0] >= 0 and pos[1] >= 0 and pos[0] < self.width and pos[1] < self.height[1]

# *****~~~~****~~~***~~**~ Grid Pathfinding ~**~~***~~~****~~~~*****
# Define what it means to add the neighbouring cells to the current node
def add_neighbour(a, b):
    return [a[0] + b[0], a[1] + b[1]]

# Define what moves are available for the selected unit and highlight them
class Legal_Moves():
    def __init__(self, cur_pos, move):
        # Create an open list of nodes to check and a closed list of nodes already checked
        open_list = [cur_pos]
        closed_list = []
        # Start the loop to check valid neighbouring nodes so long as there are nodes in the open list
        while len(open_list) != 0:
            # check the first node on the open list and add it to the closed list
            pos_check = open_list.pop(0)
            closed_list.append(pos_check)
            # loop to generate the four neighbouring nodes of the node that is being checked
            for x in range(0, len(neighbours)):
                # generate a new position based on the neighbouring nodes (left, right, up, down)
                new_pos = add_neighbour(pos_check, neighbours[x])
                # measure the distance, in absolutes, from the current position to the new position
                distance = abs(cur_pos[0] - new_pos[0]) + abs(cur_pos[1] - new_pos[1])
                # ensure the distance is within the allowable range
                if distance > move: pass
                # ensure the new position is still within the grid parameters
                elif new_pos not in Map_1.grid: pass
                #elif 0 <= new_pos[0] < Grid_Size[0] and 0 <= new_pos[1] < Grid_Size[1]:
                elif new_pos not in All_Walls: continue
                else:
                    # check that the new position is not classified as a wall
                    #if new_pos not in All_Walls:
                    # check that the new position has not already been populated or been previously checked
                    if new_pos not in all_new and new_pos not in closed_list:
                        all_new.append(new_pos)
                        open_list.append(new_pos)
        self.moves = all_new
        

Map_1 = Battle_Grid("Maps/Map1.png")
All_Walls = pygame.sprite.Group()
'''
def Map_1():
    global All_Walls
    global Map_Grid
    Walls = []
    Map_Grid = Battle_Grid(20, 20)
'''

# *****~~~~****~~~***~~**~ Grid Selector ~**~~***~~~****~~~~*****
All_Selector = pygame.sprite.Group()
class Selector(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface([Select_Size, Select_Size])
        self.image.fill(Cyan1)
        self.image.set_alpha(155)
        self.rect = self.image.get_rect(topleft = (Grid_End[0] + 1, Grid_End[1] + 1))
        All_Selector.add(self)
    def update(self):
        global move_x
        global move_y
        global cur_pos
        if move_x == 1: self.rect.x += (NODE + 1)
        if move_x == -1: self.rect.x -= (NODE + 1)
        if move_y == 1: self.rect.y += (NODE + 1)
        if move_y == -1: self.rect.y -= (NODE + 1)
        if self.rect.left < Grid_Start[0] + 1: self.rect.left = Grid_End[0] + 1
        if self.rect.left > Grid_End[0] + 1: self.rect.left = Grid_Start[0] + 1
        if self.rect.top < Grid_Start[1] + 1: self.rect.top = Grid_End[1] + 1
        if self.rect.top > Grid_End[1] + 1: self.rect.top = Grid_Start[1] + 1
        if pygame.sprite.spritecollideany(self, All_Sprites) != None: self.image.fill(Cyan2)
        elif pygame.sprite.spritecollideany(self, All_Walls) != None: self.image.fill(Gray3)
        else: self.image.fill(Cyan1)
        move_x = move_y = 0
        self.Pos = [
            (Grid_Start[0] + ((2 - 1) * (NODE + Node_Spacing))), #pos_x
            (Grid_Start[1] + ((2 - 1) * (NODE + Node_Spacing)))] #pos_y
    def select(self):
        select_unit = pygame.sprite.spritecollideany(self, All_Sprites)
        if select_unit == None: return
        if select_unit.Side == "Squad": color = Blue2
        elif select_unit.Side == "Enemy": color = Red2
        pygame.draw.rect(screen, Black, (1238, 86, 490, 586))
        pygame.draw.rect(screen, Gray2, (1243, 91, 480, 576))
        pygame.draw.line(screen, Black, (1349, 91), (1349, 197), 5)
        pygame.draw.line(screen, Black, (1243, 195), (1351, 195), 5)
        screen.blit(select_unit.frame, (1247, 95))
        # Spacing based on 48px, starting at 0
        Print(3, select_unit.Name, color, 1359, 95)
        Print(3, "(" + str(select_unit.Level) + ")", Black, 1647, 95)
        Print(2, "Job: " + select_unit.Title, Black, 1359, 159)
        Print(2, "Weapon: " + select_unit.Weapon["Name"], Black, 1247, 239)
        Print(2, "Armor: " + select_unit.Armor["Name"], Black, 1247, 287)
        Print(2, "Move Range: " + str(select_unit.Range), Black, 1247, 335)
        self.moves = Legal_Moves(self.node, select_unit.Range)
        #if select_unit.Side == "Squad": Unit_Menu
        def update():
            for x in range(0, len(all_new)):
                pygame.draw.rect(screen, Green1, (self.moves[x][0]*49+100, self.moves[x][1]*49+100, 46, 46))

Selector = Selector()
Selector_Click = False

Node_Checker = pygame.sprite.Group()

class Node_Check(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        pygame.sprite.Sprite.__init__(self)
        self.area = pygame.Surface([Select_Size, Select_Size])
        self.rect = self.image.get_rect(center = (pos_x, pos_y))
        Node_Checker.add(self)

# *****~~~~****~~~***~~**~ CHARACTER CLASSES   ~**~~***~~~****~~~~*****
All_Sprites = pygame.sprite.Group()
All_Squad = pygame.sprite.Group()
All_Enemy = pygame.sprite.Group()

Martial_Names = ["Aaron", "Adam", "Aiden", "Alan", "Albert", "Alexander",
    "Alfred", "Allen", "Alvin", "Ambrose", "Andrew", "Angus", "Anthony",
    "Arnold", "Arthur", "Ashton", "Austin", "Baldwin", "Barclay", "Barnaby",
    "Barret", "Bart", "Baxter", "Benedict", "Benjamin", "Bernard", "Bertram",
    "Blair", "Blake", "Bradley", "Brandon", "Brian", "Bruce", "Burton",
    "Caleb", "Calvin", "Cameron", "Carl", "Carter", "Cayden", "Cedric",
    "Chadwick", "Charles", "Christopher", "Clark", "Clayton", "Clifford",
    "Clinton", "Cody", "Colin", "Colton", "Conrad", "Cory", "Curtis", "Dale",
    "Dallas", "Dalton", "Damian", "Daniel", "Darcy", "Darian", "Darrell",
    "David", "Dennis", "Denzil", "Derek", "Devin", "Dexter", "Dominic",
    "Donald", "Dorian", "Douglas", "Drogo", "Dunston", "Dwayne", "Dwight",
    "Dylan", "Earl", "Edgar", "Edmund", "Eldric", "Edward", "Elias", "Elliott",
    "Elmer", "Elroy", "Emery", "Emmett", "Eric", "Ethan", "Eugene", "Evan",
    "Everett", "Farley", "Felix", "Fenton", "Finley", "Flint", "Francis",
    "Franklin", "Frederick", "Galen", "Gareth", "Garrett", "Gavin", "Geoffrey",
    "George", "Gerald", "Gideon", "Gordon", "Gregory", "Griffin", "Gunther",
    "Hank", "Harold", "Harvey", "Hayden", "Hector", "Henry", "Herbert",
    "Homer", "Hubert", "Ian", "Isaac", "Ivan", "Jack", "Jacob", "James",
    "Jared", "Jason", "Jeffrey", "Jeremy", "Jerome", "Jesse", "Joel", "John",
    "Jordan", "Joseph", "Justin", "Keith", "Kenneth", "Kevin", "Kirk", "Kurt",
    "Kyle", "Lambert", "Lawrence", "Layton", "Leo", "Leonard", "Leroy," "Levi",
    "Lincoln", "Linus", "Lloyd", "Lorne", "Louis", "Lucas", "Luke", "Malcolm",
    "Marcus", "Mark", "Martin", "Matthew", "Maurice", "Maverick", "Maximilian",
    "Michael", "Myles", "Morgan", "Morris", "Myron", "Napoleon", "Nathan",
    "Neil", "Nicholas", "Nigel", "Norman", "Oliver", "Omar", "Orville",
    "Osborn", "Oscar", "Oswald", "Otto", "Owen", "Patrick", "Paul", "Percival",
    "Peter", "Philip", "Piers", "Quinton", "Ralph", "Randolph", "Raphael",
    "Raymond", "Rayner", "Regan", "Reginald", "Reuben", "Reynard", "Richard",
    "Robert", "Roderick", "Roger", "Roland", "Ronald", "Ross", "Rowan",
    "Rupert", "Russell", "Ryan", "Ryland", "Sampson", "Samuel", "Sean",
    "Sebastian", "Shane", "Sigmund", "Silvester", "Simon", "Skyler", "Stephen",
    "Terence", "Theodore", "Thomas", "Timothy", "Titus", "Tobius", "Todd",
    "Tristen", "Tyrone", "Vernon", "Victor", "Vincent", "Virgil", "Walter",
    "Wayne", "Wesley", "Wilfred", "William", "Zachary"
    ]
Magic_Names = ["Abel", "Achilles", "Adonis", "Agni", "Ajax", "Alvis",
    "Amon", "Arash", "Argus", "Ashur", "Azriel", "Bacchus", "Bala", "Balder",
    "Belenus", "Beowulf", "Bhima", "Boreas", "Bragi", "Brahma", "Bran",
    "Brokkr", "Brontes", "Cadmus", "Cael", "Cassiel", "Castor", "Cepheus",
    "Chanda", "Charon", "Chryses", "Cian", "Conall", "Conor", "Cyrus",
    "Daedalus" "Dagon", "Daire", "Damon", "Darwyn", "Deimos", "Diederik",
    "Dinesha", "Diomedes", "Dionysos", "Dipaka", "Drupada", "Dylan", "Enlil",
    "Eoghan", "Erebus", "Etzel", "Euralus", "Eustace", "Evander", "Faunus",
    "Fenrir", "Fergus", "Fionn", "Freyr", "Fujin", "Grabriel", "Gandalf",
    "Girisha", "Glaucus", "Gopala", "Gotama", "Govad", "Gunnar", "Hadad",
    "Hama", "Heimdall", "Helios", "Herakles", "Hiram", "Hoder", "Horus",
    "Hyperion", "Iapetos", "Icarus", "Indra", "Inti", "Isha", "Jasper",
    "Jayanta", "Jeremiah", "Jimmu", "Jonah", "Joshua", "Jove", "Julian",
    "Kama", "Kane", "Kanti", "Kapali", "Karna", "Kaveh", "Kay", "Khurshid",
    "Krishna", "Kumara", "Laius", "Leander", "Lech", "Leigong", "Liber",
    "Llyr", "Mabon", "Magni", "Mahesha", "Malachi", "Manoja", "Marduk", "Mehr",
    "Melchios", "Menelaus", "Mervyn", "Meztli", "Micah", "Midas", "Minos",
    "Mithra", "Mitra", "Mohana", "Mordred", "Morpheus", "Mukesha", "Murali",
    "Nabu", "Nanda", "Narcissus", "Nechtan", "Neilos", "Nereus", "Nestor",
    "Ninurta", "Nisus", "Njall", "Noah", "Notus", "Nuada", "Numitor",
    "Odysseus", "Oisin", "Orestes", "Orion", "Orvar", "Owain", "Palles",
    "Pangu", "Patroclus", "Peredur", "Perseus", "Perun", "Philander",
    "Phineus", "Phoebus", "Pollux", "Pontus", "Prabhu", "Priam", "Proteus",
    "Pryderi", "Ptah", "Pwyll", "Pyrrhus", "Pythios", "Qruirinus", "Radha",
    "Raguel", "Raijin", "Rajani", "Rama", "Ramiel", "Rangi", "Ravi", "Remus",
    "Rostam", "Rudolph", "Rufus", "Sampo", "Sanjaya", "Sarosh", "Sarpedon",
    "Satisha", "Savitr", "Serapis", "Seth", "Shakti", "Shani", "Shankara",
    "Shyama", "Siegfried", "Sigurd", "Silvius", "Sindri", "Skanda", "Slaine",
    "Sohrab", "Solomon", "Soroush", "Sosruko", "Suijin", "Sundara", "Suresha",
    "Surya", "Sushila", "Svarog", "Sylvan", "Tahmuras", "Tane", "Tapio",
    "Taranis", "Tarhunna", "Thanatos", "Theseus", "Thoth", "Trym", "Turnus",
    "Tychon", "Tyr", "Ukko", "Ulysses", "Urien", "Uther", "Vahagn", "Varuna",
    "Vasanta", "Vena", "Vidar", "Vikrama", "Viraja", "Volos", "Weiland",
    "Woden", "Xanthos", "Xavier", "Yama", "Zephyr"
    ]

All_Squires = pygame.sprite.Group()
Squire_S = {"Image": "Sprites/Squad/Squire.png",
    "Down": ["Sprites/Squad/Squire_Down1.png", "Sprites/Squad/Squire_Down2.png", "Sprites/Squad/Squire_Down3.png"],
    "Left": ["Sprites/Squad/Squire_Left1.png", "Sprites/Squad/Squire_Left2.png", "Sprites/Squad/Squire_Left3.png"],
    "Right": ["Sprites/Squad/Squire_Right1.png", "Sprites/Squad/Squire_Right2.png", "Sprites/Squad/Squire_Right3.png"],
    "Up": ["Sprites/Squad/Squire_Up1.png", "Sprites/Squad/Squire_Up2.png", "Sprites/Squad/Squire_Up3.png"]
    }
Squire_E = {"Image": "Sprites/Enemy/Squire.png",
    "Down": ["Sprites/Enemy/Squire_Down1.png", "Sprites/Enemy/Squire_Down2.png", "Sprites/Enemy/Squire_Down3.png"],
    "Left": ["Sprites/Enemy/Squire_Left1.png", "Sprites/Enemy/Squire_Left2.png", "Sprites/Enemy/Squire_Left3.png"],
    "Right": ["Sprites/Enemy/Squire_Right1.png", "Sprites/Enemy/Squire_Right2.png", "Sprites/Enemy/Squire_Right3.png"],
    "Up": ["Sprites/Enemy/Squire_Up1.png", "Sprites/Enemy/Squire_Up2.png", "Sprites/Enemy/Squire_Up3.png"]
    }
class Squire(pygame.sprite.Sprite):
    def __init__(self, side, pos_x, pos_y):
        pygame.sprite.Sprite.__init__(self)
        self.Name = Martial_Names.pop(random.randrange(0, len(Martial_Names)))
        self.Title = "Squire"
        self.Side = side
        self.HP = random.randrange(17, 21)
        self.MP = random.randrange(3, 5)
        self.SP = random.randrange(7, 9)
        self.Level = 1
        self.Weapon = {"Name": "Sword", "Slash": 4, "Thrust": 2, "Durability": 15}
        self.Armor = {"Name": "Chainmail", "Slash": 7, "Pierce": 3, "Bash": 7, "Durability": 15}
        self.Range = 4
        self.Speed = 14
        self.Pos = [
            (Grid_Start[0] + ((pos_x - 1) * (NODE + Node_Spacing))),
            (Grid_Start[1] + ((pos_y - 1) * (NODE + Node_Spacing)))]
        if side == "Squad":
            self.frame = pygame.image.load(Squire_S["Image"]).convert_alpha()
            self.image = pygame.image.load(Squire_S["Up"][0])
            self.image_up = [
                pygame.image.load(Squire_S["Up"][0]),
                pygame.image.load(Squire_S["Up"][1]),
                pygame.image.load(Squire_S["Up"][2])
                ]
            self.image_down = [
                pygame.image.load(Squire_S["Down"][0]),
                pygame.image.load(Squire_S["Down"][1]),
                pygame.image.load(Squire_S["Down"][2])
                ]
            self.image_left = [
                pygame.image.load(Squire_S["Left"][0]),
                pygame.image.load(Squire_S["Left"][1]),
                pygame.image.load(Squire_S["Left"][2])
                ]
            self.image_right = [
                pygame.image.load(Squire_S["Right"][0]),
                pygame.image.load(Squire_S["Right"][1]),
                pygame.image.load(Squire_S["Right"][2])
                ]
            self.face = "Up"
            All_Squad.add(self)
        elif side == "Enemy":
            self.frame = pygame.image.load(Squire_E["Image"]).convert_alpha()
            self.image = pygame.image.load(Squire_E["Down"][0])
            self.image_up = [
                pygame.image.load(Squire_E["Up"][0]),
                pygame.image.load(Squire_E["Up"][1]),
                pygame.image.load(Squire_E["Up"][2])
                ]
            self.image_down = [
                pygame.image.load(Squire_E["Down"][0]),
                pygame.image.load(Squire_E["Down"][1]),
                pygame.image.load(Squire_E["Down"][2])
                ]
            self.image_left = [
                pygame.image.load(Squire_E["Left"][0]),
                pygame.image.load(Squire_E["Left"][1]),
                pygame.image.load(Squire_E["Left"][2])
                ]
            self.image_right = [
                pygame.image.load(Squire_E["Right"][0]),
                pygame.image.load(Squire_E["Right"][1]),
                pygame.image.load(Squire_E["Right"][2])
                ]
            self.face = "Down"
            All_Enemy.add(self)
        self.rect = self.image.get_rect(topleft = (self.Pos[0], self.Pos[1]))
        All_Squires.add(self)
        All_Sprites.add(self)
    def update(self):
        draw = 0
        if 0 <= FRAME < 7 or 15 <= FRAME < 22:
            draw = 0
        elif 7 <= FRAME < 15:
            draw = 1
        elif 22 <= FRAME < 30:
            draw = 2
        if self.face == "Up": self.image = self.image_up[draw]
        if self.face == "Down": self.image = self.image_down[draw]
        if self.face == "Left": self.image = self.image_left[draw]
        if self.face == "Right": self.image = self.image_right[draw]

Fighter_S = {"Image": "Sprites/Squad/Fighter.png",
    "Down": ["Sprites/Squad/Fighter_Down1.png", "Sprites/Squad/Fighter_Down2.png", "Sprites/Squad/Fighter_Down3.png"],
    "Left": ["Sprites/Squad/Fighter_Left1.png", "Sprites/Squad/Fighter_Left2.png", "Sprites/Squad/Fighter_Left3.png"],
    "Right": ["Sprites/Squad/Fighter_Right1.png", "Sprites/Squad/Fighter_Right2.png", "Sprites/Squad/Fighter_Right3.png"],
    "Up": ["Sprites/Squad/Fighter_Up1.png", "Sprites/Squad/Fighter_Up2.png", "Sprites/Squad/Fighter_Up3.png"]
    }
Fighter_E = {"Image": "Sprites/Enemy/Fighter.png",
    "Down": ["Sprites/Enemy/Fighter_Down1.png", "Sprites/Enemy/Fighter_Down2.png", "Sprites/Enemy/Fighter_Down3.png"],
    "Left": ["Sprites/Enemy/Fighter_Left1.png", "Sprites/Enemy/Fighter_Left2.png", "Sprites/Enemy/Fighter_Left3.png"],
    "Right": ["Sprites/Enemy/Fighter_Right1.png", "Sprites/Enemy/Fighter_Right2.png", "Sprites/Enemy/Fighter_Right3.png"],
    "Up": ["Sprites/Enemy/Fighter_Up1.png", "Sprites/Enemy/Fighter_Up2.png", "Sprites/Enemy/Fighter_Up3.png"]
    }

All_Fighters = pygame.sprite.Group()
class Fighter(pygame.sprite.Sprite):
    def __init__(self, side, pos_x, pos_y):
        pygame.sprite.Sprite.__init__(self)
        self.Name = Martial_Names.pop(random.randrange(0, len(Martial_Names)))
        self.Title = "Fighter"
        self.Side = side
        self.HP = random.randrange(24, 30)
        self.MP = random.randrange(4, 6)
        self.SP = random.randrange(9, 12)
        self.Level = 1
        self.Weapon = {"Name": "Sword", "Slash": 4, "Thrust": 2, "Durability": 15}
        self.Armor = {"Name": "Plate", "Slash": 8, "Pierce": 5, "Bash": 8, "Durability": 20}
        self.Range = 4
        self.Speed = 16
        self.Pos = [
            (Grid_Start[0] + ((pos_x - 1) * (NODE + Node_Spacing))),
            (Grid_Start[1] + ((pos_y - 1) * (NODE + Node_Spacing)))]
        if side == "Squad":
            self.frame = pygame.image.load(Fighter_S["Image"]).convert_alpha()
            self.image = pygame.image.load(Fighter_S["Up"][0])
            self.image_up = [
                pygame.image.load(Fighter_S["Up"][0]),
                pygame.image.load(Fighter_S["Up"][1]),
                pygame.image.load(Fighter_S["Up"][2])
                ]
            self.image_down = [
                pygame.image.load(Fighter_S["Down"][0]),
                pygame.image.load(Fighter_S["Down"][1]),
                pygame.image.load(Fighter_S["Down"][2])
                ]
            self.image_left = [
                pygame.image.load(Fighter_S["Left"][0]),
                pygame.image.load(Fighter_S["Left"][1]),
                pygame.image.load(Fighter_S["Left"][2])
                ]
            self.image_right = [
                pygame.image.load(Fighter_S["Right"][0]),
                pygame.image.load(Fighter_S["Right"][1]),
                pygame.image.load(Fighter_S["Right"][2])
                ]
            self.face = "Up"
            All_Squad.add(self)
        elif side == "Enemy":
            self.frame = pygame.image.load(Fighter_E["Image"]).convert_alpha()
            self.image = pygame.image.load(Fighter_E["Down"][0])
            self.image_up = [
                pygame.image.load(Fighter_E["Up"][0]),
                pygame.image.load(Fighter_E["Up"][1]),
                pygame.image.load(Fighter_E["Up"][2])
                ]
            self.image_down = [
                pygame.image.load(Fighter_E["Down"][0]),
                pygame.image.load(Fighter_E["Down"][1]),
                pygame.image.load(Fighter_E["Down"][2])
                ]
            self.image_left = [
                pygame.image.load(Fighter_E["Left"][0]),
                pygame.image.load(Fighter_E["Left"][1]),
                pygame.image.load(Fighter_E["Left"][2])
                ]
            self.image_right = [
                pygame.image.load(Fighter_E["Right"][0]),
                pygame.image.load(Fighter_E["Right"][1]),
                pygame.image.load(Fighter_E["Right"][2])
                ]
            self.face = "Down"
            All_Enemy.add(self)
        self.rect = self.image.get_rect(topleft = (self.Pos[0], self.Pos[1]))
        All_Fighters.add(self)
        All_Sprites.add(self)
    def update(self):
        draw = 0
        if 0 <= FRAME < 7 or 15 <= FRAME < 22:
            draw = 0
        elif 7 <= FRAME < 15:
            draw = 1
        elif 22 <= FRAME < 30:
            draw = 2
        if self.face == "Up":
            self.image = self.image_up[draw]
        if self.face == "Down":
            self.image = self.image_down[draw]
        if self.face == "Left":
            self.image = self.image_left[draw]
        if self.face == "Right":
            self.image = self.image_right[draw]
        #if self.face == "Fall": self.image = self.image_fall[2]

Squire1 = Squire("Squad", 11, 19)
Squire2 = Squire("Squad", 12, 19)
Squire3 = Squire("Squad", 13, 20)
Squire4 = Squire("Enemy", 7, 1)
Squire5 = Squire("Enemy", 8, 2)
Squire6 = Squire("Enemy", 9, 2)
Fighter1 = Fighter("Squad", 12, 18)
Fighter2 = Fighter("Enemy", 8, 3)

'''
    def path(self):
        legal_moves = []
        current_move = self.Move
        current_node = [(((self.rect.center[0] - 167) / 48) - 48), (((self.rect.center[1] - 10) / 48) - 48)]
        open_node_list = Grid_Nodes
        Grid_Clone = copy.deepcody(Grid_Nodes)
        neighbours = [[-1, 0], [1, 0], [0, -1], [0, 1]]
        def add_point(a, b):
            return [a[0] + b[0], a[1] + b[1]]
        while current_move > 0:
            current_move -= 1
            new_node = add_point(neighbours, current_node)
            new_pos_x, new_pos_y = (((new_node[0] + 48) * 48) + 167), (((new_node[1] + 48) * 48) + 10)
            Node_check = NodeChecker(new_pos_x, new_pos_y)
            if pygame.sprite.spritecollideany(Node_check, All_Sprites) == None: continue
            if pygame.sprite.spritecollideany(Node_check, All_Walls) == None: continue
            if Left_B <= check.rect.centerx <= Right_B: continue
            if Top_B <= check.rect.centery <= Bottom_B: continue
            Node_check.area.fill(Yellow1)
'''

# *****~~~~****~~~***~~**~ START THE MAIN PROGRAM ~**~~***~~~****~~~~*****
running = True
while running:
    screen.fill(Yellow2)
    mouse_x, mouse_y = pygame.mouse.get_pos()
    mouse_click = pygame.mouse.get_pressed()[0]
    #pygame.mouse.set_cursor(*pygame.cursors.diamond)
    clock.tick(FPS)

    # *****~~~~****~~~***~~**~ GAME COMMANDS ~**~~***~~~****~~~~*****
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        # ***---***---***-- KEYBOARD COMMANDS --***---***---***
        if event.type == KEYDOWN:
            if event.key == K_RETURN:
                Selector_Click = True
            elif event.key != K_RETURN:
                Selector_Click = False
            if event.key == K_LEFT:
                move_x = -1
            elif event.key == K_RIGHT:
                move_x = 1
            elif event.key == K_UP:
                move_y = -1
            elif event.key == K_DOWN:
                move_y = 1
            
            # ***---***---***-- START MENU --***---***---***
            # ***---***---***-- QUIT MENU --***---***---***
            # ***---***---***-- MAIN GAME --***---***---***
            if event.key == K_ESCAPE:
                running = False

    # *****~~~~****~~~***~~**~ PRIMARY GAME CODE ~**~~***~~~****~~~~*****
    #Battle_Grid()
    Map_1.draw()
    All_Selector.draw(screen)
    All_Selector.update()
    All_Squires.update()
    All_Fighters.update()
    All_Sprites.draw(screen)
    if Selector_Click == True: 
        Selector.select()
        #Selector.moves()
        Selector.update()
        #Node_Checker.draw(screen)
        

    # ***---***---***-- REFRESH MAIN DISPLAY --***---***---***
    if FRAME < FPS: FRAME += 1
    else: 
        FRAME = 0
    pygame.display.update()

# *****~~~~****~~~***~~**~ END OF MAIN PROGRAM ~**~~***~~~****~~~~*****
pygame.quit()
