import pyautogui as pag
# from playsound import playsound
from time import sleep
from scan_app import *
from edit import *
from clear import *

# Todo
# Auto crop with border detection
# Edit images


def main():
    open_scanner()

    # should_loop = input('Number of scans: ')
    clear_dir('results/before_crop')
    clear_dir('results/after_crop', True)

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
        # playsound('apple_sucess_sfx.mp3')
        should_continue = input('Press enter to continue or any other key to exit: ')
        if should_continue == '':
            continue
        else:
            break


    crop_imgs()
        

main()