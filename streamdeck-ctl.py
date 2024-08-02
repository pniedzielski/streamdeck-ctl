#!/usr/bin/env python3

from configparser import ConfigParser
import obsws_python as obs
import os
from PIL import Image, ImageDraw, ImageFont
import psutil
from StreamDeck.DeviceManager import DeviceManager
from StreamDeck.ImageHelpers import PILHelper
import sys
import threading
import time

global_config = ConfigParser()

def render_labeled_number(deck, number, label):
    center_font = ImageFont.load_default(size=48)
    label_font = ImageFont.load_default(size=14)

    key_image = PILHelper.create_key_image(deck)
    draw = ImageDraw.Draw(key_image)
    draw.text(
        (key_image.width / 2, key_image.height / 2),
        text=str(number),
        font=center_font,
        anchor="ms",
        fill="white"
    )
    draw.text(
        (key_image.width / 2, 7 * key_image.height / 8),
        text=label,
        font=label_font,
        anchor="ms",
        fill="white"
    )

    return PILHelper.to_native_key_format(deck, key_image)

def update_cpu_percent(deck, key_number):
    key_image = render_labeled_number(deck, psutil.cpu_percent(), "CPU %")
    with deck:
        deck.set_key_image(key_number, key_image)

def animate_system_metrics(deck):
    while deck.is_open():
        update_cpu_percent(deck, 7)
        time.sleep(2.5)

def main():
    global_config.read(os.path.expanduser("~/streamdeck.conf"))

    # Connect to Stream Deck
    stream_decks = DeviceManager().enumerate()
    match len(stream_decks):
        case 0:
            print("No Stream Deck found!", file=sys.stderr)
            sys.exit(-1)

        case 1:
            pass                # Found the device.

        case other:
            print(
                "Found more than one Stream Deck, unimplemented!",
                file=sys.stderr
            )
            sys.exit(-2)
    deck = stream_decks[0]

    deck.open()
    deck.reset()

    brightness = global_config.getint("streamdeck", "brightness", fallback=30)
    deck.set_brightness(brightness)

    deck_type = deck.deck_type()
    if deck_type == "":
        deck_type = "Stream Deck"

    print(f"""\
{deck_type} found:
    Vendor: {deck.vendor_id()}
    Product ID: {deck.product_id()}
    Serial Number: {deck.get_serial_number()}
    Firmware Version: {deck.get_firmware_version()}""")

    thread = threading.Thread(target=animate_system_metrics, args=[deck])
    thread.start()

    # Connect to OBS
    obs_host = global_config.get("obs", "host", fallback="localhost")
    obs_port = global_config.getint("obs", "port", fallback="4455")
    obs_password = global_config.get("obs", "password", fallback="")

    obs_client = obs.ReqClient(host=obs_host, port=obs_port, password=obs_password, timeout=3)

    resp = obs_client.get_version()
    print(f"Connected to OBS\n    Version: {resp.obs_version}")

    # Wait for user to kill the process
    while True:
        try:
            user_input = input()
        except EOFError:
            break

    deck.reset()
    deck.close()

    thread.join()

if __name__ == "__main__":
    main()
