#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 24 08:33:54 2020

@author: andres
"""

import os
import sys


try:
    num_subs = int(sys.argv[1])
except:
    num_subs = 1
# end try
print('Split .kal annotations in ' + str(num_subs) + ' parts')


path_in = 'anotaciones/'
path_out = 'anotaciones_sub/'

# Move all test files to train folder
for f in os.listdir(path_out):
    os.remove(os.path.join(path_out, f))

if num_subs > 1:
    num_list = list(range(1,num_subs+1))
else:
    num_list = list()
# end if

for kal in os.listdir(path_in):
    txt_in=open(os.path.join(path_in,kal),"r")
    txt_out=open(os.path.join(path_out,kal),"w")

    txt_in = txt_in.readline()
    list_txt = txt_in.split()

    spk = kal[5:8]

    if 'DEC' in spk:
        label = 'E'
    elif 'INT' in spk:
        label = 'I'
    # end if

    list_final = list_txt[0:2]

    if num_subs > 1:
        label_txt = (''.join([label+str(n)+' ' for n in num_list]))[:-1]
        list_final.append(label_txt)
        list_final.append(label_txt)
    else:
        list_final.append(label)
        list_final.append(label)
    # end if
    listToStr = '\t'.join([str(elem) for elem in list_final])
    txt_out.write(listToStr)
    txt_out.close()
# end for


#
#
#txt_in=open(path_in,"r")
#txt_out=open(path_out,"w")
#
#text_list = ['Locutor','%DEC','%INT','\n']
#listToStr = '\t'.join([str(elem) for elem in text_list])
#txt_out.write(listToStr)
#
#spk_list = list()
#d_global = {}
## Check all speakers
#for line in txt_in:
#    l1 = line.split()
#    spk = l1[0][0:8]
#    value = float(l1[1])
#
#    if spk in d_global:
#        d_global[spk].append(value)
#    else:
#        d_global[spk]= list([value])
#    # end if
#
#    spk_list.append(l1[0][0:5])
## end for
#
#spk_list = set(spk_list)
#
#for spk in spk_list:
#    l1 = [spk,np.mean(d_global[spk+'DEC']),np.mean(d_global[spk+'INT']),'\n']
#    listToStr = '\t'.join([str(elem) for elem in l1])
#    txt_out.write(listToStr)
## end for
#
#
#txt_out.close()





