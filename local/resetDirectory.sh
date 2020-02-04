#!/bin/bash


#--------------------------SETTING DIRECTORY STRUCTURE------------------------#


#Se borra la carpeta mfcc, data y exp
rm -rf mfcc
rm -rf exp
rm -rf data

#Se genera las carpetas vacias mfcc, data (y sus compartimentos), y exp
cp -vr data_init data
mkdir mfcc
mkdir exp

