import select
from Functions import *

# Splash Screen and Initializations

Display.fill((0,0,0))
gen_text = title_font.render('Generating...', True, white); gen_rect = gen_text.get_rect(); gen_rect.center = (x_resolution/2, y_resolution/2)
Display.blit(gen_text, gen_rect); flip()

# Generate World; but only allow worlds with a navigable spawn point

surface_world = World('Surface'); spawn_chunk = surface_world.grid[chunk_x][chunk_y].grid
while not all(spawn_chunk[x+dx][y+dy].navigable for dx, dy in [(0,0),(1,0),(-1,0),(0,1),(0,-1)]):
    surface_world = World('Surface')
    spawn_chunk = surface_world.grid[chunk_x][chunk_y].grid
surface_atlas = Atlas(surface_world.grid)
subterrain_world = World('Subterrain'); subterrain_atlas = Atlas(subterrain_world.grid)
active_worldgrid = surface_world.grid; active_atlas = surface_atlas
current_chunk = active_worldgrid[chunk_x][chunk_y]; current_chunk_grid = current_chunk.grid
selected_tile = current_chunk_grid[x][y]

running = True; menu_option = None; invtoggle = None; storemode = False; catch = False; creditsmode = False

xbeforemove = 0; ybeforemove = 0; chunkxbeforemove = 0; chunkybeforemove = 0

# Main Game Loop

while running:

    if creditsmode == True:
        Credits()
        continue

    # Determine Movement and Collision states

    xbeforemove, ybeforemove, chunkxbeforemove, chunkybeforemove = move_handler(x, y, chunk_x, chunk_y, xbeforemove, ybeforemove, chunkxbeforemove, chunkybeforemove)
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
    else:
        x, y, running, invtoggle, spacetoggle, atlastoggle, move_bool = key_parser(x, y, quest, selected_tile)
    try:
        x, y, chunk_x, chunk_y = boundary_checker(active_worldgrid, landwalk, x, y, chunk_x, chunk_y, xbeforemove, ybeforemove, chunkxbeforemove, chunkybeforemove)
    except:
        x = xbeforemove; chunk_x = chunkxbeforemove
        y = ybeforemove; chunk_y = chunkybeforemove
    current_chunk = active_worldgrid[chunk_x][chunk_y]
    current_chunk_grid = current_chunk.grid
    selected_tile = current_chunk_grid[x][y]
    if landwalk == False:
        if selected_tile.navigable == True:
            None
        elif selected_tile.navigable == False:
            x = xbeforemove
            y = ybeforemove
    elif landwalk == True:
        land_tally = land_tally_calculator(move_bool, land_tally)
        if land_tally == 4000:
            landwalk = False
    if hasattr(selected_tile, 'store') and selected_tile.store == True:
        if landwalk == True:
            None
        else:    
            x = xbeforemove
            y = ybeforemove
            storemode = True
            menumode = True
    if hasattr(selected_tile, 'coin') and selected_tile.coin == True:
        inventory["Gold"] = inventory["Gold"] + 10
        play_gold()
        selected_tile.coin = False
    
    # Display/Draw the above Movement and Collision states

    Screen.fill(black); Display.fill(black)
    chunk_draw(current_chunk_grid); item_draw(current_chunk_grid)
    coords = [x,y]; chunkcoords = [chunk_x, chunk_y]
    Draw_Cursor(coords, scale)
    below_y = display_offset[1] + y_resolution + 10
    coords_text = coords_font.render('coords: ' + str(coords), True, white); coords_textRect = coords_text.get_rect(); coords_textRect.midleft = (display_offset[0], below_y)
    Screen.blit(coords_text, coords_textRect)
    if landwalk == True:
        display_landwalk_metrics(land_tally)
    if invtoggle == True:
        menumode = True; display_inventory(inventory)
    if storemode == True:
        store(menu_option, quest)
    if spacetoggle == True:
        menumode = True
        if not hasattr(selected_tile, 'shadow') or not selected_tile.shadow == True or inventory['Fishing Pole'] == 0:
            spacebar_text, catch = spacebar_handler(selected_tile, catch, landwalk)
            space_text = coords_font.render(f'{spacebar_text}', True, white); space_textRect = space_text.get_rect(); space_textRect.center = (x_resolution/2, y_resolution - y_resolution/24)
            Display.blit(space_text, space_textRect)
        else:
            shadow(quest)
    if atlastoggle == True:
        if state['hasatlas'] == True:
            menumode = True
            blinking = blink()
            active_atlas.draw_atlas(coords, chunkcoords, blinking)
    if hasattr(selected_tile, 'hole') and selected_tile.hole == True and spacetoggle == True:
        active_worldgrid = subterrain_world.grid
        active_atlas = subterrain_atlas
        spacetoggle = False
        menumode = False
        landwalk = False
    if hasattr(selected_tile, 'goal') and selected_tile.goal == True and spacetoggle == True:
        creditsmode = True
        spacetoggle = False
        menumode = False
    flip()