#!/usr/bin/env python3
#
# This script is part of crossval_spk_gmm and crossval_spk_nnet. It is used to store
# functions used by both scripts.
# crossval_spk_functions.py
#


import os
import csv
import shutil
import result_format
import pandas as pd

#import sys
#import ASICA
#import config
#import crossval_spk_functions



# ----------------------- FUNCTIONS  -----------------------------------------#

def clean_wave_files(train_spks_info, audio_path, no_kal_path):
    # clean_wave_files check if audio files in /audio/ have .kal file in infor_user/train/
    #   train_spks_info: list of .kal files in info_user/train
    #   audio_path: path with audio .wav files /audio/
    #   no_kal_path: path with audios with no .kal files asociated to them


    # If folder doesn't exist, then create it.
    if not os.path.isdir(no_kal_path):
        os.makedirs(no_kal_path)
        print("created folder: ", no_kal_path)

    # speakers_list has the id of speakers
    speakers_list = list()
    for spk in train_spks_info:
        speakers_list.append(spk[0:5])      # ----    Check this if your IDs are different from above
    speakers_list = list(set(speakers_list)) # unique values

    # Takes audio_path and moves every .wav file thats not in speakers_list to no_kal_path
    files = os.listdir(audio_path)
    for f in files:
        spk = f[0:5]    # ----    Check this if your IDs are different from above
        if spk not in speakers_list:
            shutil.move(os.path.join(audio_path,f), no_kal_path)
        # end if
    # end for

    # Check the other way around in case new .kal files are added to code
    files = os.listdir(no_kal_path)
    for f in files:
        spk = f[0:5]    # ----    Check this if your IDs are different from above
        if spk in speakers_list:
            shutil.move(os.path.join(no_kal_path,f), audio_path)
        # end if
    # end for

# end function


def check_kal_wav(audio_wav_list, file_kal_list):
    # check_kal_wav check if every audio .wav in audio_wav_list has it corresponding .kal file in file_kal_list
    #   audio_wav_list: audio .wav list from /audio/
    #   file_kal_list: .kal file list from info_user/train/
    #
    #   Output: it prints the list of missing audio files without .kal files

    list_missing_file=list();

    for wav in audio_wav_list:
        name_wav = wav[:-4] + '.kal'
        if name_wav not in file_kal_list:
            list_missing_file.append(name_wav)
        # end if
    #end for

    print(list_missing_file)

#end function


def global_result_reformat(result_reformat):
    # global_result_reformat takes every .csv file in results/reformat and merge in a single .txt file to SPSS
    #   result_reformat: path results/reformat/'

    file_global = result_reformat+'global_result_reformat.txt'
    if os.path.exists(file_global):
        os.remove(file_global)
    os.mknod(file_global)

    with open(file_global, "w") as output_file:
        # Open txt output and goes for every .csv file
        index_file = 0
        list_results = os.listdir(result_reformat)
        list_results.sort()

        # Make a list of all speakers unique
        speakers_list = list()
        for spk in list_results:
            speakers_list.append(spk[0:5])  # ----    Check this if your IDs are different from above
        # end for
        speakers_list = list(set(speakers_list))

        for file in list_results:
            if file.endswith(".csv") and (file[0:5] in speakers_list):
                with open(os.path.join(result_reformat,file), "r") as input_file:
                    # all rows are readed
                    index_row = 0
                    for row in csv.reader(input_file):
                        if not (index_row == 0 and index_file!=0): # if its not the first csv head is not saved
                            output_file.write(" ".join(row)+'\n')
                        # end if
                        index_row = index_row + 1
                    # end for row
                    speakers_list.remove(file[0:5])
                # end with
            index_file = index_file + 1
            # end if
        # end for
        output_file.close()
    # end with
# end global_result_reformat

def save_raw_result(results_decode_path):
    # Extract output
    #   results_decode_path = 'exp/nnet2/nnet2_simple/decode/scoring_kaldi/wer_details/'
    #   results_decode_path = 'exp/tri1/decode/scoring_kaldi/wer_details/'
    utt_results = open(results_decode_path+'per_utt','r')
    utt = utt_results.read()
    speaker_results = open(results_decode_path+'per_spk','r')
    spk = speaker_results.read()
    # print(spk)
    r = '\n--------------------------------------------------------------------\n'
    r = r + spk + r
    r = r + utt

    # l = lambda a : a.replace(' ', '')
    lines = spk.split('\n')
    lines = lines[1:-3]

    resume = pd.DataFrame(columns=('Speaker ID', 'Accuracy'))
    for iline in list(range(0,len(lines),2)):
        line = lines[iline+1]

        items = line.split(' ')

        x = lambda a : a.replace(' ', '')
        items = list(map(x, items))
        good_Items = []
        for item in items:
            if item != '':
                good_Items.append(item)
        items = good_Items
        speaker = items[0]
        accuracy = items[4]
        resume.loc[iline] = [speaker] + [accuracy]

        output = open('results/raw/'+speaker+'_raw.txt','+w')
        output.write(r)

        result_format.extract_results(True, speaker)
    return speaker
# end save_raw_result


def results_ml_al(speaker_id,mode):
    # AM AL model is modified in file /local/score.sh min_lmwt y max_lmwt.
    # It limits the inverse of AM weight, i.e: higher lmwt means high influence of ML language model

    df = pd.DataFrame(columns=('Speaker ID', 'AMAL', 'WInst', 'WER', 'Ins', 'Del', 'Sub'))
    path = ''
    if mode == 'gmm':
        path = 'tri1'
    elif mode == 'nnet':
        path = 'nnet2/nnet2_simple'

    wer_path = 'exp/' + path +'/decode/'
    wer_best_path = 'exp/' + path + '/decode/scoring_kaldi/'
    save_csv_path = 'results_AMAL/'

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


    # Last row of data is the best_wer
    txt = open(os.path.join(wer_best_path,"best_wer"), "r")
    wer_txt = txt.readline()
    wer_txt = wer_txt.replace('/', ' ')
    wer_txt = wer_txt.split()

    # Take all data
    Speaker_ID_data = speaker_id + "_best_wer"
    AMAL_data = float(wer_txt[-1][4:-4])
    WInst_data = float(wer_txt[-1][-3:])

    WER_data = float(wer_txt[1])
    Ins_data = float(wer_txt[5])
    Del_data = float(wer_txt[7])
    Sub_data = float(wer_txt[9])

    df = df.append({'Speaker ID' : Speaker_ID_data, 'AMAL' : AMAL_data, 'WInst' : WInst_data, 'WER' : WER_data, 'Ins' : Ins_data, 'Del' : Del_data, 'Sub' : Sub_data} , ignore_index=True)

    # Save dataFrame as csv in save_csv_path
    df.to_csv(path_or_buf=os.path.join(save_csv_path,speaker_id+"_wer.csv"),index=False)
# end results_ml_al













