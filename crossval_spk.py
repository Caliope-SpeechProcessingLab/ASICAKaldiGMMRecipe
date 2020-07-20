#!/usr/bin/env python3
#
# This script is part of ASICAKaldiRecipe. It is used to test recognition of control files.
# That is the system is trained with a subset of the training files, and it is tested with
# remaining training files.
#
#
# You have three options:
#
#    python3 crossval_spk.py -a
#    python3 crossval_spk.py --all)                   to test ALL spk IDs. That is, complete cross evaluation.
#
#    python3 crossval_spk.py -p 001 123 ...
#    python3 crossval_spk.py --plus 001 123 ...       test specific spk IDs, 001 and 123 will be used in cross validation.
#
#    python3 crossval_spk.py -m  001 123 ...
#    python3 crossval_spk.py --minus 001 123 ...      test ALL spk IDs except specified. Test every speaker except indicated.
#
#   python3 crossval_spk.py -p 001 123 -f mfcc plp pitch
#
# Default parameter is --all -f mfcc
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
import argparse
import subprocess
import crossval_spk_functions

# ----------------------- FUNCTIONS  -----------------------------------------#
def main(argv):

    # ----------------------- ARGUMENT PARSING -------------------------------#
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--all', action='store_true', help='Use all speakers.')
    parser.add_argument('-p', '--plus',  nargs='+', help='Test only indicated speakers')
    parser.add_argument('-m', '--minus',  nargs='+', help='Test all except indicated speakers')
    parser.add_argument('-f', '--feats',  nargs='+', help='Features to use, compulsory to include one e.g. -l mfcc')
    args = parser.parse_args()

    speakers_plus_minus = list()
    if args.all:
        print("CrossVal mode set to \"all\"")
        crossVal_mode = "all"
    elif args.plus!=None:
        speakers_plus_minus = args.plus
        crossVal_mode = "+"
    elif args.minus!=None:
        speakers_plus_minus = args.minus
        crossVal_mode = "-"
    else:
        print("\nNo argument indicated. CrossVal mode set to \"all\"")
        crossVal_mode = "all"
    # end if

    # Features
    features_list = list()
    if args.feats==None:
        print("\nNo features indicated. Using only mfcc")
        features_list = list(['mfcc'])
    else:
        features_list = args.feats
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
    result_reformat = 'results/reformat/'
    #    result_amal= 'results_AMAL/'
    #    result_spk_raw= 'results/raw/'
    #    global_spk = 'results/global_spk.txt'

    # Result filename path:
    resultFilename = 'resultIniciales'
    combined_features_path = 'combined_features';


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

    bashCommand = "rm -rf " + combined_features_path
    process = subprocess.Popen(bashCommand,shell=True)
    output, error = process.communicate()

    bashCommand = "mkdir " + combined_features_path
    process = subprocess.Popen(bashCommand,shell=True)
    output, error = process.communicate()

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
                if (f.startswith(excludedSpk) and (f.endswith(".kal") or f.endswith(".TextGrid"))):
                    shutil.move(os.path.join(info_train_path,f), info_test_path)
                # end if
            # end for

            # --------------------- NNET2 CROSS VAL --------------------------#
            # ----------------------------------------------------------------#

            bashCommand = "python3 run.py --train --test -f " + ' '.join(features_list)

            # bashCommand = "python3 run.py --test -f " + ' '.join(features_list)
            # bashCommand = "python3 run.py --train -f " + ' '.join(features_list)
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
            fileGlobal = open('results/global_spk', 'a')
            for i in range(0,num_lines-1):
                line = file.readline()
                fileGlobal.write(line)
            fileGlobal.close()

            # Save raw results and csv
            results_decode_path = 'exp/tri1/decode/scoring_kaldi/wer_details/'
            crossval_spk_functions.save_raw_result(results_decode_path)

        # end for
    except Exception as e:
        print("\n\n"+e)
        print("\nAn ERROR inside the code have occured: Moving back every file as in the initial state")

        # Move back all test files to train folder
        files = os.listdir(info_test_path)
        #for f in files:
        #    shutil.move(os.path.join(info_test_path,f), info_train_path)

    # end try
    for f in os.listdir(combined_features_path):
            os.remove(os.path.join(combined_features_path, f))

    print("\n---------------------------------------------------")
    print("---------------------------------------------------")
    print("       MAIN LOOP OF CROSS-VALIDATION FINISHED      ")
    print("---------------------------------------------------")
    print("---------------------------------------------------")

    # result_spk= 'results/'
    # result_reformat = 'results/reformat/'

    # Take .csv result and reformat for SPSS analysis
    for file in os.listdir(result_spk):
        if file.endswith(".csv"):
            bashCommand = "python3 result_reformat4.py " + os.path.join(result_spk,file) + " " + os.path.join(result_reformat,file[:-4])+'_reformat.csv'
            process = subprocess.Popen(bashCommand,shell=True)
            output, error = process.communicate()

    # Global results for SPSS
    # """ SE HA COMENTADO PARA HACER LOS CÁLCULOS POR PARTES """
    crossval_spk_functions.global_result_reformat(result_reformat)
    # """ SE HA COMENTADO PARA HACER LOS CÁLCULOS POR PARTES """

# end main


# ----------------------------- MAIN SECTION -------------------------------- #
if __name__ == "__main__":
   main(sys.argv)
# end if

