import os,sys
import json

json_dict={}
with open('third_address.json', 'r') as f:
    json_dict = json.load(f)

adr = open('address.txt', 'w')
for keys1 in json_dict:
    for keys2 in json_dict[keys1]:
        for list3 in json_dict[keys1][keys2]:
            str1 = keys1.encode('utf-8')
            str2 = keys2.encode('utf-8')
            str3 = list3.encode('utf-8')
            #str1 = unicode(keys1, 'utf-8').encode('utf-8')
            #str2 = unicode(keys2, 'utf-8').encode('utf-8')
            #str3 = unicode(list3, 'utf-8').encode('utf-8')
            if str1 == str2:
                str2 = u''
            adr.write("{}{}{}\n".format(str1,str2,str3))

adr.close()
