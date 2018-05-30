# _*_ encoding=utf-8 _*_
import sys,os
import re

"""
words order:
    order. [words[num]][end_id]
    0. [0-9 [10]][9]
    1. [A-Z [26]][35]
    2. [a-a [26]][61]
    3. [ASCII33-ASCII47 [15], ASCII58-ASCII64 [7], ASCII91-ASCII96 [6]][89]
    4. [赵钱孙李-百家姓终 [568]][657]
    5. [一级汉字gb2312-1(除百家姓) []]
    6. [二级汉字gb2312-2(除百家姓) []][7331]
    7. [gbk/3-4汉字补充 []]
"""

text_num='0123456789'
text_eng='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
#ASCII number=ord(char), char=chr(number)
text_ascii=[[33,47],[58,64],[91,96],[126]]
words_map={}
words_id=0
def get_words_map(words_file):
    global words_map,words_id
    def limited_words(text_):
        global words_map
        global words_id
        for w in text_:
            words_map[w] = words_id
            words_id += 1
        return words_id
    # text we know first
    limited_words(text_num)
    limited_words(text_eng)
    def get_text_ascii(text_range_):
        global words_map
        global words_id
        for tr in text_range_:
            tr_id_start=tr[0]
            tr_id_end=tr_id_start
            if len(tr) > 1:
                tr_id_end = tr[1]
            tr_id = tr_id_start
            while tr_id <= tr_id_end:
                words_map[chr(tr_id)]=words_id
                words_id += 1
                tr_id += 1
        return words_id

    # Ascii strange words
    get_text_ascii(text_ascii)
    
    # urgly chinese words
    with open(words_file, 'r') as f:
        lines=unicode(f.read(), 'utf-8')
        print(len(lines))
        for widx in range(len(lines)):
            if lines[widx] in words_map:
                continue
            else:
                words_map[lines[widx]]=words_id
                words_id += 1
    words_map = sorted(words_map.items(), lambda x, y: cmp(x[1], y[1]))
   
    # write to file
    with open('words_encode_crnn.txt', 'w') as f:
        for w in words_map:
            f.write("{} {}\n".format(w[0].encode('utf-8'), w[1]))
    #print words_map

get_words_map('all_crnn.txt')
