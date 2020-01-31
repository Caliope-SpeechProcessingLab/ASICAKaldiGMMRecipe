#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#"""
#Created on Sun Dec  1 08:27:04 2019
#
#@author: ignaciomoreno-torres
#"""

import os
import sys



def extraeCons(silaba):
    #print("Lista actual: ",list1)
    if len(silaba)==1:
        cons="*"
    elif len(silaba)==2:
        cons=silaba[0:1]
    elif ((len(silaba)==3) & (silaba[1] in ['a','e','i','o','u'])):
        cons=silaba[0:1]
    else:
        cons=silaba[0:2]
    return(cons)

def extraeVocal(silaba):
    #print("Lista actual: ",list1)
    if len(silaba)==2:
        cons=silaba[1:2]
    else:
        cons=silaba[2:3]
    return(cons)


def modo(cons):
    if cons in ["b","p","d","t","g","k"]:
        resp="Ocl"
    elif cons in ["ch"]:
        resp="Afic"
    elif cons in ["f","z","s","y","x"]:
        resp="fric"
    elif cons in ["m","n","ny"]:
        resp="nas"
    elif cons in ["l","r","rr"]:
        resp="Aprox"
    else:
        resp="Other"
    return(resp)

def lugar(cons):
    if cons in ["b","p","f","m"]:
        resp="Frontal"
    elif cons in ["d","t","ch","z","s","y","n","ny","l","r","rr"]:
        resp="Coronal"
    elif cons in ["g","k","x"]:
        resp="back"
    else:
        resp="Other"
    return(resp)


def sonoridad(cons):
    if cons in ["b","d","g","y","m","n","ny","l","r","rr"]:
        resp="Voiced"
    elif cons in ["p","t","k","ch","f","z","x","s",]:
        resp="Vless"
    else:
        resp="Other"
    return(resp)

# read commandline arguments, first
fullCmdArguments = sys.argv

# - further arguments
argumentList = fullCmdArguments[1:]

# print(argumentList)

if (len(argumentList) != 2):
    print("")
    print("Sintaxis incorrecta!")
    print("")
    print("Debe ser: python3 result_reformat.py ENTRADA SALIDA")
    print("")
    print("Donde:")
    print("ENTRADA es un archivo generado por result_format.py")
    print("SALIDA es un nombre de archivo de salida")
    print("")
    exit()


entrada=open(argumentList[0],"r");
salida=open(argumentList[1],"w");

n=0

for linea in entrada:
    if (n == 0):
        n=n+1
        lista1=linea.split('\t')
        lista1[0]="N"
        ultimo=lista1[len(lista1)-1]
#        print("Lista1 original: ",lista1)
#        print("NCampos: ",len(lista1))
#        print("Último: ",ultimo)
        lista1.pop(len(lista1)-1)
#        print("Nueva lista1: ",lista1)
#        print("NCampos: ",len(lista1))
#        print("Último: ",ultimo)
#        print(ultimo)
        lista1.append("TargetC")
        lista1.append("TargetV")
        lista1.append("RespC")
        lista1.append("RespV")
        lista1.append("TargetCManner")
        lista1.append("TargetCVoice")
        lista1.append("TargetCPlace")
        lista1.append("RespCanner")
        lista1.append("RespVoice")
        lista1.append("RespPlace")

        lista1.append("CorrC")
        lista1.append("CorrV")
        lista1.append("CorrManner")
        lista1.append("CorrVoice")
        lista1.append("CorrPlace")

        lista1.append("\n")
#        print("Nueva lista1: ",lista1)
#        print("NCampos: ",len(lista1))
        ultimo=lista1[len(lista1)-2]
#        print(ultimo)
        listToStr = '\t'.join([str(elem) for elem in lista1])
        salida.write(listToStr)

    else:
        lista2=linea.split('\t')
#        print("Nueva lista de datos: ",lista2)
#        print("NCampos: ",len(lista2))
        lista2.pop(len(lista2)-1)

        targetSil=lista2[4]
        targetC=extraeCons(targetSil)
        targetV=extraeVocal(targetSil)
        respSil=lista2[5]
        respC=extraeCons(respSil)
        respV=extraeVocal(respSil)

        targetManner=modo(targetC)
        targetVoice=sonoridad(targetC)
        targetPlace=lugar(targetC)

        respManner=modo(respC)
        respVoice=sonoridad(respC)
        respPlace=lugar(respC)

        if (targetC==respC):
            corrC=1
        else:
            corrC=0

        if (targetV==respV):
            corrV=1
        else:
            corrV=0


        if targetManner==respManner:
            corrManner=1
        else:
            corrManner=0

        if targetVoice==respVoice:
            corrVoice=1
        else:
            corrVoice=0

        if targetPlace==respPlace:
            corrPlace=1
        else:
            corrPlace=0

        lista2.append(targetC)
        lista2.append(targetV)
        lista2.append(respC)
        lista2.append(respV)
        lista2.append(targetManner)
        lista2.append(targetVoice)
        lista2.append(targetPlace)

        lista2.append(respManner)
        lista2.append(respVoice)
        lista2.append(respPlace)

        lista2.append(corrC)
        lista2.append(corrV)

        lista2.append(corrManner)
        lista2.append(corrVoice)
        lista2.append(corrPlace)

        lista2.append("\n")

        listToStr = '\t'.join([str(elem) for elem in lista2])
        salida.write(listToStr)


#        print("Target C: ",targetC)
#        print("Target V: ",targetV)
#        print("Resp C:", respC)
#        print("Resp V",respV)


salida.close()