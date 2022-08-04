from notifypy import Notify

nfc = Notify()


nfc.title = 'Finished Scanning'
nfc.message = 'proceed to next step'
nfc.application_name = 'AutoScan'
nfc.icon = 'icon_48.png'
nfc.audio = 'apple_sucess_sfx.wav'
nfc.send()