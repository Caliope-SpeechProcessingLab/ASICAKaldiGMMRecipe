#!/usr/bin/env python3
#
# This script is the core of ASICAKaldiGMMRecipe and performs the main steps to train and test the model.
#
# Use:
#   python3 run.py --train          only make model training with info_user/train
#   python3 run.py --test           only make model testing with info_user/test
#   python3 run.py --train --test   performs both training and testing
#
# Now you should find the predicted transcriptions (results) in the folder "results".
#
# Funtion to interrupt program with CTRL-C
#


import os
import time
import argparse
import subprocess

import configTest
import configTrain
import check_format
import result_format


start_time = time.time()


parser = argparse.ArgumentParser()
parser.add_argument('-t', '--train',action='store_true', help='make training')
parser.add_argument('-r', '--test',action='store_true', help='make testing')

args = parser.parse_args()


#--------------------------- USER VARIABLES --------------------------------- #

# .wav and .kal file paths:
audioTestPath = 'audio/experiment_lm/'
audioTrainPath = 'audio/experiment_lm/'

testInfo_path = 'info_user/test/'
trainInfo_path = 'info_user/train/'

# Result filename path:
resultFilename = 'resultSimple'


# ----------------------- CHECK .KAL FORMAT --------------------------------- #
check_format.checker(testInfo_path)
check_format.checker(trainInfo_path)


#---------------------- INITIALIZE DATA AND AUDIO LISTS --------------------- #

# ASSESMENT OF THE DIRECTORY STRUCTURE:
audioTestFilenames = list()
audioTrainFilenames = list()
dataTestFilenames = list()
dataTrainFilenames = list()

for file in os.listdir(testInfo_path):
    if file.endswith(".kal") and not(file.startswith(".")) and not(file.startswith("_")):
        dataTestFilenames.append(file)
for file in os.listdir(trainInfo_path):
    if file.endswith(".kal") and not(file.startswith(".")) and not(file.startswith("_")):
        dataTrainFilenames.append(file)

for file in os.listdir(audioTestPath):
    if file.endswith(".wav") and not(file.startswith(".")) and not(file.startswith("_")):
        audioTestFilenames.append(file)
for file in os.listdir(audioTrainPath):
    if file.endswith(".wav") and not(file.startswith(".")) and not(file.startswith("_")):
        audioTrainFilenames.append(file)

print("\n " + str(len(audioTestFilenames)) + " wav files in folder " + audioTestPath)
# print(" " + str(len(audioTrainFilenames)) + " wav files in folder " + audioTrainPath + "   \n")
print(" " + str(len(dataTestFilenames)) + " kal files in folder " + testInfo_path)
print(" " + str(len(dataTrainFilenames)) + " kal files in folder " + trainInfo_path + "   \n")

if len(audioTestFilenames) == 0 or len(audioTrainFilenames) == 0 or len(dataTestFilenames) == 0 or len(dataTrainFilenames) == 0:
    print("Some folders are empty. This is posibly an error.")
    # print("ABORTING EXECUTION BECAUSE SOME FOLDER IS EMPTY")
    # exit()


#---------------------------------------------------------------------------- #


if args.train:

    print("\n-----------------RESET DATA----------------------\n")
    bashCommand = "bash local/resetDirectory.sh"
    process = subprocess.Popen(bashCommand,shell=True)
    output, error = process.communicate()

    print("\n-----------------CONFIG TRAIN DATA----------------------\n")
    configTrain.main(dataTrainFilenames)
    # Se ha corregido para que no muestre todos los nombres
    # Se corrige los path de audio y user_data


    print("\n-----------------MAKE FEATS----------------------\n")
    bashCommand = "bash local/makeFeats.sh train"
    process = subprocess.Popen(bashCommand,shell=True)
    output, error = process.communicate()

    print("\n-----------------MAKE LANGUAGE MODEL----------------------\n")
    bashCommand = "bash local/makeLanguageModel.sh"
    process = subprocess.Popen(bashCommand,shell=True)
    output, error = process.communicate()


    print("\n-----------------TRAIN----------------------\n")
    bashCommand = "bash local/train.sh {}".format(trainInfo_path)
    process = subprocess.Popen(bashCommand,shell=True)
    output, error = process.communicate()

    print("\n-----------------END TRAINING----------------------\n")
# end if

if args.test:

    print("\n-----------------CONFIG TEST DATA----------------------\n")
    configTest.main(dataTestFilenames, audioTestPath, testInfo_path)
    # Se ha corregido para que no muestre todos los nombres


    print("\n-----------------MAKE FEATS----------------------\n")
    bashCommand = "bash local/makeFeats.sh test"
    process = subprocess.Popen(bashCommand,shell=True)
    output, error = process.communicate()


    print("\n-----------------TEST----------------------\n")
    bashCommand = "bash local/test.sh {}".format(testInfo_path)
    process = subprocess.Popen(bashCommand,shell=True)
    output, error = process.communicate()


    print("\n-----------------EXTRACT RESULTS----------------------\n")
    pathTo_perSpk = 'exp/tri1/decode/scoring_kaldi/wer_details/per_spk'
    result_format.simpleFormat(pathTo_perSpk,'results/' + resultFilename)

    import result_format

# end if

print("--- %s seconds ---" % (time.time() - start_time))


