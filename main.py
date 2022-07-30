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
    create_dir('results/before_crop')
    create_dir('results/bkp')

    should_clear = input('Do you want to clear the images? (y/n) ')
    if should_clear == 'y' or should_clear == 'Y':
        clear_dir('results/before_crop', True)
        clear_dir('results/after_crop', True)

    open_scanner()

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


    should_crop = input('Crop images? (y/n): ')
    if should_crop == 'y' or should_crop == 'Y':
        crop_imgs()
    else: 
        print('exiting...')
        sleep(1)
        

main()