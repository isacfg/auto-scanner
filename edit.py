from PIL import Image
from os import walk



def crop_imgs():

    for _,__,img_files in walk('results/before_crop'):
        for img_file in img_files:
            img = Image.open('results/before_crop/' + img_file)
            cropped_1 = img.crop((0, 0, 2552, 3508))
            cropped_2 = img.crop((2552, 0, 2548 + 2552, 3508))
            cropped_3 = img.crop((0, 3508, 2552, 3508 + 3506))
            cropped_4 = img.crop((2552, 3508, 2548 + 2552, 3508 + 3506))
            cropped_1.save('results/after_crop/' + '__1__' + img_file)
            cropped_2.save('results/after_crop/' + '__2__' + img_file)
            cropped_3.save('results/after_crop/' + '__3__' + img_file)
            cropped_4.save('results/after_crop/' + '__4__' + img_file)

crop_imgs()