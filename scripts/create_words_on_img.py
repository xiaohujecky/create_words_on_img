# -*- encoding: utf-8 -*-

from PIL import Image,ImageDraw,ImageFont
import random
from path import Path
import os
import sys
import copy
import math
import codecs

fonts_test=0
debug=0
NUM_WORDS=100
bg_imgs_path='image.txt'
bg_imgs_path='/data/xiaohu/data/train/classify_words/wenziguanggao/bg_img.txt'
words_path='conf/words_all.txt'
words_img_path='result/v3_multi_words_cls/'
single_words_img_path=words_img_path + 'words_classify/'

def text_on_img(img_name,text,font_file,font_sizes,colors):
    img=Image.open(img_name)
    width=img.size[0]
    height=img.size[1]
   
    # get random settings.
    font_size=random.choice(font_sizes)
    
    if width < 2*font_size or height < 2*font_size :
        return [0,0,0,0],img
    color=colors[random.randint(0,len(colors)-1)]
    loc=(random.randint(0,width-font_size-1),\
            random.randint(0,height-font_size-1))

    font=ImageFont.truetype(font_file,font_size)
    draw=ImageDraw.Draw(img)

    # we can choose different colors if needed.
    #color=img.getpixel((x,y))

    if fonts_test:
        draw.text((width/2,height/2),text,color,font=font)
        draw.text((1,1),font_file.split(u'/')[-1],color,font=font)
    else:
        draw.text(loc,text,color,font=font)

    bbox=[loc[0],loc[1],int(loc[0])+font_size,int(loc[1])+font_size]
    return bbox,img

def multi_text_on_img(img_name,text_id,texts,font_file,font_sizes,colors):
    img=Image.open(img_name)
    width=img.size[0]
    height=img.size[1]
    
    # get random settings.
    font_size=random.choice(font_sizes)
    if width < 2*font_size or height < 2*font_size :
        return [[0,0,0,0]],img
    max_num_words_w = width / (font_size*2) 
    max_num_words_h = height / (font_size*2) 
    color_idx=random.randint(0,len(colors)-1)
    font=ImageFont.truetype(font_file,font_size)
    draw=ImageDraw.Draw(img)
    
    h_list=range(1,height-font_size-1,random.randint(font_size,2*font_size))
    h_loc=random.sample(h_list, random.randint(1,min(5,len(h_list))))
    if len(h_loc) <= 0:
        h_loc=[random.randint(0,height-font_size-1)]
   
    bboxes=[]
    word_id = text_id
    for h in h_loc:
        w_list=range(1,width-font_size-1,random.randint(font_size,3*font_size))
        w_loc=random.sample(w_list, random.randint(len(w_list)/2,len(w_list)))
        if len(w_loc) <= 0:
            w_loc=[random.randint(0,width-font_size-1)]
        for w in w_loc:
            loc=(w,h)
            img_color=img.getpixel(loc)
            color=colors[color_idx]
            if (math.fabs(color[0]-img_color[0]) + \
                    math.fabs(color[0]-img_color[0]) + \
                    math.fabs(color[0]-img_color[0])) < 20:
                color_idx += 1
            if (color_idx >= len(colors)):
                color_idx=0
            color=colors[color_idx]
            text=texts[word_id]
            draw.text(loc,text,color,font=font)
            bboxes.append([loc[0],\
                    loc[1],\
                    int(loc[0])+font_size,\
                    int(loc[1])+font_size,\
                    text.encode('utf-8')],\
                    word_id)
            word_id=random.choice(texts.keys())
    return bboxes,img

def create_word_cls_data(img, bbox, words_num, cls_label_file, crop_offset=5):
    word_id=bbox[5]
    word_path=single_words_img_path + '/{}/'.format(word_id)
    check_path(word_path)
    word_fname=word_path + '{}_{}.png'.format(word_id,words_num)
   
    xmin=bbox[0] + random.choice(xrange(-crop_offset,crop_offset+1))
    ymin=bbox[1] + random.choice(xrange(-crop_offset,crop_offset+1))
    xmax=bbox[2] + random.choice(xrange(-crop_offset,crop_offset+1))
    ymax=bbox[3] + random.choice(xrange(-crop_offset,crop_offset+1))
    xmin = max(1,xmin)
    ymin = max(1,ymin)
    xmax = min(img.size[0]-1, xmax)
    ymax = min(img.size[1]-1, ymax)
    crop_size=(xmin,ymin,xmax,ymax)

    img.crop(crop_size)
    img.save(word_fname,'JPEG')
    
    cls_label_file.write('%s %d\n'%(word_fname,word_id))
    return 

def check_path(a_path):
    if not os.path.exists(a_path):
        os.popen("mkdir -p %s"%a_path)

if __name__ == "__main__":
    if not os.path.exists(words_img_path):
        os.popen("mkdir -p %s"%words_img_path)
    if os.path.isdir(bg_imgs_path):
        img_path=Path(bg_imgs_path)
        imgs=img_path.files()
    elif os.path.isfile(bg_imgs_path):
        with open(bg_imgs_path,'r') as f:
            imgs=f.readlines()
    # we can also get files is way.
    #imgs=[f for f in os.listdir(words_img_path) if os.path.isfile(os.path.join(words_img_path,f))]

    fonts_path=Path('fonts/')
    label_file='word_label.txt'
    # 'classification' for different label of words
    # 'detection' for label 1 for all words 
    label_type='detection' 
    label_type='classification' 
    
    words={}
    with open(words_path,'r') as f:
        lines=unicode(f.read(),'utf-8').split('\n')
        lines=lines[0:-1]
        for line in lines:
            label,word=line.strip().split(u' ')
            if label in words and word !=words[label]:
                print "word label wrong: %s - %s"%(label,word)
                sys.exit(0)
            words[label]=word


    colors=[(0,0,0),(255,0,0),(0,255,0),(0,0,255)]
    font_sizes=[18,20,22,24,28,32,36,40,44,48,54,60,66]
    font_files=fonts_path.files()

    # show the different fonts on the image.
    if fonts_test:
        for font in font_files:
            try:
                bbox,img=text_on_img(imgs[10],u'好',font,font_sizes,colors)
                img.save(words_img_path + font.split(u'/')[-1][0:-4] + '.jpg','JPEG')
            except:
                print font
                continue
        sys.exit()

    bg_img_pick=[]
    font_pick=[]
    bg_img_idx=0
    font_file_idx=0
    word_idx=0
    words_num={}
    random.shuffle(imgs)
    bg_imgs_size=len(imgs)
    random.shuffle(font_files)
    fonts_size=len(font_files)
    anno=open(words_img_path+'/'+label_file, 'w')
    anno_cls=open(single_words_img_path+'/'+label_file, 'w')
    for word in words:
        img_folder='/img_%s'%word
        label_folder='/gt_%s'%word
        if not os.path.exists(words_img_path + img_folder):
            os.popen("mkdir -p %s"%(words_img_path + img_folder))
        if not os.path.exists(words_img_path + label_folder):
            os.popen("mkdir -p %s"%(words_img_path + label_folder))
        # create words on image.
        idx = 0
        while(idx < NUM_WORDS):
            img_name="/%s_%d"%(word,idx)
            
            # choose the background.
            bg_img_idx += 1
            if bg_img_idx > bg_imgs_size - 1:
                bg_img_idx = 0

            # choose the font.
            font_file_idx += 1
            if font_file_idx > fonts_size - 1:
                font_file_idx = 0

            # draw text on image.
            bboxes,img=multi_text_on_img(imgs[bg_img_idx].strip(),word,\
                    words,font_files[font_file_idx],font_sizes,colors)
            if bboxes[0][-1] == 0:
                continue
            with open(words_img_path+label_folder+img_name+".txt",'w') as label_file:
                label=word
                if label_type == 'detection':
                    label='1'
                for bbox in bboxes:
                    label_file.write("%d %d %d %d %d\n"%(\
                        int(label),bbox[0],bbox[1],bbox[2],bbox[3]))
                    if bbox[4] not in words_num:
                        words_num[bbox[4]]=1
                    else:
                        words_num[bbox[4]] += 1
                    create_word_cls_data(img,bbox,words_num[bbox[4]],anno_cls)
            img.save(words_img_path+img_folder+img_name+'.jpg','JPEG')

            anno.write("%s %s\n"%(words_img_path+img_folder+img_name+'.jpg',\
                    words_img_path+label_folder+img_name+".txt"))
            if debug:
                draw=ImageDraw.Draw(img)
                draw.rectangle((bbox[0],bbox[1],\
                    bbox[0] + bbox[2],bbox[1] + bbox[3]),outline = "red")
                img.save(words_img_path + 'tt.jpg','JPEG')
            idx += 1
        word_idx += 1
        print "Generating No. {} - {} .".format(word_idx,words[word].encode('utf-8'))
    anno.close()
    anno_cls.close()
    words_num_info=open(words_img_path + '/words_num_info.txt','w')
    words_num_info.write("word num\n")
    for word in words_num:
        words_num_info.write("%s %s\n"%(word,words_num[word]))
    words_num_info.close()
    

