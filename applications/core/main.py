import cv2
import os
from applications.classification import Classification
from PIL import Image

def compress_images(infile,outfile,mb=350,step=10, quality=60):
    image_size = os.path.getsize(infile)/1024
    im = Image.open(infile)
    if image_size <= mb:
        return im.save(outfile)
    while image_size > mb:
        im.save(outfile, quality=quality)
        if quality - step < 0:
            break
        quality -= step
        image_size = os.path.getsize(outfile)/1024
    im.thumbnail((400, 400))  # Adjust your size

def predict(dataset, model, ext, age):

    global img_y

    CLS = Classification()

    x = dataset[0].replace('\\', '/')#static/upload/xxx.png
    file_name = dataset[1]# file_name_0

    step1_img = Image.open(x)
    # step2_img = np.array(step1_img)
    step2_img = cv2.imread(x)

    if CLS.detect_image(step1_img):
        img_y, image_info = model.detect(step2_img,age)
        
    else:
        img_y, image_info = model.out(step2_img)

    cv2.imwrite('./static/tmp/draw/{}.{}'.format(file_name, ext), img_y)
        #raise Exception('保存图片时出错.Error saving thepicture.')

    filename = '{}.{}'.format(file_name, ext)
    infile = os.path.join('./static/tmp/draw/', filename)
    outfile = './static/tmp/comp/{}'.format(filename)

    compress_images(infile, outfile)

    return image_info

def pre_process(data_path):
    file_name_0 = os.path.split(data_path)[1].split('.')[0]
    return data_path, file_name_0

def c_main(path, model, ext, age):
    image_data = pre_process(path)
    image_info = predict(image_data, model, ext, age)
    
    return image_data[1] + '.' + ext, image_info


if __name__ == '__main__':
    pass
