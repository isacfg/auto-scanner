import pyautogui as pag
import time


def open_scanner():
   
    scanner_icon = pag.locateCenterOnScreen('imgs\scanner_icon.png', confidence=0.8)
    if scanner_icon:
        pag.moveTo(scanner_icon)
        pag.doubleClick()
        print('sucessfully found scanner icon')

def scan_dialog():
    scanner_dialog = pag.locateCenterOnScreen('imgs\scanner_dialog.png')

    while scanner_dialog == None:
        print('trying to find scanner dialog')
        time.sleep(1)
        scanner_dialog = pag.locateCenterOnScreen('imgs\scanner_dialog.png', confidence=0.8)


    if scanner_dialog:
        pag.moveTo(scanner_dialog)
        pag.click()
        print('sucessfully found scanner dialog')


def scan_settings():
    auto_scan_option = pag.locateCenterOnScreen('imgs/auto_scanner.png')

    while auto_scan_option == None:
        print('trying to find auto scan option')
        time.sleep(1)
        auto_scan_option = pag.locateCenterOnScreen('imgs/auto_scanner.png', confidence=0.8)

    if auto_scan_option:
        pag.moveTo(auto_scan_option)
        pag.click()
        print('sucessfully found auto scan option')

        scan_button = pag.locateCenterOnScreen('imgs\scan_button.png', confidence=0.7)

        while scan_button == None:
            print('trying to find scan button')
            time.sleep(1)
            scan_button = pag.locateCenterOnScreen('imgs\scan_button.png', confidence=0.7)
        
        if scan_button:
            pag.moveTo(scan_button)
            pag.click()
            print('sucessfully found scan button')
    
def is_scanning():
    time.sleep(1)
    preparing_scan = pag.locateCenterOnScreen('imgs\preparing_scan.png', confidence=0.6)

    while preparing_scan:
        print('preparing scan')
        time.sleep(1)
        preparing_scan = pag.locateCenterOnScreen('imgs\preparing_scan.png', confidence=0.6)

        if preparing_scan == None:
            print('done preparing scan')
            break

    time.sleep(3)
    default_mouse_pos = pag.locateCenterOnScreen('imgs\default_mouse.png', confidence=0.8)
    pag.moveTo(default_mouse_pos)

    save_button = pag.locateCenterOnScreen('imgs\save_button.png', confidence=0.8)
    if save_button:
        pag.moveTo(save_button)
        pag.click()
        print('sucessfully found save button')
    else:
        print('could not find save button')

    preparing_scan_2 = pag.locateCenterOnScreen('imgs\preparing_scan.png', confidence=0.6)
    scanning = pag.locateCenterOnScreen('imgs\scanning.png', confidence=0.6)

    while preparing_scan_2 or scanning:
        print('scanning')
        time.sleep(2)
        preparing_scan_2 = pag.locateCenterOnScreen('imgs\preparing_scan.png', confidence=0.6)
        scanning = pag.locateCenterOnScreen('imgs\scanning.png', confidence=0.6)

        if preparing_scan_2 == None and scanning == None:
            print('done scanning')
            break

    time.sleep(3)


def done_scanning():
    done_img = pag.locateCenterOnScreen('imgs\done.png', confidence=0.8)

    while done_img == None:
        print('trying to find done img')
        time.sleep(1)
        done_img = pag.locateCenterOnScreen('imgs\done.png', confidence=0.6)

    if done_img:
        pag.moveTo(done_img)
        pag.click()
        print('sucessfully found done img')


def back_to_cmd():
    cmd_img = pag.locateCenterOnScreen('imgs\cmd.png', confidence=0.6)

    while cmd_img == None:
        print('trying to find cmd img')
        time.sleep(1)
        cmd_img = pag.locateCenterOnScreen('imgs\cmd.png', confidence=0.5)

    if cmd_img:
        pag.moveTo(cmd_img)
        pag.click()
        print('sucessfully found cmd img')
