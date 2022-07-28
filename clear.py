import os
import shutil

def clear_dir(dir_name, bkp=False):

    # copy all files in dir_name to a bkp folder
        

    for file_name in os.listdir(dir_name):

        if bkp:
            shutil.copy(dir_name + '/' + file_name, 'results/bkp/' + file_name)

        os.remove(dir_name + '/' + file_name)

    print('cleared directory: ' + dir_name)