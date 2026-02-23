import pygame as pg
import random
import time

#Colors
black = (0, 0, 0); black2 = (45, 45, 45); black3 = (40, 45, 0)
brown = (100, 85, 50); brown2 = (150, 95, 50)
green1 = (110, 165, 30); green2 = (85, 135, 25); green3 = (55, 105, 25)
gold1 = (233, 135, 45); gold2 = (231, 181, 61); gold3 = (201, 101, 31)
white = (255, 255, 255); red = (255, 0, 0); blue = (55, 95, 210); darkblue = (55, 75, 190)
mapcoral = (255, 80, 90); store2 = (180, 80, 65); store1 = (160, 110, 65)

#Variables
pg.mixer.pre_init(44100, -16, 2, 512)
pg.init()
title_font = pg.font.Font('Assets/Font/PressStart2P-Regular.ttf', 28); coords_font = pg.font.Font('freesansbold.ttf', 10)
general_font = pg.font.Font('Assets/Font/PressStart2P-Regular.ttf', 14); instruction_font = pg.font.Font('Assets/Font/PressStart2P-Regular.ttf', 14)
x_resolution = 800; x = 8; meta_x = 0
y_resolution = 600; y = 6; meta_y = 0
scale = int(x_resolution/16)
inventory = {'Gold':0, 'Fishing Pole':0, 'Fish':0, 'Seaweed':0, 'Coral':0, 'Potion':'Inactive'}
showstore = None
state = {'hasatlas': False}
menumode = False
land_tally = 0
quest = 0
landwalk = False

#Adjustables
nLand = 750 #Out of 1,000 (lower bound) default 750
nShore = 900 #Out of 1,000 (lower bound) default 900
nShadow = 902 #out of 10,000 (lower bound) default 902
nCoin = 9970 #Out of 10,000 (upper bound) default 9970
nFish = 9350 #Out of 10,000 (range bound) default 9350
nSeaweed = 9100 # Out of 10,000 (range bound) default 9100
nCoral = 910 #Out of 10,000 (lower bound) default 910
nStore = 897 #Out of 900 (upper bound) default 897
nTree = 1 #Out of 750 (lower bound) default 1
nHole = 748 #Out of 750 (upper bound) default 748

#Other Variables
pg.display.init()
_info = pg.display.Info()
Screen = pg.display.set_mode((_info.current_w, _info.current_h), pg.NOFRAME)
pg.display.set_caption('Treasure Hunt Simulator')
screen_w, screen_h = Screen.get_size()
display_offset = ((screen_w - x_resolution) // 2, (screen_h - y_resolution) // 2)
Display = pg.Surface((x_resolution, y_resolution))
start_time = time.time()
finish_time = None
controls = [
    'Arrow Keys: Move',
    '',
    'Spacebar: Interact',
    '',
    'Return: View Inventory',
    '',
    'A: View Atlas',
    '',
    '',
    '',
    'Esc : Quit',
]

#User Defined Functions
def DrawRect(color, origin_list, border):
    pg.draw.rect(Display, color, origin_list, border)
    
def DrawCirc(color, origin, radius):
    pg.draw.circle(Display, color, origin, radius)
    
def Draw_Cursor(coords, scale):
    DrawRect(red, [coords[0]*scale, coords[1]*scale, scale - scale/50, scale - scale/50], 2)
    
def DrawCoin(tile):
    DrawCirc(gold3, (tile.x*scale + (scale/2+1), tile.y*scale + (scale/2+1)), 7); DrawCirc(gold2, (tile.x*scale + (scale/2), tile.y*scale + (scale/2)), 7)
    pg.draw.line(Display, gold1, (tile.x*scale + scale/2 + 4, tile.y*scale + scale/2 - 4), (tile.x*scale + scale/2 - 2, tile.y*scale + scale/2 - 2)); pg.draw.line(Display, gold1, (tile.x*scale + scale/2 + 2, tile.y*scale + scale/2 + 1.5), (tile.x*scale + scale/2 - 4, tile.y*scale + scale/2 + 4))

def DrawTree(tile):
    DrawCirc(green3, (tile.x*scale + (scale/2), tile.y*scale + (scale/2)), 12); DrawCirc(green2, (tile.x*scale + (scale/2), tile.y*scale + (scale/2)), 8); DrawCirc(green1, (tile.x*scale + (scale/2), tile.y*scale + (scale/2)), 4)
    
def DrawHole(tile):
    DrawCirc(brown, (tile.x*scale + (scale/2-1), tile.y*scale + (scale/2-1)), 12); DrawCirc(black2, (tile.x*scale + (scale/2), tile.y*scale + (scale/2)), 12); DrawCirc(black3, (tile.x*scale + (scale/2), tile.y*scale + (scale/2)), 10)
    
def DrawShadow(tile):
    DrawCirc(darkblue, (tile.x*scale + (scale/2-1), tile.y*scale + (scale/2-1)), 16)

def DrawStore(tile):
    DrawRect(store2, [tile.x*scale + (scale/4), tile.y*scale + (scale/4), scale/2, scale/2], 0); DrawRect(store1, [tile.x*scale + (scale/3), tile.y*scale + (scale/3), int(scale/3), int(scale/3)], 0)
    

def rr(a, b):
    return random.randrange(a, b, 1)

def flip():
    Screen.blit(Display, display_offset)
    title_surf = title_font.render('TREASURE HUNT SIMULATOR', True, white)
    title_rect = title_surf.get_rect(center=(screen_w // 2, display_offset[1] // 2))
    Screen.blit(title_surf, title_rect)
    right_x = display_offset[0] + x_resolution + 20
    line_h = title_font.get_linesize()
    total_h = line_h * len(controls)
    start_y = display_offset[1] + (y_resolution - total_h) // 2
    for i, line in enumerate(controls):
        color = white if (line != 'A: View Atlas' or state['hasatlas']) else black
        surf = instruction_font.render(line, True, color)
        Screen.blit(surf, (right_x, start_y + i * line_h))
    elapsed = min(int((finish_time or time.time()) - start_time), 5999)
    mm = elapsed // 60; ss = elapsed % 60
    timer_surf = instruction_font.render(f'Time: {mm:02}:{ss:02}', True, white)
    timer_rect = timer_surf.get_rect(bottomleft=(right_x, display_offset[1] + y_resolution))
    Screen.blit(timer_surf, timer_rect)
    pg.display.update()

def play_click():
    pg.mixer.Sound('Assets/Sound/Click.wav').play()

def play_splash():
    pg.mixer.Sound('Assets/Sound/Splash.wav').play()

def play_gold():
    pg.mixer.Sound('Assets/Sound/Gold.wav').play()

def blink():
    t = time.time()
    blink = 0
    digits = int(repr(t)[11:13])
    if 0 < digits < 49:
        blink = False
    elif 50 < digits < 99:
        blink = True
    return blink

#Objects
class Tile:
    def __init__(self, coors, land_seed, touch_seed):
        self.name = 'Tile ' + str(coors)
        self.sea = (rr(50,55), rr(85,100), rr(195,215))
        self.land = (rr(125,150), rr(140,180), rr(70,75))
        self.shore = (rr(200,220), rr(160,175), rr(120,130))
        self.coin = None
        self.fish = None
        self.seaweed = None
        self.coral = None
        self.store = None
        self.tree = None
        self.hole = None
        self.shadow = None
        Tile.goal = False
        self.locate = coors
        self.x = coors[0]
        self.y = coors[1]
        self.tile_type = str()
        self.land_seed = land_seed
        self.touch_seed = touch_seed
        self.randint = rr(1, 10000)
        if self.land_seed == 1:
            self.randint = 0
        if 1 in self.touch_seed:
            self.randint = rr(0,1000)
        if self.randint < nLand:
            self.tile_type = 'Land'
        elif self.randint < nShore:
            self.tile_type = 'Shore'
        else:
            self.tile_type = 'Water'
            
        if self.tile_type == 'Water':
            if self.randint > nCoin:
                self.coin = True
            if self.randint > nFish and self.randint < nCoin:
                self.fish = True
            if self.randint > nSeaweed and self.randint < nFish:
                self.seaweed = True
            if self.randint > nShadow and self.randint < nCoral:
                self.coral = True
            if self.randint < nShadow:
                self.shadow = True
            
        if self.tile_type == 'Shore' and self.randint > nStore:
            self.store = True
        
        if self.tile_type == 'Land':
            if self.randint < nTree:
                self.tree = True
            if self.randint > nHole:
                self.hole = True
            
    def draw(self, a, b):
        if self.tile_type == 'Water':
            DrawRect(self.sea, [a*scale, b*scale, 49, 49], 0)
        elif self.tile_type == 'Shore':
            DrawRect(self.shore, [a*scale, b*scale, 49, 49], 0)
        else:
            DrawRect(self.land, [a*scale, b*scale, 49, 49], 0)
            
class NetherTile:
    def __init__(self, coors, land_seed, touch_seed):
        self.name = 'Tile ' + str(coors)
        self.sea = (rr(10,50), rr(10,50), rr(10,50))
        self.land = (rr(140,200), rr(140,200), rr(140,200))
        self.bright = (rr(229,230), rr(229,230), rr(0,1))
        self.coin = None
        self.fish = None
        self.seaweed = None
        self.coral = None
        self.store = None
        self.tree = None
        self.hole = None
        self.shadow = None
        self.goal = None
        self.locate = coors
        self.x = coors[0]
        self.y = coors[1]
        self.tile_type = str()
        self.land_seed = land_seed
        self.touch_seed = touch_seed
        self.randint = rr(1, 10000)
        if self.land_seed == 1:
            self.randint = 0
        if 1 in self.touch_seed:
            self.randint = rr(0,1500)
        if self.randint < nLand:
            self.tile_type = 'Land'
        else:
            self.tile_type = 'Water'
            
        if self.tile_type == 'Water':
            if self.randint > 9985:
                self.goal = True    
                
    def draw(self, a, b):
        if self.tile_type == 'Water':
            DrawRect(self.sea, [a*scale, b*scale, 49, 49], 0)
            if self.goal == True:
                DrawRect(self.bright, [a*scale, b*scale, 49, 49], 0)
                DrawCirc((rr(200,201), rr(185,186), rr(0,1)), (a*scale + (scale/2-1), b*scale + (scale/2-1)), 20)
        else:
            DrawRect(self.land, [a*scale, b*scale, 49, 49], 0)

class Map:
    def __init__(self, metcoords):
        self.name = 'Metacoords: ' + str(metcoords)
        self.innertest = 'Num unique to ' + str(metcoords) + ' : ' + str(rr(1,99))
        self.grid = []
        self.seeder = []
        self.x = metcoords[0]
        self.y = metcoords[1]
        for xf in range(0, 16):
            s_vertical = []
            for yf in range(0,12):
                island_seed = rr(1,1000)
                if island_seed < 40:
                    island_seed = 1
                else:
                    island_seed = 0
                s_vertical.append(island_seed)
            self.seeder.append(s_vertical)
        
        for x in range(0, 16):
            vertical = []
            for y in range(0,12):
                coor = (x,y)
                ls = self.seeder[x][y]
                try:
                    ts = (self.seeder[x-1][y-1],self.seeder[x-1][y],self.seeder[x-1][y+1],self.seeder[x][y-1],self.seeder[x][y+1],self.seeder[x+1][y-1],self.seeder[x+1][y],self.seeder[x+1][y+1])
                except:
                    ts = (0,0,0,0,0,0,0,0)
                vertical.append(Tile(coor,ls,ts))
            self.grid.append(vertical)
            
class NetherMap:
    def __init__(self, metcoords):
        self.name = 'Metacoords: ' + str(metcoords)
        self.innertest = 'Num unique to ' + str(metcoords) + ' : ' + str(rr(1,99))
        self.grid = []
        self.seeder = []
        self.x = metcoords[0]
        self.y = metcoords[1]
        for xf in range(0, 16):
            s_vertical = []
            for yf in range(0,12):
                island_seed = rr(1,1000)
                if island_seed < 40:
                    island_seed = 1
                else:
                    island_seed = 0
                s_vertical.append(island_seed)
            self.seeder.append(s_vertical)
        
        for x in range(0, 16):
            vertical = []
            for y in range(0,12):
                coor = (x,y)
                ls = self.seeder[x][y]
                try:
                    ts = (self.seeder[x-1][y-1],self.seeder[x-1][y],self.seeder[x-1][y+1],self.seeder[x][y-1],self.seeder[x][y+1],self.seeder[x+1][y-1],self.seeder[x+1][y],self.seeder[x+1][y+1])
                except:
                    ts = (0,0,0,0,0,0,0,0)
                vertical.append(NetherTile(coor,ls,ts))
            self.grid.append(vertical)

class Metamap:
    def __init__(self):
        self.name = 'The only overworld Metamap'
    
    def metachart():
        built_metamap = []
        for x in range(0, 16):
            vertical = []
            for y in range(0,12):
                coor = (x,y)
                vertical.append(Map(coor))
            built_metamap.append(vertical)
        return built_metamap

    metagrid = metachart()

class NetherMetamap:
    def __init__(self):
        self.name = 'The only underworld Metamap'
    
    def metachart():
        built_metamap = []
        for x in range(0, 16):
            vertical = []
            for y in range(0,12):
                coor = (x,y)
                vertical.append(NetherMap(coor))
            built_metamap.append(vertical)
        return built_metamap

    metagrid = metachart()

class Atlas:
    def __init__(self, metamap_grid):
        self.name = 'This is the Atlas'
        self.atlas = metamap_grid
    
    def draw_atlas(self, coords, metacoords, blinking):
        atlas = self.atlas
        coords = coords
        metacoords = metacoords
        mapsea = []
        mapland = []
        mapshore = []
        off = x_resolution/scale*(11/4)
        Layer_2 = pg.Surface((x_resolution, y_resolution))
        Layer_2.set_alpha(150)
        Layer_2.fill((0,0,0))
        Display.blit(Layer_2, (0,0))
        for vertical_atlas_strips in atlas:
            for map in vertical_atlas_strips:
                chunk_x = map.x
                chunk_y = map.y
                for vertical_tiles in map.grid:
                    for tile in vertical_tiles:
                        dot_x = tile.x
                        dot_y = tile.y
                        if not tile.tile_type == "Water":
                            if tile.tile_type == "Land":
                                mapland = tile.land
                                pg.draw.rect(Display, mapland, [x_resolution/8 + off + chunk_x*32 + dot_x*2, y_resolution/4 + chunk_y*24 + dot_y*2, 2, 2], 0)
                            if tile.tile_type == "Shore":
                                mapshore = tile.shore
                                pg.draw.rect(Display, mapshore, [x_resolution/8 + off + chunk_x*32 + dot_x*2, y_resolution/4 + chunk_y*24 + dot_y*2, 2, 2], 0)
                        else:
                            if tile.coral == False or tile.coral == None:
                                mapsea = tile.sea
                                pg.draw.rect(Display, mapsea, [x_resolution/8 + off + chunk_x*32 + dot_x*2, y_resolution/4 + chunk_y*24 + dot_y*2, 2, 2], 0)
                            elif tile.coral == True:
                                pg.draw.rect(Display, mapcoral, [x_resolution/8 + off + chunk_x*32 + dot_x*2, y_resolution/4 + chunk_y*24 + dot_y*2, 2, 2], 0)
        if blinking == True:
            cx = x_resolution/8 + off + metacoords[0]*32 + coords[0]*2
            cy = y_resolution/4 + metacoords[1]*24 + coords[1]*2
            pg.draw.rect(Display, red, (cx-6, cy, 6, 2), 0)   # left arm
            pg.draw.rect(Display, red, (cx+2, cy, 6, 2), 0)   # right arm
            pg.draw.rect(Display, red, (cx, cy-6, 2, 6), 0)   # top arm
            pg.draw.rect(Display, red, (cx, cy+2, 2, 6), 0)   # bottom arm

#Functions
def mapdraw(current_map_grid):
    xdraw = 0
    ydraw = 0
    for column in current_map_grid:
        ydraw = 0
        for tile in column:
            tile.draw(xdraw,ydraw)
            ydraw = ydraw + 1
        xdraw = xdraw + 1
        
def itemdraw(current_map_grid):
    xdraw = 0
    ydraw = 0
    for column in current_map_grid:
        ydraw = 0
        for tile in column:
            if tile.coin == True:
                DrawCoin(tile)
            if tile.store == True:
                DrawStore(tile)
            if tile.hole == True:
                DrawHole(tile)
            if tile.tree == True:
                DrawTree(tile)
            if tile.shadow == True and inventory["Fishing Pole"] > 0:
                DrawShadow(tile)
                
            ydraw = ydraw + 1
        xdraw = xdraw + 1
                
def display_inventory(inv):
    headerpos = (x_resolution/2, y_resolution/2 - 40)
    goldpos = (x_resolution/2, y_resolution/2 + 40)
    polepos = (x_resolution/2, y_resolution/2 + 80)
    fishpos = (x_resolution/2, y_resolution/2 + 120)
    sweedpos = (x_resolution/2, y_resolution/2 + 160)
    coralpos = (x_resolution/2, y_resolution/2 + 200)
    Layer_2 = pg.Surface((x_resolution, y_resolution))
    Layer_2.set_alpha(130)
    Layer_2.fill((0,0,0))
    inv_head = general_font.render('~Inventory~', True, white)    
    inv_gold = general_font.render( "Gold - " + str(inventory["Gold"]), True, white)
    inv_pole = general_font.render( "Fishing Pole - " + str(inventory["Fishing Pole"]), True, white)
    inv_fish = general_font.render( "Fish - " + str(inventory["Fish"]), True, white)
    inv_sweed = general_font.render( "Seaweed - " + str(inventory["Seaweed"]), True, white)
    inv_coral = general_font.render( "Coral - " + str(inventory["Coral"]), True, white)
    inv_headRect = inv_head.get_rect(); inv_goldRect = inv_gold.get_rect(); inv_poleRect = inv_pole.get_rect(); inv_fishRect = inv_fish.get_rect(); inv_sweedRect = inv_sweed.get_rect(); inv_coralRect = inv_coral.get_rect()
    inv_headRect.center = headerpos; inv_goldRect.center = goldpos; inv_poleRect.center = polepos; inv_fishRect.center = fishpos; inv_sweedRect.center = sweedpos; inv_coralRect.center = coralpos
    Layer_2.blit(inv_head, inv_headRect); Layer_2.blit(inv_gold, inv_goldRect)
    if inventory["Fishing Pole"] > 0:
        Layer_2.blit(inv_pole, inv_poleRect); Display.blit(inv_pole, inv_poleRect)
    if inventory["Fish"] > 0:
        Layer_2.blit(inv_fish, inv_fishRect); Display.blit(inv_fish, inv_fishRect)    
    if inventory["Seaweed"] > 0:
        Layer_2.blit(inv_sweed, inv_sweedRect); Display.blit(inv_sweed, inv_sweedRect)
    if inventory["Coral"] > 0:
        Layer_2.blit(inv_coral, inv_coralRect); Display.blit(inv_coral, inv_coralRect)
    
    
    Display.blit(inv_head, inv_headRect); Display.blit(inv_gold, inv_goldRect);
    Display.blit(Layer_2, (0,0))
    flip()

def move_handler(x, y, meta_x, meta_y, xbeforemove, ybeforemove, metaxbeforemove, metaybeforemove):
    if x != xbeforemove or y != ybeforemove:
        play_click()
    xbeforemove = x
    ybeforemove = y
    metaxbeforemove = meta_x
    metaybeforemove = meta_y
    return xbeforemove, ybeforemove, metaxbeforemove, metaybeforemove


def menu_handler():
    for event in pg.event.get():
        if event.type == pg.QUIT:
            return "Exit"
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                return "Exit"
            if event.key == pg.K_y:
                play_click()
                return 'y'
            elif event.key == pg.K_n:
                play_click()
                return 'n'
            elif event.key == pg.K_a:
                play_click()
                return False
            if event.key == pg.K_SPACE:
                play_click()
                return False
            elif event.key == pg.K_RETURN:
                play_click()
                return False
    return True

def quest_handler(inventory, quest, selected_tile, landwalk):
    inventory = inventory
    quest = quest
    selected_tile = selected_tile
    landwalk = landwalk
    if selected_tile.shadow == True:
        if 0 < quest < 5:
            quest = quest + 1
        selected_tile.shadow = False
    if inventory["Fishing Pole"] == 1 and quest == 0:
        inventory["Gold"] = inventory["Gold"] - 50
        quest = 1
    if inventory["Potion"] == "Active" and quest == 5:
        inventory["Gold"] = inventory["Gold"] - 100
        inventory["Coral"] = inventory["Coral"] - 10
        landwalk = True
        quest = quest + 1
    
    return inventory, quest, selected_tile, landwalk

def spacebar_handler(selected_tile, catch, landwalk):
    catch = catch
    landwalk = landwalk
    text = ""
    if inventory["Fishing Pole"] == 0:
        text = "There's nothing here"
    else:
        if selected_tile.fish == True:
            inventory["Fish"] = inventory["Fish"] + 1
            selected_tile.fish = False
            catch = True
            text = "You caught something"
        elif selected_tile.seaweed == True:
            inventory["Seaweed"] = inventory["Seaweed"] + 1
            selected_tile.seaweed = False
            catch = True
            text = "You caught something"
        elif selected_tile.coral == True:
            inventory["Coral"] = inventory["Coral"] + 1
            selected_tile.coral = False
            catch = True
            text = "You caught something"
        elif catch == True:
            text = "You caught something"
        else:
            if landwalk == True:
                if selected_tile.tile_type == "Water":
                    text = "Nothing's biting"
                else:
                    text = "There's nothing here"
            else:
                text = "Nothing's biting"
    
    return text, catch

def key_parser(x, y, quest, selected_tile):
    x = x
    y = y
    selected_tile = selected_tile
    running = True
    k_return = False
    k_space = None
    k_a = None
    move_bool = False
    #Key presses
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                running = False
            if event.key == pg.K_RETURN:
                k_return = True
            if event.key == pg.K_LEFT:
                x = x-1
                move_bool = True
            if event.key == pg.K_RIGHT:
                x = x+1
                move_bool = True
            if event.key == pg.K_UP:
                y = y-1
                move_bool = True
            if event.key == pg.K_DOWN:
                y = y+1
                move_bool = True
            if event.key == pg.K_a:
                k_a = True
            if event.key == pg.K_SPACE:
                k_space = True
                if quest > 0 and selected_tile.tile_type == 'Water':
                    play_splash()

    return x, y, running, k_return, k_space, k_a, move_bool

def boundary_checker(xin, yin, xbeforemovein, ybeforemovein, metaxin, metayin, metaxbeforemovein, metaybeforemovein, metamapin, landwalk):
    landwalk = landwalk
    x = xin; y = yin
    meta_x = metaxin; meta_y = metayin
    xbeforemove = xbeforemovein; ybeforemove = ybeforemovein
    metaxbeforemove = metaxbeforemovein; metaybeforemove = metaybeforemovein
    metamap = metamapin
    if landwalk == True:
        if x == 16:
            meta_x = meta_x + 1
            if meta_x == 16:
                meta_x = 0
            x = 0
        if x == -1:
            meta_x = meta_x - 1
            if meta_x == -1:
                meta_x = 15
            x = 15
        if y == 12:
            meta_y = meta_y + 1
            if meta_y == 12:
                meta_y = 0
            y = 0
        if y == -1:
            meta_y = meta_y - 1
            if meta_y == -1:
                meta_y = 11
            y = 11
        return x, y, meta_x, meta_y
    elif landwalk == False:
        if x == 16:
            meta_x = meta_x + 1
            if meta_x == 16:
                meta_x = 0
            x = 0
            tilechecker = metamap[meta_x][meta_y].grid
            if not tilechecker[x][y].tile_type == 'Water':
                meta_x = metaxbeforemove
                x = xbeforemove
        if x == -1:
            meta_x = meta_x - 1
            if meta_x == -1:
                meta_x = 15
            x = 15
            tilechecker = metamap[meta_x][meta_y].grid
            if not tilechecker[x][y].tile_type == 'Water':
                meta_x = metaxbeforemove
                x = xbeforemove
        if y == 12:
            meta_y = meta_y + 1
            if meta_y == 12:
                meta_y = 0
            y = 0
            tilechecker = metamap[meta_x][meta_y].grid
            if not tilechecker[x][y].tile_type == 'Water':
                meta_y = metaybeforemove
                y = ybeforemove
        if y == -1:
            meta_y = meta_y - 1
            if meta_y == -1:
                meta_y = 11
            y = 11
            tilechecker = metamap[meta_x][meta_y].grid
            if not tilechecker[x][y].tile_type == 'Water':
                meta_y = metaybeforemove
                y = ybeforemove
        
        return x, y, meta_x, meta_y
    
def store(menu_option, quest):
    menu_option = menu_option
    quest = quest
    Layer_2 = pg.Surface((x_resolution, y_resolution))
    Layer_2.set_alpha(130)
    Layer_2.fill((0,0,0))
    store_header = general_font.render('~Sandy Bazaar~', True, white)
    store_text2 = None
    if quest == 0:
        if inventory["Gold"] < 49:
            store_text = general_font.render("For 50 gold, you can have this tool that I found.", True, white)
        else:
            store_text = general_font.render("Want to buy this nifty fishing pole for 50 gold? y/n", True, white)
            if menu_option == 'y':
                inventory["Fishing Pole"] = 1
                store_text = general_font.render("Thank you! (Use spacebar to fish)", True, white)
            elif menu_option == 'n':
                store_text = general_font.render("Okay! Come back any time.", True, white)
    else:
        store_text  = general_font.render("I'm afraid I'm out of wares!", True, white)
        store_text2 = general_font.render("But keep a lookout for coral...", True, white)

    if quest > 4:
        if inventory["Gold"] > 99 and inventory ["Coral"] > 9:
            store_text  = general_font.render("Would you like me to make you a potion", True, white)
            store_text2 = general_font.render("that will let you dwell on land? y/n", True, white)
            if menu_option == 'y':
                inventory["Potion"] = "Active"
                store_text  = general_font.render("The formula is unstable, so you'll have to", True, white)
                store_text2 = general_font.render("drink it now... have fun!", True, white)
            elif menu_option == 'n':
                store_text  = general_font.render("Okay! Come back any time.", True, white)
                store_text2 = None
        else:
            store_text  = general_font.render("For 10 coral and 100 gold, I can make you", True, white)
            store_text2 = general_font.render("a potion that will change everything!", True, white)

    store_headRect = store_header.get_rect(center=(x_resolution/2, y_resolution/2 - 40))
    store_textRect = store_text.get_rect(center=(x_resolution/2, y_resolution/2 + 20))
    Layer_2.blit(store_header, store_headRect); Layer_2.blit(store_text, store_textRect)
    Display.blit(store_header, store_headRect); Display.blit(store_text, store_textRect)
    if store_text2:
        store_text2Rect = store_text2.get_rect(center=(x_resolution/2, y_resolution/2 + 60))
        Layer_2.blit(store_text2, store_text2Rect)
        Display.blit(store_text2, store_text2Rect)
    Display.blit(Layer_2, (0,0))
    flip()
    
def shadow(quest):
    Layer_2 = pg.Surface((x_resolution, y_resolution)); Layer_2.set_alpha(130); Layer_2.fill((0,0,0))
    if quest == 1:
        shadow_header = general_font.render('~MAIA THE MAGIC TALKING FISH~', True, white)
        shadow_text  = general_font.render("Hello, my brother has a map you may find useful...", True, white)
        shadow_text2 = general_font.render("Not sure where he went.", True, white)
    elif quest == 2:
        shadow_header = general_font.render('~HANS THE MAGIC TALKING FISH~', True, white)
        shadow_text  = general_font.render("Entschuldigung, nicht zie fischen du bist looking for...", True, white)
        shadow_text2 = general_font.render("Schprechen mit Miguel.", True, white)
    elif quest == 3:
        shadow_header = general_font.render('~MIGUEL THE MAGIC TALKING FISH~', True, white)
        shadow_text  = general_font.render("Senior, you are seeking a different pescado magico...", True, white)
        shadow_text2 = general_font.render("Keep fishing.", True, white)
    elif quest == 4:
        shadow_header = general_font.render('~JULIAN THE MAGIC TALKING FISH~', True, white)
        shadow_text  = general_font.render("No, I'm not related to any of those fish...", True, white)
        shadow_text2 = general_font.render("But I do have a map. (Press A to view)", True, white)
        state['hasatlas'] = True
    else:
        shadow_header = general_font.render('~SOME TALKING FISH~', True, white)
        shadow_text  = general_font.render("The pink dots on your map are areas that", True, white)
        shadow_text2 = general_font.render("have been known to harbor coral.", True, white)

    shadow_headRect  = shadow_header.get_rect(center=(x_resolution/2, y_resolution/2 - 40))
    shadow_textRect  = shadow_text.get_rect(center=(x_resolution/2, y_resolution/2 + 20))
    shadow_text2Rect = shadow_text2.get_rect(center=(x_resolution/2, y_resolution/2 + 60))
    Layer_2.blit(shadow_header, shadow_headRect); Layer_2.blit(shadow_text, shadow_textRect); Layer_2.blit(shadow_text2, shadow_text2Rect)
    Display.blit(shadow_header, shadow_headRect); Display.blit(shadow_text, shadow_textRect); Display.blit(shadow_text2, shadow_text2Rect)
    Display.blit(Layer_2, (0,0))
    flip()
    
    return

def land_tally_limiter(inp, recurs):
    land_tally = recurs
    if inp == True:
        land_tally = land_tally + 1
        
    return land_tally

def Credits():
    global finish_time
    if finish_time is None:
        finish_time = time.time()
    elapsed = min(int(finish_time - start_time), 5999)
    mm = elapsed // 60; ss = elapsed % 60
    Display.fill((200, 200, 0))
    credits_header = general_font.render('~Credits~', True, brown)
    credits_text = general_font.render("A game by Vincent Wisehoon", True, brown)
    credits_text2 = general_font.render("Good Game", True, brown)
    credits_time = general_font.render(f'Time: {mm:02}:{ss:02}', True, brown)
    credits_headRect = credits_header.get_rect(); credits_textRect = credits_text.get_rect(); credits_text2Rect = credits_text2.get_rect(); credits_timeRect = credits_time.get_rect()
    credits_headRect.center = (x_resolution/2, y_resolution/2 - 80); credits_textRect.center = (x_resolution/2, y_resolution/2); credits_text2Rect.center = (x_resolution/2, y_resolution/2 + 80); credits_timeRect.center = (x_resolution/2, y_resolution/2 + 160)
    Display.blit(credits_header, credits_headRect); Display.blit(credits_text, credits_textRect); Display.blit(credits_text2, credits_text2Rect); Display.blit(credits_time, credits_timeRect)
    flip()