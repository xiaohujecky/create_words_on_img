# -*- encoding: utf-8 -*-
import os,sys,random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

prefix_path = 'result/verify_code_train_v8'
if not os.path.exists(prefix_path):
    os.popen("mkdir -p %s"%prefix_path)

#random.sample(string,num)从指定string中获取长度为num的随机字符
def random_str(str_type = 'eng+numb',length = 4):
    if str_type == 'eng':
        return ''.join(random.sample('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ',length))
    if str_type == 'numb':
        return ''.join(random.sample('0123456789',length))
    if str_type == 'eng+numb':
        return ''.join(random.sample('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789',length))

def random_col():  #颜色值
    pixel_high = random.randint(200,255)
    cols = ((255,255,0),(255,0,255),(0,255,255),(0,0,0),(255,0,0),(0,255,0),(0,0,255))
    return (random.randint(50,255),random.randint(50,255),random.randint(50,255))

def make_verify_code_type1( strs, width = 400, height = 200):
    print strs
    im = Image.new( 'RGB', (width, height ), (255,255,255))
    draw = ImageDraw.Draw(im)
    font = ImageFont.truetype('font/verify_code/verdana.ttf',width//4)  #//浮点数除法，结果四舍五入
    font_width , font_height = font.getsize(strs)
    print font_width, font_height
    strs_len = len(strs)
    print 'strs_len: ' + str(strs_len)
    x = (width - font_width) // 2
    y = (height - font_height ) //2
    print x, y
    total_dex = 0
    for i in strs:
        draw.text((x,y), i, random_col(), font)
        temp = random.randint(-20,20)
        total_dex += temp
        im = im.rotate(temp)  #旋转角度
        draw = ImageDraw.Draw(im)
        x += font_width/strs_len
    im = im.rotate(-total_dex)
    draw = ImageDraw.Draw(im)
    draw.line(   #下面三段代码用来画直线，参数分别是直线起始、终止位置，颜色以及宽度
        [(random.randint(0,width//4),
        random.randint(0,height//4)
        ),
        (random.randint(width//4*3,width),
        random.randint(height//4*3,height)
        )],
        fill = random_col(),
        width = width // 80
    )
    draw.line(
        [(random.randint(0,width//4),
            random.randint(height//4*3,height)
        ),
        (random.randint(width//3*2,width),
        random.randint(0,height//3)
        )],
        fill = random_col(),
        width = width // 80
    )
    draw.line(
        [(random.randint(width//4*3,width),
            random.randint(height//4*3,height)
        ),
        (random.randint(width//3*2,width),
        random.randint(0,height//3)
        )],
        fill = random_col(),
        width = width // 80
    )
    # im = im.crop((width//10,height//10,width,height))
    for x in range(width):
        for y in range(height):
            col = im.getpixel((x,y))  #获取坐标点像素的RGB值
            if col == (255,255,255) or col == (0,0,0):
                draw.point((x,y), fill = random_col())#将背景中的黑白两色重新随机涂色
    im = im.filter(ImageFilter.BLUR) #模糊效果
    # im.show()
    # im = im.convert('L')
    #im.save('out.jpg')
    return im

def make_verify_code_type2( strs, width = 400, height = 200):
    line_distorb = True 
    line_num = random.randint(3,6)
    noise_distorb = False
    blur_distorb = False
    print strs
    im = Image.new( 'RGB', (width, height ), (255,255,255))
    draw = ImageDraw.Draw(im)
    font = ImageFont.truetype('font/verify_code/verdana.ttf', int(2*height/3.0))  #//浮点数除法，结果四舍五入
    font_width , font_height = font.getsize(strs)
    print font_width, font_height
    strs_len = len(strs)
    print 'strs_len: ' + str(strs_len)
    x = random.randint(1, (width - font_width) // 4)
    y = (height - font_height ) //2
    print x, y
    total_dex = 0
    for i in strs:
        draw.text((x,y), i, random_col(), font)
        temp = random.randint(-5,5)
        total_dex += temp
        im = im.rotate(temp)  #旋转角度
        draw = ImageDraw.Draw(im)
        x += font_width/strs_len
        #x += width/strs_len
    im = im.rotate(-total_dex)
    draw = ImageDraw.Draw(im)
    #下面三段代码用来画直线，参数分别是直线起始、终止位置，颜色以及宽度
    if line_distorb :
        for _ in range(line_num):
            draw.line(   
                [(random.randint(0,width//2),
                random.randint(0,height)
                ),
                (random.randint(width//2,width),
                random.randint(0,height)
                )],
                fill = random_col(),
                width = int(min(height*0.1, 2))
            )
    # background
    for x in range(width):
        for y in range(height):
            col = im.getpixel((x,y))  #获取坐标点像素的RGB值
            if noise_distorb and (col == (255,255,255) or col == (0,0,0)):
                draw.point((x,y), fill = random_col()) #将背景中的黑白两色重新随机涂色
            elif col == (0,0,0):
                draw.point((x,y), fill = (255,255,255))

    # im = im.crop((width//10,height//10,width,height))
    if blur_distorb:
        im = im.filter(ImageFilter.BLUR) #模糊效果
    # im.show()
    # im = im.convert('L')
    #im.save('out.jpg')
    return im

if __name__ == '__main__':
    sam_num = 3000
    for a in range(sam_num):
        str_len = random.randint(4,8)
        str_seq = random_str('numb', 4)
        fname = "type1_{:>08}_{}.png".format(int(a),str_seq)
        img = make_verify_code_type2(str_seq, 240, 80)
        img.save(prefix_path + '/' + fname)
