#!/bin/bash


#--------------------------SETTING DIRECTORY STRUCTURE------------------------#


#Se borra la carpeta mfcc, data y exp
rm -rf exp
rm -rf data

#Se genera las carpetas vacias mfcc, data (y sus compartimentos), y exp
cp -vr data_init data
mkdir exp


for f; do
    #echo $f
    rm -rf $f
    mkdir $f
done

#rm -rf mfcc
#mkdir mfcc
