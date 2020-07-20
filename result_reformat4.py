#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec  1 08:27:04 2019

@author: ignaciomoreno-torres
"""

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
        resp="Afric"
    elif cons in ["f","z","s","y","x"]:
        resp="Fric"
    elif cons in ["m","n","ny"]:
        resp="Nas"
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
        resp="Back"
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

def sex(evaluation):
    return (evaluation[0:1])

def ageGroup(evaluation):
    edad=evaluation[1:3]
#    print("Edad: ",edad," ")

    if edad in ["00","50","51","52","54","55","56","57"]:
        ageGroup="5"
    else:
        ageGroup="2"

#    print("Grupo Edad: ",ageGroup," ")

    return (ageGroup)


def tipo_palabra(palabra):
    if palabra in ["ba rre nyo", "bu ke", "ka ba ye ro", "ka ba ye te", "ka yo", "ka mi no", "ka nyo", "ka pi tu lo", "ka rro ma to", "ka rro nya", "ze bo", "chu lo", "zi ma", "zi ne", "ko li ya", "ko pa", "de ba te", "di ne ro", "fe cha", "fi lo so fo", "ge rra", "gi nyo", "xe ta", "la do", "la ti ga zo", "li ga", "lo na", "lu cha", "ma ni be la", "ma no ta zo", "ma nya na", "ma re xa da", "me ze do ra", "me di zi na", "mi ri ya", "mo te", "mu lo", "mu si ka", "no che", "no be la", "nu me ro", "pa le ti ya", "pa li yo", "pe li ku la", "pe na", "pe so", "pe ta ka", "pe ta te", "rre ti ra da", "rro ka", "sa te li te", "se nyo ri ta", "so da", "so ga", "ta le go", "ti tu lo", "to rre", "tu fo", "ba ye", "be na", "bi ga", "bi ya", "ya te", "ye ma"]:
        tipo="PAL"
    elif palabra in ["ba rre yo", "bu de", "ka ba ye mo", "ka ba ye to", "ka xo", "ka yi", "ka mi ro", "ka pi tu bo", "ka rro fa", "ka rro ma do", "ze bi", "chu so", "zi da", "zi se", "ko da", "ko li za", "de ba ti", "di ne so", "fe za", "fi lo so zo", "ge za", "gi cho", "xe ra", "la ro", "la ti ga fo", "li ya", "lo ra", "lu xa", "ma ni be za", "ma no ta go", "ma nya da", "ma re xa za", "me ze do ta", "me di zi ra", "mi ri za", "mo de", "mu no", "mu si ma", "no fe", "no be ya", "nu me so", "pa le ti rra", "pa li xo", "pe li ku za", "pe no", "pe ta", "pe ta ma", "pe ta ti", "rre ti ra za", "rro ko", "sa te li to", "se nyo ri da", "so ya", "so ma", "ta le bo", "ti tu mo", "to ye", "tu zo", "ba fe", "be ta", "bi ka", "bi la", "ya to", "ye da"]:
        tipo="PSUD1"
    elif palabra in ["be ya fe", "be yo lu", "bi fu pe si", "bu fe lu", "ka mo", "ka po di no", "zi bu fe ni", "zi fo", "ko zi", "ko di so", "ko ga", "ko pa di", "ko pa te", "ku fe", "ku xo ba", "di ku", "di ku li te", "di la", "di ma ko", "di ra ni", "do bu", "do fe", "do ya", "fe bu xo", "fe xi", "fo bo xe ma", "fu xo", "lo fe du ne", "lu fo", "ma po", "me la ni to", "me pe", "me po", "mo ku", "mo pa so ka", "mo pe", "mo pe di ta", "na fe", "ni fu ba mi", "ni gu", "ni bo fe ma", "no fe", "no fe ba", "no lu", "pa ba ri mo", "pa de so", "pa do", "pa ne", "pa ni", "pe ku ga ta", "pe mi", "rri bu po", "se ku", "so ga li na", "so ma zi", "so ri", "so te to", "ti bo", "ti bu", "ti fe du ne", "ti yo", "za fe lu di", "za lu", "za bo lu"]:
        tipo="PSUD2"
    else:
        tipo="ERROR"

    return(tipo)

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

        lista1.append("Syllable position") #


        lista1.append("UttType") # ZZ PENDIENTEZZ


        lista1.append("AgeGroup")
        lista1.append("Sex")
        lista1.append("SilabaN")
        lista1.append("TargetC")
        lista1.append("TargetV")
        lista1.append("RespC")
        lista1.append("RespV")

        lista1.append("ErrPattern")


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
        ultimo=lista1[len(lista1)-1]
#        print(ultimo)
        listToStr = '\t'.join([str(elem) for elem in lista1])
        salida.write(listToStr)

    else:
        lista2=linea.split('\t')
        #print("Nueva lista de datos: ",lista2)
        #print("NCampos: ",len(lista2))
        ultimo=lista2[11]
        lista2[11]=ultimo[:1]
#        lista2.pop(len(lista2)-1)
        #print("Nueva lista2 de datos: ",lista2)
        #print("NCampos: ",len(lista2))

        targetUtt=lista2[8]

        if (lista2[6]=="D"):
             typeUtt="InsDel"
        elif (lista2[6]=="I"):
             typeUtt="InsDel"
        else:
            typeUtt=tipo_palabra(targetUtt)

        evaluation=lista2[3]
        groupoEdad=ageGroup(evaluation)
        sexo=sex(evaluation)



        #print("lista2[10] vale: ",lista2[10])


        silabaN=lista2[10]+lista2[11] # Concateno para tener un identificador único de sílaba


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
            errPattern=0
        else:
            corrC=0
            errPattern=targetC+"_"+respC

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

        lista2.append(typeUtt)

        lista2.append(groupoEdad)
        lista2.append(sexo)
        lista2.append(silabaN)
        lista2.append(targetC)
        lista2.append(targetV)
        lista2.append(respC)
        lista2.append(respV)

        lista2.append(errPattern)

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