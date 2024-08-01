#!/usr/bin/env python3

from StreamDeck.DeviceManager import DeviceManager
import sys

def main():
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

    deck_type = deck.deck_type()
    if deck_type == "":
        deck_type = "Stream Deck"

    print(f"""\
{deck_type} found:
    Vendor: {deck.vendor_id()}
    Product ID: {deck.product_id()}
    Serial Number: {deck.get_serial_number()}
    Firmware Version: {deck.get_firmware_version()}""")

    # Wait for user to kill the process
    while True:
        try:
            user_input = input()
        except EOFError:
            break

    deck.reset()
    deck.close()

if __name__ == "__main__":
    main()
