import pygame as pg

print('Setup Start')
pg.init()
windows = pg.display.set_mode(size= (600, 480))
print('Setup End')

print('Loop Start')
while True:
    # Check for all events
    for event in pg.event.get():
        if event.type == pg.QUIT:
            print("Quitting...")
            pg.quit() # Close window
            quit() # End paygame
