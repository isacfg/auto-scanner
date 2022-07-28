from PIL import Image
from os import remove, walk
from time import sleep



def crop_imgs():

    for _,__,img_files in walk('results/before_crop'):
        for img_file in img_files:
            img = Image.open('results/before_crop/' + img_file)
            cropped_1 = img.crop((0, 0, 2552, 3508))
            cropped_1.save('results/after_crop/' + '__1__' + img_file)
            print('cropped first image')
            sleep(1)

            cropped_2 = img.crop((2552, 0, 5094, 3508))
            cropped_2.save('results/after_crop/' + '__2__' + img_file)
            print('cropped second image')
            sleep(1)

            cropped_3 = img.crop((5094, 0, 7636, 3508))
            cropped_3.save('results/after_crop/' + '__3__' + img_file)
            print('cropped third image')
        
            sleep(1)

            cropped_4 = img.crop((7636, 0, 10178, 3508))
            cropped_4.save('results/after_crop/' + '__4__' + img_file)
            print('cropped fourth image')
            sleep(1)

        sleep(2)

