# -*- coding: utf-8 -*-
#############################################################
#                          IMPORTS                          #
#############################################################
import random
import board
from time import sleep
from analogio import AnalogIn
from story import story
import displayio
from adafruit_bitmap_font import bitmap_font
from adafruit_display_text import label, wrap_text_to_lines
import adafruit_touchscreen
import audiocore
import audiomixer
from audioio import AudioOut

#############################################################
#                          CONTENT                          #
#############################################################
# ---------------- Colors ---------------- #
WHITE = 0xFFFFFF
BLACK = 0x000000
FIRE = 0xAA5500
EARTH = 0x64EE64
WATER = 0x0687FF
ELIXIR = 0x9F272F
AIR = 0xB0BCBF

# --------------- Captions --------------- #
CAPTIONS = [["Feu", FIRE, 156, 156],
            ["Terre", EARTH, 0, 130],
            ["Eau", WATER, 327, 156],
            ["Elixir", ELIXIR, 165, 52],
            ["Air", AIR, 184, 52],
            ]

cwd = ("/"+__file__).rsplit('/', 1)[0] # the current working directory (where this file is)

# --------------- Random ----------------- #
seed = AnalogIn(board.A1)
random.seed(seed.value)
seed.deinit()

# ------------- Screen Setup ------------- #
display = board.DISPLAY
display.rotation = 0
display.brightness = 0.4

ts = adafruit_touchscreen.Touchscreen(
            board.TOUCH_YU,
            board.TOUCH_YD,
            board.TOUCH_XL,
            board.TOUCH_XR,
            calibration=((5200, 59000), (5800, 57000)),
            size=(320, 480),
        )

# Main font
font = bitmap_font.load_font("/fonts/Helvetica-Bold-16.bdf")

text_label = label.Label(font, text="Chargement", color=WHITE)
element_label = label.Label(font, text="", color=WHITE)
display.root_group = text_label
display.root_group.append(element_label) 

# ------------ Sound Effects ------------- #
wav_files = (
    '/sounds/next1.wav',
    '/sounds/next2.wav',
    '/sounds/next3.wav',
    '/sounds/music.wav',
)

audio = AudioOut( board.A0 )  # RP2040 PWM, use RC filter on breadboard
mixer = audiomixer.Mixer(voice_count=2, sample_rate=22050, channel_count=1,
                         bits_per_sample=16, samples_signed=True)
audio.play(mixer) # attach mixer to audio playback

wave = audiocore.WaveFile(open(wav_files[3],"rb"))
mixer.voice[0].play(wave, loop=True)
mixer.voice[0].level = 0.3

def text_box(string, target=text_label, x=13, y=21, max_chars=54):
    text = wrap_text_to_lines(string, max_chars)
    new_text = ""
    test = ""

    for w in text:
        new_text += "\n" + w
        test += "M\n"

    text_height = label.Label(font, text="M", color=0x03AD31)
    text_height.text = test  # Odd things happen without this
    glyph_box = text_height.bounding_box
    target.text = ""  # Odd things happen without this
    target.x = x
    target.y = y
    target.text = new_text

def caption(*args) :
    element_label.text = args[0]
    element_label.color = args[1]
    element_label.x = args[2]        
    element_label.y = args[3]

#############################################################
#                         MAIN LOOP                         #
#############################################################
text_box("Chargement...", x=184, y=120)
mixer.voice[1].play(audiocore.WaveFile(open(wav_files[1],"rb")))
font.load_glyphs(b"aàbcdeéèfghjiklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890- ()")
sleep(0.5)
text_box("La Renaissance Élémentaire\n"  + (" " * 40) + "Un Air Malade\n", x=132, y=120) # show title
mixer.voice[1].play(audiocore.WaveFile(open(wav_files[2],"rb")))

while True:
    if ts.touch_point:
        mixer.voice[1].play(audiocore.WaveFile(open(wav_files[0],"rb")))
        if len(story) > 0 :
            element_label.text = ""    
            text_box(story.pop(0))
            if len(story) == 4 :
                caption(CAPTIONS[0][0], CAPTIONS[0][1], CAPTIONS[0][2], CAPTIONS[0][3])
            elif len(story) == 3 :
                caption(CAPTIONS[1][0], CAPTIONS[1][1], CAPTIONS[1][2], CAPTIONS[1][3])
            elif len(story) == 2 :
                caption(CAPTIONS[2][0], CAPTIONS[2][1], CAPTIONS[2][2], CAPTIONS[2][3])
            elif len(story) == 0 :
                caption(CAPTIONS[3][0], CAPTIONS[3][1], CAPTIONS[3][2], CAPTIONS[3][3])
        else :
            element_label.text = ""
            text_box("Bonne chance, Héros des éléments !\n" + " " * 35 + "Sauvez notre Air !", x=96, y=120)
            caption(CAPTIONS[4][0], CAPTIONS[4][1], CAPTIONS[4][2], CAPTIONS[4][3])

            sleep(2)

            for i in range(mixer.voice[0].level * 100):
                mixer.voice[0].level = min(max(mixer.voice[0].level - 0.01, 0), 1)
                sleep(0.2)
            mixer.voice[0].stop()
            audio.deinit() 

        # don't repeat until a new touch begins
        while ts.touch_point:
            continue
