# -*- coding: utf-8 -*-
#############################################################
#                          IMPORTS                          #
#############################################################
import random
import board
from analogio import AnalogIn
from story import story
from adafruit_pyportal import PyPortal

#############################################################
#                          CONTENT                          #
#############################################################
# --------------- Colors ----------------- #
WHITE = 0xFFFFFF
BLACK = 0x000000
FIRE = 0xAA5500
EARTH = 0x64EE64
WATER = 0x0687FF
ELIXIR = 0x9F272F
AIR = 0xB0BCBF

cwd = ("/"+__file__).rsplit('/', 1)[0] # the current working directory (where this file is)

# --------------- Random ----------------- #
seed = AnalogIn(board.A1)
random.seed(seed.value)
seed.deinit()
 
# ------------ Sound Effects ------------- #
soundNext1 = '/sounds/next1.wav'
soundNext2 = '/sounds/next2.wav'
soundNext3 = '/sounds/next3.wav'

# ------------- Screen Setup ------------- #
display = board.DISPLAY
display.rotation = 90
# display.auto_brightness = True

# ------------ Pyportal Setup ------------ #
pyportal = PyPortal(
                    status_neopixel = board.NEOPIXEL,
                    # text_font = "fonts/Arial-ItalicMT-23.bdf",
                    text_font = "fonts/Helvetica-Bold-16.bdf",
                    caption_font = "fonts/Helvetica-Bold-16.bdf",
                    # text_font = "fonts/Arial-Bold-24.bdf",
                    text_position = (13, 240),
                    text_color = WHITE
                   )

#############################################################
#                         MAIN LOOP                         #
#############################################################
pyportal.set_text((" " * 18) + "Chargement...") # display while user waits
pyportal.play_file(soundNext2)
pyportal.preload_font() # speed things up by preloading font
pyportal.set_text((" "*7) + "La Renaissance Élémentaire\n"  + (" " * 18) + "Un Air Malade\n \n" + (" " * 17) + "Touchez l'ecran\n " + (" " * 17) + "pour continuer") # show title
pyportal.play_file(soundNext3)


while True:
    if pyportal.touchscreen.touch_point:
        pyportal.play_file(soundNext1)
        # get random string from array and wrap w line breaks
        if len(story) > 0 :
            strat = pyportal.wrap_nicely(story.pop(0), 32)
            outstring = '\n'.join(strat)

            # display new text
            pyportal.set_text(outstring, 0)
        else :
            pyportal.set_text("Bonne chance, Héros des éléments !", 0)
            pyportal.set_caption("FEU", (10, 260), FIRE)
            pyportal.set_caption("TERRE", (60, 260), EARTH)
            pyportal.set_caption("EAU", (140, 260), WATER)
            pyportal.set_caption("ELIXIR", (200, 260), ELIXIR)
            pyportal.set_caption("AIR", (270, 260), AIR)
        
        # don't repeat until a new touch begins
        while pyportal.touchscreen.touch_point:
            continue


