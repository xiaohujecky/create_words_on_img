#!/usr/bin/evn python
import os,sys
import cv2
save_classify_dir='result/v3_textline_det_eng/words_classify/text_train/'
if os.path.exists(save_classify_dir):
    print "The dir exists, please rm it. %s"%save_classify_dir
    sys.exit()
else:
    os.popen('mkdir -p %s'%save_classify_dir)
print "DIR: %s"%save_classify_dir

def load_words_map(words_map_path):
    words={}
    with open(words_map_path,'r') as f:
        lines=unicode(f.read(),'utf-8').split('\n')
        lines=lines[0:-1]
        for line in lines:
            label,word=line.strip().split(u' ')
            if label in words and word !=words[label]:
                print "word label wrong: %s - %s"%(label,word)
                sys.exit(0)
            words[label]=word
    return words

def crop_img_and_save(words_map, img_file, lab_file, idx):
    cv_img = cv2.imread(img_file)
    index=idx
    with open(lab_file, 'r') as f:
        lines = f.readlines()
        for line in lines:
            itms = line.strip().split(' ')
            if len(itms) < 5:
                continue
            labels = itms[0].split('+')[:-1]
            label = ''
            for lab in labels:
                label += words_map[lab]
            xmin = int(itms[1])
            ymin = int(itms[2])
            xmax = int(itms[3])
            ymax = int(itms[4])
            cv_img_crop = cv_img[ymin:ymax, xmin:xmax]
            crop_save_name = "{:0>8}_{}.png".format(index, label)
            cv2.imwrite(save_classify_dir + crop_save_name, cv_img_crop)
            index += 1
            print "id:{}\t".format(index),
    return index 

def crop_img_and_save_label(flabel, words_map, img_file, lab_file, idx):
    cv_img = cv2.imread(img_file)
    index=idx
    with open(lab_file, 'r') as f:
        lines = f.readlines()
        for line in lines:
            itms = line.strip().split(' ')
            if len(itms) < 5:
                continue
            labels = itms[0]
            xmin = int(itms[1])
            ymin = int(itms[2])
            xmax = int(itms[3])
            ymax = int(itms[4])
            cv_img_crop = cv_img[ymin:ymax, xmin:xmax]
            crop_save_name = "{:0>8}.png".format(index)
            cv2.imwrite(save_classify_dir + crop_save_name, cv_img_crop)
            index += 1
            flabel.write("%s %s\n"%(save_classify_dir + crop_save_name, labels))
            print "id:{}\t".format(index),
    return index


def walk_cls_label_file(label_file, words_map_file, words_label_file):
    words_map = load_words_map(words_map_file)
    index_id = 0
    flabel = open(words_label_file, 'w')
    with open(label_file, 'r') as f:
        for line in f.readlines():
            itm = line.strip().split()
            index_id_next = crop_img_and_save_label(flabel, words_map, itm[0], itm[1], index_id)
            index_id = index_id_next
    flabel.close()

if __name__ == '__main__':
    cls_label_file = sys.argv[1]
    words_label_file = sys.argv[2]
    words_map_file = 'conf/words_all.txt' 
    walk_cls_label_file(cls_label_file, words_map_file, words_label_file)
    print "DIR: %s"%save_classify_dir
