# -*- encoding: utf-8 -*-
from PIL import Image,ImageDraw,ImageFont
import random
from path import Path
import os
import sys
import copy
import math
import codecs
import numpy as np
import cv2
reload(sys)  
sys.setdefaultencoding('utf8')
cur_pid=os.getpid()
print('current pid : {}'.format(cur_pid))


fonts_test=0
debug=0
save_detection_img=False
NUM_WORDS=200
bg_imgs_path='image.lst'
words_path='conf/words_new/words_encode.txt'
words_path='conf/words_new/words_encode_crnn_add_names.txt'
#words_img_path='result/textline_atribute_pildraw_trainv{}/'.format(sys.argv[1])
words_img_path='result/Chinese_driver_license_eng_trainv{}/'.format(sys.argv[1])
#words_img_path='/xiaohu.data/OCR/create_words_on_img_html/result/textline_fonts_show_v{}/'.format(sys.argv[1])
#fonts_path=Path('font/xuexin.bkp/')
#fonts_path=Path('font/chinese_simplified/')
#fonts_path=Path('font/driver_license_ch/')
fonts_path=Path('font/driver_license_eng_num/')
#fonts_path=Path('font/Indonesia/')
font_files=fonts_path.files()
font_sizes=[14,16,18,20,22,24,26,28,30,34]
words_map={}
words_label_map={}
words_total_num=0
bg_imgs_id = []
NUM_SAMPLES=100000
train_label=None

def init_global_variables():
    """
    Function:
        generate the image accroding to the given size.  
    Parameter:
        return : the image in numpy.
    """
    global words_map
    global words_label_map
    global words_total_num
    global train_label
    global bg_imgs_id 
    check_path(words_img_path)
    train_label = open(os.path.join(words_img_path, 'train_label.txt'), 'w')
    with open(words_path,'r') as f:
        lines=unicode(f.read(),'utf-8').split('\n')
        lines=lines[0:-1]
        for line in lines:
            print "{}".format(line)
            word,label=line.strip().split(u' ')
            if label in words_map and word !=words_map[label]:
                print "word label wrong: %s - %s"%(label,word)
                sys.exit(0)
            words_map[label]=word
            words_label_map[word]=label
            words_total_num += 1
    words_map[u' '] = u' '
    words_label_map[u' '] = u' '
    with open(bg_imgs_path, 'r') as f:
        bg_imgs_id = [line.strip() for line in f.readlines()]  
    #print bg_imgs_id
    print("Global variables init done! Total words : {}".format(len(words_map))) 

def check_path(a_path):
    if not os.path.exists(a_path):
        os.popen("mkdir -p %s"%a_path)

def gen_bg_img(height, width, r=255, g=255, b=255):
    """
    Function:
        generate the image accroding to the given size.  
    Parameter:
        return : the image in numpy.
    """
    img = np.ones((height, width, 3), np.uint8)
    #color = tuple(reversed((b,g,r)))
    # black background
    #b=g=r=random.randint(0,50)
    # wihte background
    #b=g=r=random.randint(200,255)
    val = random.randint(random.randint(0,127),255)
    img = img*val
    return img, val 

bgimg_idx = 0
def gen_bg_img_from_file(height, width):
    """
    Function:
        generate the image accroding to the given size.  
    Parameter:
        return : the image in numpy.
    """
    global bgimg_idx
    global bg_imgs_id
    bg_img_crop = None
    while bg_img_crop is None:
        if not bgimg_idx < len(bg_imgs_id):
            bgimg_idx = 0
        bg_img_name = bg_imgs_id[bgimg_idx]
        bg_img = cv2.imread(bg_img_name)
        bgimg_idx += 1
        if bg_img is not None:
            bg_img_h, bg_img_w = bg_img.shape[:2] 
            # 水平镜像
            bg_img_flip_v = bg_img[:,::-1] 
            bg_img_extend = bg_img[:]
            flip_idx = 0
            while bg_img_w <= width :
                if flip_idx % 2 == 0:
                    bg_img_extend = np.concatenate((bg_img_extend, bg_img_flip_v), axis=1)
                else:
                    bg_img_extend = np.concatenate((bg_img_extend, bg_img), axis=1)
                flip_idx += 1
                bg_img_h, bg_img_w = bg_img_extend.shape[:2] 
            
            # 竖直镜像
            bg_img_flip_h = bg_img_extend[::-1,:] 
            bg_img_extend2 = bg_img_extend[:]
            flip_idx = 0
            while bg_img_h <= height :
                if flip_idx % 2 == 0:
                    bg_img_extend2 = np.concatenate((bg_img_extend2, bg_img_flip_h), axis=0)
                else:
                    bg_img_extend2 = np.concatenate((bg_img_extend2, bg_img_extend), axis=0)
                flip_idx += 1
                bg_img_h, bg_img_w = bg_img_extend2.shape[:2] 

            bg_img = bg_img_extend2
            bg_img_h, bg_img_w = bg_img.shape[:2] 
            if bg_img_h > height and bg_img_w > width :
                y_max = bg_img_h - height 
                x_max = bg_img_w - width
                y = random.randint(0, y_max-1)
                x = random.randint(0, x_max-1)
                bg_img_crop = bg_img[ y:y+height, x:x+width, :]
                bg_pixel_value = int(np.mean(bg_img_crop)) 
                #bg_name_split = bg_img_name.split('/')[-1].split('_')
                #if len(bg_name_split) > 0 and bg_name_split[0] == 'CreatedPureImg20180517':
                #    bg_pixel_value = int(bg_name_split[1].split('.')[0])
    return bg_img_crop, bg_pixel_value

cimg_idx = 0
def put_text_on_img(text=''):
    """
    Function:
        put the text on a image that generate accroding to the text size.  
    Parameter:
        text : the specify text.
    """
    global cimg_idx
    text_len = len(text)
    font_size = random.choice(font_sizes)
    #font_file = random.choice(font_files)
    
    # to see the fonts effects
    if cimg_idx >= len(font_files):
        cimg_idx = 0
    font_file = font_files[cimg_idx]
    cimg_idx += 1

    font = ImageFont.truetype(font_file, font_size)
    img, bg_pixel_val = gen_bg_img(font_size*2, (text_len+2)*font_size)
    img=Image.fromarray(np.uint8(img))
    draw=ImageDraw.Draw(img)
    
    text_h = font_size
    text_w = text_h*text_len
    try :
        text_w, text_h = draw.textsize(text, font)
    except :
        print "Font : {} may not work.".format(font_file)
        font_file = random.choice(font_files)
        font = ImageFont.truetype(font_file, font_size)
        text_w, text_h = draw.textsize(text, font)
    w_extend = min(int(text_w*0.2), 32)
    w_border = int(w_extend/2.0)
    h_border = int(text_h/2.0)
    #print('border : w {} h {}'.format(w_border, h_border)) 
    if random.randint(1,2) == 1:
        img, bg_pixel_val = gen_bg_img(text_h*2, text_w + w_extend)
    else:
        img, bg_pixel_val = gen_bg_img_from_file(text_h*2, text_w + w_extend)
    img=Image.fromarray(np.uint8(img))
    loc=(random.randint(0, max(w_border*2 - 1, 1)), random.randint(0, max(h_border*2 - 1, 1)))
    draw=ImageDraw.Draw(img)
    # black text
    rgb = random.randint(0, random.randint(127, 255))
    while math.fabs(rgb - bg_pixel_val) < 50 :
        if bg_pixel_val < 127:
            rgb=random.randint(bg_pixel_val+51, 255)
        else:
            rgb=random.randint(0, bg_pixel_val - 51)
    # wihte text
    #rgb=random.randint(150,255)
    draw.text(loc, text, (rgb, rgb, rgb), font=font)
    
    return img,font_file

def put_text_on_img_cv(text=''):
    """
    Function:
        put the text on a image that generate accroding to the text size.  
    Parameter:
        text : the specify text.
    """
    text_len = len(text)
    font_size = random.choice(font_sizes)
    font=cv2.cv.InitFont(cv.CV_FONT_HERSHEY_SCRIPT_SIMPLEX, 1, 1, 0, 3, 8)
    img = gen_bg_img(font_size*2, text_len*font_size*2)
    img=Image.fromarray(np.uint8(img))
    draw=ImageDraw.Draw(img)
    
    text_w, text_h = draw.textsize(text, font)
    w_border = int(text_h/2.0)
    h_border = int(text_w/(float(text_len)*2))
    #print('border : w {} h {}'.format(w_border, h_border)) 
    img=gen_bg_img(text_h + 2*h_border, text_w + 2*w_border)
    img=Image.fromarray(np.uint8(img))
    loc=(random.randint(1, w_border*2-1), random.randint(1, h_border*2-1))
    draw=ImageDraw.Draw(img)
    rgb=random.randint(0,150)
    draw.text(loc, text, (rgb, rgb, rgb), font=font)
    
    return img

font_mask={}
def put_mask_indonesia_nums_on_img(text=''):
    global font_mask
    font_sizes=[16,18,20,22,25,28,30,32,34]
    nums = [unicode(str(na), 'utf-8') for na in range(10)]

    words_inter_offset = 1
    font_width=random.choice(font_sizes)
    font_height = int(font_width*35/25.0)
    font_len = len(text)*(font_width + words_inter_offset)

    text_img_w = font_len + random.randint(0, font_width*2)
    text_img_h = font_height + random.randint(0, font_height)
    img = gen_bg_img_from_file(text_img_h, text_img_w)

    text_start = (random.randint(0, text_img_w - font_len), 
            random.randint(0, text_img_h - font_height)) 
    idx_x = text_start[0]
    idx_y = text_start[1]
    set_color = random.randint(0,100)
    for w in text:
        if w == u' ':
            idx_x += font_width + words_inter_offset
            continue
        elif w not in nums:
            print("{} is not a number!".format(w))
            raise ValueError

        if w not in font_mask:
            mask = cv2.imread('Indonesia_font_mask/{}_bin.jpg'.format(w))
            font_mask[w]=mask
        mask_ = font_mask[w]
        mask_ = cv2.resize(mask_, (font_width, font_height))
        mask_idx = np.where(mask_ < 127)
        dst = img[idx_y:idx_y + font_height, idx_x:idx_x + font_width, :]
        dst[mask_idx] = set_color 
        img[idx_y:idx_y + font_height, idx_x:idx_x + font_width, :] = dst
        idx_x += font_width + words_inter_offset
    #img = cv2.GaussianBlur(img,(3,3),0)
    return img

def save_img_label(cstr, save_path, itm_name, gen_idx):
    """
    Function:
        to generate a proper image hold the textline.  
    Parameter:
        cstr : the textline to put on image.
        save_path : location of the image to save.
        itm_name : the iterm of the image.
        gen_idx : index of current image.
    """
    global train_label
    sample_name = '{}_{:0>9}'.format(itm_name, gen_idx)
    img_name = sample_name + '.png'
    label_name = sample_name + '.txt'
    img,font = put_text_on_img(cstr)
    #img = put_mask_indonesia_nums_on_img(cstr)
    img = np.asarray(img)
    # to see the fonts
    #cv2.imwrite(os.path.join(save_path, font.split('/')[-1] + cstr.replace(' ', '_').encode('utf-8') + "_" + img_name), img)
    #print('text-- {}, len-- {}'.format(cstr.encode('utf-8'), len(cstr)))
    #return

    cv2.imwrite(os.path.join(save_path, img_name), img)
    if False: #DEPRECATED: train label format:img_file label_file
        with open(os.path.join(save_path, label_name), 'w') as flabel:
            label = ''
            for w in cstr:
                if w == ' ':
                    continue
                if w not in words_label_map:
                    print('Warning : Not found {}!'.format(w.encode('utf-8')))
                    #raise KeyError('Not found key {}'.format(w.encode('utf-8')))
                #label += '{},'.format(words_label_map[w])
            #flabel.write('{};{};\n'.format(label, cstr.encode('utf-8')))
            #flabel.write('{} {}'.format(cstr.encode('utf-8'), font))
            flabel.write('{}'.format(cstr.encode('utf-8')))
        train_label.write('{} {}\n'.format(os.path.join(save_path, img_name), os.path.join(save_path, label_name)))
    train_label.write('{} {}\n'.format(os.path.join(save_path, img_name), cstr.encode('utf-8')))
    #print('text-- {}, len-- {}, label-- {}'.format(cstr.encode('utf-8'), len(cstr), label))
    print('text-- {}, len-- {}'.format(cstr.encode('utf-8'), len(cstr)))


def save_img_label_from_mask(cstr, save_path, itm_name, gen_idx):
    """
    Function:
        to generate a proper image hold the textline.  
    Parameter:
        cstr : the textline to put on image.
        save_path : location of the image to save.
        itm_name : the iterm of the image.
        gen_idx : index of current image.
    """
    global train_label
    sample_name = '{}_{:0>9}'.format(itm_name, gen_idx)
    img_name = sample_name + '.png'
    label_name = sample_name + '.txt'
    img = put_mask_indonesia_nums_on_img(cstr)
    img = np.asarray(img)

    cv2.imwrite(os.path.join(save_path, img_name), img)
    train_label.write('{} {}\n'.format(os.path.join(save_path, img_name), cstr.encode('utf-8')))
    print('text-- {}, len-- {}'.format(cstr.encode('utf-8'), len(cstr)))

def index_to_words(idx):
    cstr = ''
    for dd in idx:
        i_key = u'{}'.format(dd)
        if i_key in words_map:
            cstr += words_map[i_key]
        else:
            raise "key {} not in words_map!".format(i_key)
    return cstr

def gen_Indonesia_nik(fix_str, itm_name, length=[2,3], num=NUM_SAMPLES):
    """
    Function:
        generate 姓名 ：xxx 
    Parameter:
        fix_str : title '姓名' 
        itm_name : the iterm of the image.
        length : length of the text line. 
        num : samples to generate.
    Remark : famil name in words_map index is [92, 586] closed range.
    """
    def text_seq_gen(num, length):
        global words_total_num
        #second_name_idx = [na for na in range(92, words_total_num)]
        second_name_idx = []
        for _ in range(num):
            second_name_idx = [na for na in range(words_total_num)]

            numbers_char = random.randint(1,1)
            length = [i for i in range(4,19)]
            if (numbers_char == 1):
                second_name_idx = [na for na in range(10)]
            elif (numbers_char == 2):
                second_name_idx = [na for na in range(10,37)]
            elif (numbers_char == 3):
                second_name_idx = [na for na in range(10,62)]
            elif (numbers_char == 4):
                second_name_idx = [na for na in range(37,62)]
            elif (numbers_char == 5):
                second_name_idx = [na for na in range(91)]

            random.shuffle(second_name_idx)
            #yield random.sample(second_name_idx, random.choice(length))
            #yield [random.choice(second_name_idx) for _ in range(random.choice(length))]
            cstr_id = []
            cstr_len = random.choice(length)
            space_mark = False
            sword_len = 0
            if random.randint(1,5) == 1 :
                space_mark = True
            for idx in range(cstr_len):
                cstr_id.append(random.choice(second_name_idx))
                sword_len += 1
                p_prob = random.choice([ll for ll in range(1, max(2, 20 - sword_len))])
                if idx > 2 and idx < cstr_len - 2 and random.randint(1, p_prob) == 1 and space_mark:
                    cstr_id.append(u' ')
                    space_mark = not space_mark
                    sword_len = 0
            yield cstr_id

    num = num
    length=[16,16,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,16,16,16,16,16,16]
    random.shuffle(length)
    gen_idx=0
    save_path=os.path.join(words_img_path, itm_name)
    check_path(save_path)
    for sna in text_seq_gen(num, length):
        #cstr=fix_str
        #cstr += ' : '
        cstr = ''
        cstr += index_to_words(sna)
        
        save_img_label_from_mask(cstr, save_path, itm_name, gen_idx)
        #save_screenshot_label('', cstr, save_path, itm_name, gen_idx)
        gen_idx += 1

def gen_Indonesia_nik_from_file(fix_str, itm_name, length=[2,3], num=NUM_SAMPLES):
    """
    Function:
        generate specify iterms in the file. 
    Remark :  
    """
    print("generating {}".format(itm_name))
    specify_itm_file = "Indonesia_words/Indonisa_idcode.txt"
    def itms_gen(num):
        with open(specify_itm_file, 'r') as f:
            lines=unicode(f.read(),'utf-8').split('\n')
            lines=lines[0:-1]
            random.shuffle(lines)
            for _ in range(num):
                yield random.choice(lines) 
    gen_idx=0
    save_path=os.path.join(words_img_path, itm_name)
    check_path(save_path)
    for school in itms_gen(num):
        #cstr=fix_str
        cstr = u''
        cstr += school 
        
        save_img_label_from_mask(cstr, save_path, itm_name, gen_idx)
        gen_idx += 1

def gen_Indonesia_nama_from_file(fix_str, itm_name, length=[2,3], num=NUM_SAMPLES):
    """
    Function:
        generate specify iterms in the file. 
    Remark :  
    """
    print("generating {}".format(itm_name))
    specify_itm_file = "Indonesia_words/cat_names.txt"
    #specify_itm_file = "Indonesia_words/names_real.txt"
    def itms_gen(num):
        with open(specify_itm_file, 'r') as f:
            lines=unicode(f.read(),'utf-8').split('\n')
            lines=lines[0:-1]
            random.shuffle(lines)
            for _ in range(num):
                yield random.choice(lines)
    gen_idx=0
    save_path=os.path.join(words_img_path, itm_name)
    check_path(save_path)
    for school in itms_gen(num):
        #cstr=fix_str
        cstr = u''
        cstr += school.upper() 
        
        save_img_label(cstr, save_path, itm_name, gen_idx)
        gen_idx += 1


def gen_nlp_words_from_file(fix_str, itm_name, length=[2,3], num=NUM_SAMPLES):
    """
    Function:
        generate specify iterms in the file. 
    Remark :  
    """
    print("generating {}".format(itm_name))
    #specify_itm_file = "chinese_text/lex.txt"
    #specify_itm_file = "chinese_text/driver_text/driver_license.txt"
    specify_itm_file = "chinese_text/driver_text/driver_license_eng_num.txt"
    #specify_itm_file = "Indonesia_words/names_real.txt"
    def itms_gen(num):
        with open(specify_itm_file, 'r') as f:
            lines=unicode(f.read(),'utf-8').split('\n')
            lines=lines[0:-1]
            random.shuffle(lines)
            for _ in range(num):
                yield random.choice(lines)
    gen_idx=0
    save_path=os.path.join(words_img_path, itm_name)
    check_path(save_path)
    for school in itms_gen(num):
        #cstr=fix_str
        cstr = u''
        cstr += school.upper() 
        
        save_img_label(cstr, save_path, itm_name, gen_idx)
        gen_idx += 1


def gen_atribuate_words(fix_str, itm_name, length=[2,3], num=NUM_SAMPLES):
    """
    Function:
        generate 姓名 ：xxx 
    Parameter:
        fix_str : title '姓名' 
        itm_name : the iterm of the image.
        length : length of the text line. 
        num : samples to generate.
    Remark : famil name in words_map index is [92, 586] closed range.
    """
    def text_seq_gen(num, length):
        global words_total_num
        #second_name_idx = [na for na in range(92, words_total_num)]
        second_name_idx = []
        for _ in range(num):
            second_name_idx = [na for na in range(words_total_num)]

            numbers_char = random.randint(0,41)
            #length = [i for i in range(4,19)]
            if (numbers_char <= 1):
                # 0-9 numbers
                second_name_idx = [na for na in range(10)]
            elif (numbers_char == 2):
                # Uppercase A-Z
                second_name_idx = [na for na in range(10,36)]
            elif (numbers_char == 3):
                second_name_idx = [na for na in range(10,62)]
            elif (numbers_char == 4):
                # lowercase a-z
                second_name_idx = [na for na in range(37,62)]
            elif (numbers_char == 5):
                # other comma like sign
                second_name_idx = [na for na in range(91)]

            random.shuffle(second_name_idx)
            #yield random.sample(second_name_idx, random.choice(length))
            #yield [random.choice(second_name_idx) for _ in range(random.choice(length))]
            cstr_id = []
            cstr_len = random.choice(length)
            space_mark = True
            sword_len = 0
            for idx in range(cstr_len):
                cstr_id.append(random.choice(second_name_idx))
                sword_len += 1
                p_prob = random.choice([ll for ll in range(1, max(2, 20 - sword_len))])
                if idx > 2 and idx < cstr_len - 2 and random.randint(1, p_prob) == 1 and space_mark:
                    cstr_id.append(u' ')
                    sword_len = 0
                space_mark = not space_mark
            yield cstr_id


    num = num
    length=[4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29]
    random.shuffle(length)
    gen_idx=0
    save_path=os.path.join(words_img_path, itm_name)
    check_path(save_path)
    for sna in text_seq_gen(num, length):
        #cstr=fix_str
        #cstr += ' : '
        cstr = ''
        cstr += index_to_words(sna)
        
        save_img_label(cstr, save_path, itm_name, gen_idx)
        #save_screenshot_label('', cstr, save_path, itm_name, gen_idx)
        gen_idx += 1

def gen_p_name(fix_str, itm_name, length=[2,3], num=NUM_SAMPLES):
    """
    Function:
        generate 姓名 ：xxx 
    Parameter:
        fix_str : title '姓名' 
        itm_name : the iterm of the image.
        length : length of the text line. 
        num : samples to generate.
    Remark : famil name in words_map index is [92, 586] closed range.
    """
    def family_name_gen(num, length):
        global words_total_num
        second_name_idx = [na for na in range(92, words_total_num)]
        for _ in range(num):
            random.shuffle(second_name_idx)
            yield random.randint(92, 586), \
                    random.sample(second_name_idx, random.choice(length))
    num = 100*num
    length=[1,1,1,1,1,\
            2,2,2,2,2,2,2,2,2,2,2,\
            3,4,5,6,7,8]
    random.shuffle(length)
    gen_idx=0
    save_path=os.path.join(words_img_path, itm_name)
    check_path(save_path)
    for fna,sna in family_name_gen(num, length):
        cstr=fix_str
        cstr += ' : '
        cstr += index_to_words([fna])
        cstr += index_to_words(sna)
        
        save_img_label(cstr, save_path, itm_name, gen_idx)
        gen_idx += 1

def gen_p_name_from_list(fix_str, itm_name, length=[2,3], num=NUM_SAMPLES):
    """
    Function:
        generate 姓名 : xxx from a file
    """
    name_flist='conf/words_new/p_names.txt'
    def family_name_gen(num):
        with open(name_flist, 'r') as f:
            lines=unicode(f.read(),'utf-8').split('\n')
            lines=lines[0:-1]
            random.shuffle(lines)
            for _ in range(num):
                yield random.randint(92,586), random.choice(lines)[1:]
    num = 2*num
    gen_idx=0
    save_path=os.path.join(words_img_path, itm_name)
    check_path(save_path)
    for fna,sna in family_name_gen(num):
        cstr=fix_str
        cstr += ' : '
        cstr += index_to_words([fna])
        cstr += (sna)
        
        save_img_label(cstr, save_path, itm_name, gen_idx)
        gen_idx += 1

def gen_p_name_from_html(fix_str, itm_name, length=[2,3], num=NUM_SAMPLES):
    """
    Function:
        generate 姓名 : xxx from a file
    """
    name_flist='conf/words_new/p_names.txt'
    def family_name_gen(num):
        with open(name_flist, 'r') as f:
            lines=unicode(f.read(),'utf-8').split('\n')
            lines=lines[0:-1]
            random.shuffle(lines)
            for _ in range(num):
                yield random.randint(92,586), random.choice(lines)[1:]
    num = 30*num
    gen_idx=0
    save_path=os.path.join(words_img_path, itm_name)
    check_path(save_path)
    for fna,sna in family_name_gen(num):
        cstr = u''
        cstr += index_to_words([fna])
        cstr += (sna)
        
        save_screenshot_label(fix_str + u' : ', cstr, save_path, itm_name, gen_idx)
        gen_idx += 1


def gen_p_gender(fix_str, itm_name, length=[2,3], num=NUM_SAMPLES):
    """
    Function:
        generate 性别 ： 男／女
    Remark : gender index in words_map : [男-2287, 女- 2339]
    """
    def gender_gen(num):
        for _ in range(num):
            yield random.choice([2287, 2339]) 
    num = num/5
    gen_idx=0
    save_path=os.path.join(words_img_path, itm_name)
    check_path(save_path)
    for gender in gender_gen(num):
        #cstr=fix_str
        #cstr += ' : '
        cstr = u''
        cstr += index_to_words([gender])
        
        #save_img_label(cstr, save_path, itm_name, gen_idx)
        save_screenshot_label(fix_str + u' : ', cstr, save_path, itm_name, gen_idx)
        gen_idx += 1


def gen_specify_itm(fix_str, itm_name, specify_itm_file=None, length=[2,3], num=NUM_SAMPLES):
    """
    Function:
        generate specify iterms in the file. 
    Remark :  
    """
    print("generating {}".format(itm_name))
    def itms_gen(num):
        with open(specify_itm_file, 'r') as f:
            lines=unicode(f.read(),'utf-8').split('\n')
            lines=lines[0:-1]
            random.shuffle(lines)
            for _ in range(num):
                yield random.choice(lines) 
    gen_idx=0
    save_path=os.path.join(words_img_path, itm_name)
    check_path(save_path)
    for school in itms_gen(num):
        #cstr=fix_str
        cstr = u''
        cstr += school 
        
        #save_img_label(cstr, save_path, itm_name, gen_idx)
        save_screenshot_label(fix_str + u' : ', cstr, save_path, itm_name, gen_idx)
        gen_idx += 1




if __name__ == "__main__":
    global train_label 
    init_global_variables() 
    crop_str={
            'atrib' : [gen_atribuate_words, 'atribuate_words'], 'nlp' : [gen_nlp_words_from_file, 'nlp_words'], \
                    'nik' : [gen_Indonesia_nik_from_file, 'Indonesia_NIK'], \
            'Nama' : [gen_Indonesia_nama_from_file, 'Indonesia_Nama']}
    #for itm in crop_str:
    #    print(itm)
    #    crop_str[itm][0](itm, crop_str[itm][1])
    itm='nlp'
    crop_str[itm][0](itm, crop_str[itm][1])
    train_label.close()

