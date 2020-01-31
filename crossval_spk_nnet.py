#!/usr/bin/env python3
#
# This script is part of ASICAKaldiRecipe. It is used to test recognition of control files.
# That is the system is trained with a subset of the training files, and it is tested with
# remaining training files.
#
#
# You have three options:
#    python3 Andres_ASICA_cross_val all             to test ALL spk IDs. That is, complete cross evaluation.
#    python3 Andres_ASICA_cross_val + 001 123 ...   test specific spk IDs, 001 and 123 in this example will be used in cross validation.
#    python3 Andres_ASICA_cross_val - 001 123 ...   test ALL spk IDs except specified. Test every speaker in cross validation except indicated.
#
# Default parameter is all
#
#
# Speaker's ID are recovered from the audio files as follows.
# For files ----------------  the ID is ---
#               CL001QL4_H45.wav                 001
#               CL034QL4_H45.wav                 034
# etc.
# That is, it gets chars 3, 4 and 5
# If your speakers IDs are different from the above you will have to adapt the code.
# To facilitate this, you will find this comment where the code change is needed:
#
# ----    Check this if your IDs are different from above
#
#
# The RESULTS will be found in results/crossval_spk_all.txt
# You will also find temporal files such as:
# crossval_spk_001.txt
# crossval_spk_034.txt
# But the latter are deleted at the very begining of this script
#
#
# NOTE: This script is part fo ASICAKaldiRecipe, developed by:
# Salvador Florido (main programmaer), Ignacio Moreno-Torres and Enrique Nava
# We assume the folder structure in your compuTer is that described in the Recipe
# and that this file is in the main folder (i.e. ASICAKaldiRecipe)
#
# Funtion to interrupt program with CTRL-C


import os
import sys
import shutil
import subprocess
#import result_format
import crossval_spk_functions
import pandas as pd

#import csv
#import ASICA
#import config

#import configTrain
#import configTest
#import check_format
#import time
#import argparse
#import subprocess
#import run_iteration


# ----------------------- FUNCTIONS  -----------------------------------------#


def results_ml_al(speaker_id):

    # speaker_id = 'CA016'
    # AM AL model is modified in file /local/score.sh min_lmwt y max_lmwt. It limits the inverse of AM weight, i.e: higher lmwt means high influence of ML language model

    df = pd.DataFrame(columns=('Speaker ID', 'AMAL', 'WInst', 'WER', 'Ins', 'Del', 'Sub'))
    wer_path = 'exp/nnet2/nnet2_simple/decode/'
    wer_best_path = 'exp/nnet2/nnet2_simple/decode/scoring_kaldi/'
    save_csv_path = 'results_AMAL/'

    if not os.path.isdir(save_csv_path):
        os.makedirs(save_csv_path)
        print("created folder: ", save_csv_path)

    wer_files = os.listdir(wer_path)
    wer_files.sort()

    for file in wer_files:
        if file.startswith("wer_"):

            txt = open(os.path.join(wer_path,file), "r")
            wer_txt = txt.readline()
            wer_txt = txt.readline()
            wer_txt = wer_txt.split()

            # Take all data
            Speaker_ID_data = speaker_id
            AMAL_data = float(file[4:-4])
            WInst_data = float(file[-3:])

            WER_data = float(wer_txt[1])
            Ins_data = float(wer_txt[6])
            Del_data = float(wer_txt[8])
            Sub_data = float(wer_txt[10])

            df = df.append({'Speaker ID' : Speaker_ID_data, 'AMAL' : AMAL_data, 'WInst' : WInst_data, 'WER' : WER_data, 'Ins' : Ins_data, 'Del' : Del_data, 'Sub' : Sub_data} , ignore_index=True)


    txt = open(os.path.join(wer_best_path,"best_wer"), "r")
    wer_txt = txt.readline()
    wer_txt = wer_txt.split()

    # Take all data
    Speaker_ID_data = speaker_id + "_best_wer"
    AMAL_data = float(wer_txt[-1][4:-4])       # ----    Check this if your IDs are different from above
    WInst_data = float(wer_txt[-1][-3:])

    WER_data = float(wer_txt[1])
    Ins_data = float(wer_txt[5])
    Del_data = float(wer_txt[7])
    Sub_data = float(wer_txt[9])

    df = df.append({'Speaker ID' : Speaker_ID_data, 'AMAL' : AMAL_data, 'WInst' : WInst_data, 'WER' : WER_data, 'Ins' : Ins_data, 'Del' : Del_data, 'Sub' : Sub_data} , ignore_index=True)

    # Save dataFrame as csv in save_csv_path
    df.to_csv(path_or_buf=os.path.join(save_csv_path,speaker_id+"_wer.csv"),index=False)

# end function

def main(argv):

    # ----------------------- ARGUMENT PARSING -------------------------------#
    speakers_plus_minus = list()    # speakers included in + or excluded in -

    if len(sys.argv) == 1:
        print("\nNo argument indicated. CrossVal mode set to \"all\"")
        crossVal_mode = "all"
    else:
        crossVal_mode = sys.argv[1]
        speakers_plus_minus = sys.argv[2:]

        if not( crossVal_mode=="all" or crossVal_mode=="+" or crossVal_mode=="-"):
           print("\nNo adecuated argument indicated. Only possible values: all, +, -. CrossVal mode set to \"all\"")
           crossVal_mode = "all"
        elif not(speakers_plus_minus):
           print("\nNo list of speakers argument indicated. CrossVal mode set to \"all\"")
           crossVal_mode = "all"
    # end if


    # -------------------------- USER VARIABLES ------------------------------#

    # .wav and .kal file paths:
    # !!: Audio files are in the same folder both training and testing, are selected based on info_user folders
    audio_path = 'audio/experiment_lm/'
    info_test_path = 'info_user/test/'
    info_train_path = 'info_user/train/'

    # Internal folder Paths:
    no_kal_path = 'audio/experiment_lm/no_kal_audio'

    # Internal file Paths:
    result_spk= 'results/'
#    result_amal= 'results_AMAL/'
#    result_spk_raw= 'results/raw/'
    result_reformat = 'results/reformat/'
#    global_spk = 'results/global_spk.txt'

    # Result filename path:
    resultFilename = 'resultIniciales'



    # ------------------------ MAIN SECTION ----------------------------------#

    # Move all test files to train folder
    for f in os.listdir(info_test_path):
        shutil.move(os.path.join(info_test_path,f), info_train_path)

    # Asses directory structure:
    train_spks_audio = list()
    test_spks_info = list()
    train_spks_info = list()

    for file in os.listdir(info_test_path):
        if file.endswith(".kal") and not(file.startswith(".")) and not(file.startswith("_")):
            test_spks_info.append(file)
    for file in os.listdir(info_train_path):
        if file.endswith(".kal") and not(file.startswith(".")) and not(file.startswith("_")):
            train_spks_info.append(file)

    # Clean and reorder audio files
    crossval_spk_functions.clean_wave_files(train_spks_info, audio_path, no_kal_path)

    for file in os.listdir(audio_path):
        if file.endswith(".wav") and not(file.startswith(".")) and not(file.startswith("_")):
            train_spks_audio.append(file)


    print("\n " + str(len(train_spks_audio)) + " wav files in folder " + audio_path)

    print("\n " + str(len(train_spks_info)) + " kal files in folder " + info_train_path)
    print(" " + str(len(test_spks_info)) + " kal files in folder " + info_test_path)

    print("\n Estos archivos .kal faltan:")
    crossval_spk_functions.check_kal_wav(train_spks_audio, train_spks_info)

    if len(train_spks_audio) == 0 or len(train_spks_info) == 0:
        print("ABORTING EXECUTION BECAUSE SOME FOLDER IS EMPTY")
        exit()


    # Search for unique speakers ID
    speakers_list = list()
    for spk in train_spks_info:
        speakers_list.append(spk[0:5])  # ----    Check this if your IDs are different from above
    # end for
    speakers_list = list(set(speakers_list))
    print("\n " + str(len(speakers_list)) + " different speakers")

    # Also check the input list of user to adequate labeling system
    speakers_plus_minus_nameModified = list()
    for spk in speakers_list:
        user = spk[2:5]     # ----    Check this if your IDs are different from above
        if user in speakers_plus_minus:
            speakers_plus_minus_nameModified.append(spk[0:5])   # ----    Check this if your IDs are different from above
    # end for



#    # Clean result folder
#    config.silentFile_remove(global_spk)  # delete global_spk (results/global_spk.txt) from /results/
#
#    filelist = [ f for f in os.listdir(result_spk_raw) if f.endswith("raw.txt") ]
#    for f in filelist:
#        os.remove(os.path.join(result_spk_raw, f))
#
#    filelist = [ f for f in os.listdir(result_spk) if f.endswith(".csv") ]
#    for f in filelist:
#        os.remove(os.path.join(result_spk, f))
#
#    filelist = [ f for f in os.listdir(result_amal) if f.endswith(".csv") ]
#    for f in filelist:
#        os.remove(os.path.join(result_amal, f))


    # ------------------------- CROSS VALIDATION -----------------------------#

    print("\n---------------------------------------------------")
    print("---------------------------------------------------")
    print("        MAIN LOOP OF CROSS-VALIDATION STARTED      ")
    print("---------------------------------------------------")
    print("---------------------------------------------------")

    speakers_list_modified = list()

    if crossVal_mode == "all":
        # Each iteration: training phase --> (train except one speaker) ··· testing phase --> (One of train excluded before)
        speakers_list_modified = speakers_list
    if crossVal_mode == "+":
        speakers_list_modified = speakers_plus_minus_nameModified
    if crossVal_mode == "-":
        speakers_list_modified = [spk for spk in speakers_list if spk not in speakers_plus_minus_nameModified]
    #end if

    print("Testing " + str(len(speakers_list_modified)) + " speakers:")
    print(speakers_list_modified)

    try:

        # Executed for each speaker indicated in speakers_list_modified
        for spk in speakers_list_modified:

            excludedSpk = spk
            # excludedSpk = speakers_list_modified[0]

            print("\n---------------------------------------------------")
            print("      Testing with Speaker " + excludedSpk + "     ")
            print("---------------------------------------------------")

            # Folder info_user/test is filled with testing speaker
            files = os.listdir(info_train_path)


            for f in files:
                if (f.startswith(excludedSpk) and f.endswith(".kal")):
                    shutil.move(os.path.join(info_train_path,f), info_test_path)
                # end if
            # end for

            # --------------------- NNET2 CROSS VAL --------------------------#
            # ----------------------------------------------------------------#

            # bashCommand = "python3 run.py --train --test"
            bashCommand = "python3 run.py --test"
            # bashCommand = "python3 run.py --train"
            process = subprocess.Popen(bashCommand,shell=True)
            output, error = process.communicate()

            # Results
            # crossval_spk_functions.results_ml_al(excludedSpk,'nnet')  # only calculate AM AL for QL4 in speakers

            # Folder info_user/test is emptied
            files = os.listdir(info_test_path)
            for f in files:
                shutil.move(os.path.join(info_test_path,f), info_train_path)
            # end for


            # Save all results in txt file
            resultFilename = 'results/resultSimple'
            os.rename(resultFilename, resultFilename+'_'+excludedSpk)

            num_lines = sum(1 for line in open(resultFilename+'_'+excludedSpk))
            file = open(resultFilename+'_'+excludedSpk)
            fileGlobal = open('results/resultGlobal', 'a')
            for i in range(0,num_lines-1):
                line = file.readline()
                fileGlobal.write(line)
            fileGlobal.close()

            # Save raw results and csv
            crossval_spk_functions.save_raw_result()

        # end for
    except Exception as e:
        print("\n\n"+e)
        print("\nAn ERROR inside the code have occured: Moving back every file as in the initial state")

        # Move back all test files to train folder
        files = os.listdir(info_test_path)
        for f in files:
            shutil.move(os.path.join(info_test_path,f), info_train_path)

    # end try

    print("\n---------------------------------------------------")
    print("---------------------------------------------------")
    print("       MAIN LOOP OF CROSS-VALIDATION FINISHED      ")
    print("---------------------------------------------------")
    print("---------------------------------------------------")

    # Take .csv result and reformat for SPSS analysis
    for file in os.listdir(result_spk):
        if file.endswith(".csv"):
            bashCommand = "python3 result_reformat.py " + os.path.join(result_spk,file) + " " + os.path.join(result_reformat,file[:-4])+'_reformat.csv'
            process = subprocess.Popen(bashCommand,shell=True)
            output, error = process.communicate()

    # Global results for SPSS
    crossval_spk_functions.global_result_reformat(result_reformat)

# end function


# ----------------------------------------------------- MAIN SECTION ------------------------------------------------------------------------------#

if __name__ == "__main__":
   main(sys.argv)


