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
NUM_WORDS=50
bg_imgs_path='image.txt'
bg_imgs_path='/Users/xiaohu/tongdun/textDetect/image/10k.txt'
words_img_path='result/'
words_path='conf/words_all.txt'

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

def multi_text_on_img(img_name,text,texts,font_file,font_sizes,colors):
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
            draw.text(loc,text,color,font=font)
            text=texts[random.choice(texts.keys())]
            bboxes.append([loc[0],loc[1],int(loc[0])+font_size,int(loc[1])+font_size])
    return bboxes,img

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
    anno=open(words_img_path+'/'+label_file, 'w')
    for word in words:
        random.shuffle(imgs)
        bg_imgs_size=len(imgs)
        random.shuffle(font_files)
        fonts_size=len(font_files)
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
            if bg_img_idx >= bg_imgs_size - 1:
                bg_img_idx = 0

            # choose the font.
            font_file_idx += 1
            if font_file_idx >= fonts_size - 1:
                font_file_idx = 0

            # draw text on image.
            bboxes,img=multi_text_on_img(imgs[bg_img_idx].strip(),words[word],\
                    copy.copy(words),font_files[font_file_idx],font_sizes,colors)
            if bboxes[0][-1] == 0:
                continue
            with open(words_img_path+label_folder+img_name+".txt",'w') as label_file:
                label=word
                if label_type == 'detection':
                    label='1'
                for bbox in bboxes:
                    label_file.write("%d %d %d %d %d\n"%(\
                        int(label),bbox[0],bbox[1],bbox[2],bbox[3]))
            img.save(words_img_path+img_folder+img_name+'.jpg','JPEG')

            anno.write("%s %s\n"%(words_img_path+img_folder+img_name+'.jpg',\
                    words_img_path+label_folder+img_name+".txt"))
            if debug:
                draw=ImageDraw.Draw(img)
                draw.rectangle((bbox[0],bbox[1],\
                    bbox[0] + bbox[2],bbox[1] + bbox[3]),outline = "red")
                img.save(words_img_path + 'tt.jpg','JPEG')
            idx += 1
        break
    anno.close()
    

