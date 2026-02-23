import select
from Functions import *

#Initializations
running = True
menu_option = None; invtoggle = None; storemode = False; nether = False; catch = False
xbeforemove = 0; ybeforemove = 0
metaxbeforemove = 0; metaybeforemove = 0
metamap = Metamap().metagrid; overworld_atlas = Atlas(metamap)
nether_metamap = NetherMetamap().metagrid; underworld_atlas = Atlas(nether_metamap)
current_map = metamap[meta_x][meta_y]; current_map_grid = current_map.grid
current_nethmap = nether_metamap[meta_x][meta_y]; current_nethmap_grid = current_nethmap.grid
selected_tile = current_map_grid[x][y]
pg.key.set_repeat(440,220)

#Main running functionality
while running: #move_handler(), menu_handler(), quest_handler(), boundary_checker()
    xbeforemove, ybeforemove, metaxbeforemove, metaybeforemove = move_handler(x, y, meta_x, meta_y, xbeforemove, ybeforemove, metaxbeforemove, metaybeforemove)
    if menumode == True:
        if (menu_result := menu_handler()) == 'Exit':
            running = False
        elif menu_result == 'y':
            menu_option = 'y'
        elif menu_result == 'n':
            menu_option = 'n'
        elif menu_result == False:
            menumode = False; menu_result = None; storemode = False; invtoggle = False; atlastoggle = False; spacetoggle = False; menu_option = None; catch = False
            inventory, quest, selected_tile, landwalk = quest_handler(inventory, quest, selected_tile, landwalk)
            #if inventory["Potion"] == "Active":
            #    landwalk = True

    else:
        x, y, running, invtoggle, spacetoggle, atlastoggle, move_bool = key_parser(x, y, quest, selected_tile)
        
    try:
        x, y, meta_x, meta_y = boundary_checker(x, y, xbeforemove, ybeforemove, meta_x, meta_y, metaxbeforemove, metaybeforemove, metamap, landwalk)
    except:
        x = xbeforemove; meta_x = metaxbeforemove
        y = ybeforemove; meta_y = metaybeforemove

    if nether == True:
        current_nethmap = nether_metamap[meta_x][meta_y]
        current_nethmap_grid = current_nethmap.grid
        selected_tile = current_nethmap_grid[x][y]
    else:
        current_map = metamap[meta_x][meta_y]
        current_map_grid = current_map.grid
        selected_tile = current_map_grid[x][y]

    if selected_tile.store == True:
        if landwalk == True:
            None
        else:    
            x = xbeforemove
            y = ybeforemove
            storemode = True
            menumode = True

    if landwalk == False:
        if selected_tile.tile_type == 'Water':
            None
        elif not selected_tile.tile_type == 'Water':
            x = xbeforemove
            y = ybeforemove
    elif landwalk == True:
        land_tally = land_tally_limiter(move_bool, land_tally)
        if land_tally == 4000:
            landwalk = False
        
    if selected_tile.coin == True:
        inventory["Gold"] = inventory["Gold"] + 10
        play_gold()
        selected_tile.coin = False
    
    Screen.fill(black)
    Display.fill(black)
    if nether == True:
        mapdraw(current_nethmap_grid)
    else:
        mapdraw(current_map_grid)
        itemdraw(current_map_grid)
    coords = [x,y]
    metacoords = [meta_x, meta_y]
    Draw_Cursor(coords, scale)
    below_y = display_offset[1] + y_resolution + 10
    coords_text = coords_font.render('coords: ' + str(coords), True, white); coords_textRect = coords_text.get_rect(); coords_textRect.midleft = (display_offset[0], below_y)
    Screen.blit(coords_text, coords_textRect)
    if landwalk == True:
        p_left = coords_font.render('You have ', True, white)
        p_num  = coords_font.render(str(4000 - land_tally), True, white)
        p_right = coords_font.render(' steps before potion effects end', True, white)
        num_max_w = coords_font.size('4000')[0]
        mid_x = screen_w // 2
        num_right_x = mid_x + num_max_w // 2
        Screen.blit(p_left,  p_left.get_rect(midright=(num_right_x - num_max_w, below_y)))
        Screen.blit(p_num,   p_num.get_rect(midright=(num_right_x, below_y)))
        Screen.blit(p_right, p_right.get_rect(midleft=(num_right_x, below_y)))
    if invtoggle == True:
        menumode = True; display_inventory(inventory)
    if storemode == True:
        store(menu_option, quest)
    if spacetoggle == True:
        menumode = True
        if not selected_tile.shadow == True:
            spacebar_text, catch = spacebar_handler(selected_tile, catch, landwalk)
            space_text = coords_font.render(f'{spacebar_text}', True, white); space_textRect = space_text.get_rect(); space_textRect.center = (x_resolution/2, y_resolution - y_resolution/24)
            Display.blit(space_text, space_textRect)
        else:
            shadow(quest)
    if atlastoggle == True:
        if state['hasatlas'] == True:
            menumode = True
            blinking = blink()
            if nether == False:
                overworld_atlas.draw_atlas(coords, metacoords, blinking)
            else:
                underworld_atlas.draw_atlas(coords, metacoords, blinking)
    
    if selected_tile.hole == True and spacetoggle == True:
        nether = True
        spacetoggle = False
        menumode = False
        landwalk = False
        
    if selected_tile.goal == True:
        Credits()
        menumode = True
        
    flip()