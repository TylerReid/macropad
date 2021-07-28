import board
import digitalio
import rotaryio
import neopixel
import keypad
import random
import time
import usb_hid
import terminalio

from _pixelbuf import colorwheel
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
from adafruit_hid.consumer_control import ConsumerControl
from adafruit_hid.consumer_control_code import ConsumerControlCode
from adafruit_display_text import label

#setup display
text_area = label.Label(terminalio.FONT, text="super cool macropad")
text_area.x = 10
text_area.y = 10
board.DISPLAY.show(text_area)

# configure device as keyboard
kbd = Keyboard(usb_hid.devices)
layout = KeyboardLayoutUS(kbd)
cc = ConsumerControl(usb_hid.devices)

write = lambda s: layout.write(s)

key_pins = (board.KEY1, board.KEY2, board.KEY3, board.KEY4, board.KEY5, board.KEY6,
            board.KEY7, board.KEY8, board.KEY9, board.KEY10, board.KEY11, board.KEY12)
keys = keypad.Keys(key_pins, value_when_pressed=False, pull=True)

encoder = rotaryio.IncrementalEncoder(board.ROTA, board.ROTB)
button = digitalio.DigitalInOut(board.BUTTON)
button.switch_to_input(pull=digitalio.Pull.UP)

pixels = neopixel.NeoPixel(board.NEOPIXEL, 12, brightness=0.2)
pixels.brightness = 1

last_position = encoder.position
pressed_keys = set({})
layer = "volume"

def update_layer_text():
    text = "Layer: " + layer + "\n"
    text_area.text = text

def update_layer_state():
    global layer
    if not button.value:
        #cc.send(ConsumerControlCode.PLAY_PAUSE)
        layer = "lights" if layer == "volume" else "volume"
        if layer != "lights":
            pixels.brightness = 1
            for p in range(12):
                pixels[p] = 0
        update_layer_text()
        time.sleep(0.2)


def handle_encoder():
    global last_position
    position = encoder.position
    if layer == "lights":
        if len(pressed_keys):
            pixels.brightness = 1
        else:
            pixels.brightness = 0.1
        color_value = ((position+80) * 2) % 255
        for p in range(12):
            if not p in pressed_keys:
                pixels[p] = colorwheel(color_value)
    elif layer == "volume":
        if last_position > position:
            #kbd.send(Keycode.CONTROL, Keycode.TAB)
            cc.send(ConsumerControlCode.VOLUME_INCREMENT)
        if last_position < position:
            #kbd.send(Keycode.CONTROL, Keycode.SHIFT, Keycode.TAB)
            cc.send(ConsumerControlCode.VOLUME_DECREMENT)
    last_position = position

default_keys = {
    8: lambda: write("blorp") if 2 in pressed_keys else lambda: None,
    9: lambda: write("bleep") if 3 in pressed_keys else lambda: None,
    10: lambda: write("bloop") if 4 in pressed_keys else lambda: None,
    11: lambda: write("lol") if 5 in pressed_keys else lambda: None,
}

layer_map = {
    "volume": default_keys
}

def handle_keys():
    event = keys.events.get()
    if event:
        if event.pressed:
            pressed_keys.add(event.key_number)
            pixels[event.key_number] = colorwheel(random.randint(1, 255))
            key_map = layer_map.get(layer, {})
            if event.key_number in key_map:
                key_map[event.key_number]()
        else:
            pressed_keys.discard(event.key_number)
            pixels[event.key_number] = 0

update_layer_text()

while True:
    update_layer_state()
    handle_encoder()
    handle_keys()
