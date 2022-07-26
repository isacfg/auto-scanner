import pyautogui as pag
import time

def open_scanner():
   
    scanner_icon = pag.locateCenterOnScreen('imgs\open_scanner.png')
    if scanner_icon:
        pag.moveTo(scanner_icon)
        pag.doubleClick()
        print('sucessfully found printer icon')
    else:
        print('could not find printer icon')
        return False

def scan_dialog():
    time.sleep(4)

    scan_dialog = pag.locateCenterOnScreen('imgs\scan_dialog.png')

    if scan_dialog:
        pag.moveTo(scan_dialog)
        pag.click()
        print('sucessfully found scan dialog')

    else:
        print('could not find scan dialog')
        return False

def scan_settings():
    time.sleep(4)

    auto_scan_option = pag.locateCenterOnScreen('imgs/auto_scan_option.png')
    scan_button = pag.locateCenterOnScreen('imgs\scan_option.png')

    if auto_scan_option:
        pag.moveTo(auto_scan_option)
        pag.click()
        print('sucessfully found auto scan option')

    if scan_button:
        # time.sleep(1)
        pag.moveTo(scan_button)
        pag.click()
        print('sucessfully found scan button')

def is_scanning():
    time.sleep(4)
    is_save_available = False
    save_button_grey = pag.locateCenterOnScreen('imgs\save_not_available.png')
    save_button_green = pag.locateCenterOnScreen('imgs\save_available.png')
    save_button = pag.locateCenterOnScreen('imgs\save_button.png')
    preparing = pag.locateCenterOnScreen('imgs\preparing.png')
    mouse_default = pag.locateCenterOnScreen('imgs\mouse_default.png')

    # rescaning = pag.locateCenterOnScreen('imgs/rescaning.png')

    pag.moveTo(mouse_default)

    while not is_save_available:
   
        if preparing:
            print('preparing...')

            preparing = pag.locateCenterOnScreen('imgs\preparing.png')

            time.sleep(4)
            is_save_available = False
        
        else:
            print('preparation complete')
            is_save_available = True

 
    if is_save_available:
        save_button = pag.locateCenterOnScreen('imgs\save_button.png')
        # 930 617

        if save_button:
            print('sucessfully found save button')
        else:
            print('could not find save button')

        time.sleep(2)
        pag.moveTo(930, 617)
        pag.click()
        print('waiting for preparation to complete')

        time.sleep(8)
 

    print('scanning with the correct resolution...')
    time.sleep(60 + 25)
    # print('scanning complete')

def done_scanning():
    done_img = pag.locateCenterOnScreen('imgs\done.png')
    if done_img:
        pag.moveTo(done_img)
        pag.click()
        print('sucessfully found done button')
    else:
        print('could not find done button')


def back_to_cmd():
    tskbar_cmd = True
    cmd_img = pag.locateCenterOnScreen('imgs\cmd.png')

    if tskbar_cmd:
        pag.moveTo(805, 741)
        pag.click()
        print('sucessfully found cmd in taskbar')

        if cmd_img:
            pag.moveTo(cmd_img)
            pag.click()
            print('sucessfully found cmd window')
        else:
            print('could not find cmd window')      

    else:
        print('could not find cmd in taskbar')