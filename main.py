import pyautogui as pag
from time import sleep
from scan_app import *
from edit import *

# Todo
# Auto crop with border detection
# Compress images
# Add a progress bar
# Add sound notification when ready to scan
# Edit images


def main():
    open_scanner()

    # should_loop = input('Number of scans: ')
    counter = 1
    while True:

        scan_dialog()
        scan_settings()
        is_scanning()
        done_scanning()

        print('finished scan ' + str(counter))
        counter += 1

        # sleep(2)
        back_to_cmd()
        should_continue = input('Continue? ')
        if should_continue == '':
            continue
        else:
            break


    crop_imgs()
        

main()