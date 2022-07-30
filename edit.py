import os
from PIL import Image
from os import remove, walk
from time import sleep


def create_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)
        print('Directory "' + path + '" created')
    else:
        print('Directory "' + path + '" already exists')

def crop_imgs():
    create_dir('results/after_crop')

    for _,__,img_files in walk('results/before_crop'):
        for img_file in img_files:
            img = Image.open('results/before_crop/' + img_file)

            cropped_1 = img.crop((0, 0, 2552, 3508))
            print('saving ' + '__1__' + img_file)
            cropped_1.save('results/after_crop/' + '__1__' + img_file)

            cropped_2 = img.crop((2552, 0, 2548 + 2552, 3508))
            print('saving ' + '__2__' + img_file)
            cropped_2.save('results/after_crop/' + '__2__' + img_file)

            cropped_3 = img.crop((0, 3508, 2552, 3508 + 3506))
            print('saving ' + '__3__' + img_file)
            cropped_3.save('results/after_crop/' + '__3__' + img_file)

            cropped_4 = img.crop((2552, 3508, 2548 + 2552, 3508 + 3506))
            print('saving ' + '__4__' + img_file)
            cropped_4.save('results/after_crop/' + '__4__' + img_file)

crop_imgs()