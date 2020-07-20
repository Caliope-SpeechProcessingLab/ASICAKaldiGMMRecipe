#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Created on Mon Apr 20 11:10:24 2020
#
# @author: Andrés Lozano Durán
#
#This script is used to split audio and kal file in words and pseudowords (easy and difficult). This is made in order to train the ASR system with words spoken by the speakers. The test is only donde with pseudowords in cross validation.
#
# Audio and kal file can be split in two or three classes.
#
# Audio files must be placed in kaldi/.../audio/experimentln
# Kal files must be placed in  kaldi/.../info_user/train
#
# python3 split_words.py

import os
import sys
import shutil
import crossval_spk_functions

# --------------------------- FUNCTIONS  ------------------------------------ #

def duplicate_kal(info_train_path,spks_info,id_word,new_id_easy,new_id_hard,words,pseudowords_easy,pseudowords_hard):
    """Duplicate annotation .kal files with new names.

    :param info_train_path: Annotation path for kaldi/.../info_user/train.
    :param spks_info: A list with all .kal files names.
    :param id_word: A list with new index for words.
    :param new_id_easy: A list with new index for pseudowords labelled as easy.
    :param pseudo_hard: A list with new index for pseudowords labelled as hard.
    :returns: None, duplicate files in folder.
    """
    # spks_info = train_spks_info  --> PALABRAS

    if len(new_id_easy)>0: new_id_easy = new_id_easy * int(len(spks_info)/len(new_id_easy))
    if len(new_id_hard)>0: new_id_hard = new_id_hard * int(len(spks_info)/len(new_id_hard))
    if len(id_word)>0: id_word = id_word * int(len(spks_info)/len(id_word))
    new_id_easy.sort()
    new_id_hard.sort()
    id_word.sort()

    index = 0
    id_pseudo_easy = list()
    id_pseudo_hard = list()
    id_word_list = list()

    for file in spks_info:
        if file.endswith(".kal") and not(file.startswith(".")) and not(file.startswith("_")):

            if len(new_id_easy)>0:
                new_name = new_id_easy[index] + file[5:]
                dest_dir = info_train_path + "/" + new_name
                try: shutil.copy(os.path.join(info_train_path,file),dest_dir)
                except: 0
                id_pseudo_easy.append(new_name)
            # end if

            if len(new_id_hard)>0:
                new_name = new_id_hard[index] + file[5:]
                dest_dir = info_train_path + "/" + new_name
                try: shutil.copy(os.path.join(info_train_path,file),dest_dir)
                except: 0
                id_pseudo_hard.append(new_name)
            # end if

            if len(id_word)>0:
                new_name = id_word[index] + file[5:]
                dest_dir = info_train_path + "/" + new_name
                try: shutil.copy(os.path.join(info_train_path,file),dest_dir)
                except: 0
                id_word_list.append(new_name)
            # end if

            index = index + 1
        # end if
    # end for

    for file in os.listdir(info_train_path):
        if file.endswith(".kal") and not(file.startswith(".")) and not(file.startswith("_")):

            if file in id_word_list:
                # se trata de una palabra
                rewrite_kal(os.path.join(info_train_path,file),words)
            elif file in id_pseudo_easy:
                # se trata de una pseudopalabra fácil
                rewrite_kal(os.path.join(info_train_path,file),pseudowords_easy)
            elif file in id_pseudo_hard:
                # se trata de una pseudopalabra dificil
                rewrite_kal(os.path.join(info_train_path,file),pseudowords_hard)
            # end if

        # end if
    # end for

# end duplicate_kal


def rewrite_kal(file,word_list):
    """Reqrite file saving words in word_list

    :param file: Path to .kal file.
    :param word_list: A list of words to SAVE.
    :returns: None, modifies files in folder.
    """

    # First, open the file and get all your lines from the file.
    with open(file, "r") as f:
        lines = f.readlines()
    # end with

    # Then reopen the file in write mode and write your lines back, except for the line you want to delete:
    with open(file, "w") as f:
        for line in lines:
            values = line.split("\t")
            if values[2] in word_list:
                f.write(line)
            # end if
        # end for
    # end with

# def rewrite_kal


def duplicate_audio(audio_path,spks_audio,id_word,new_id_easy,new_id_hard):
    """Duplicate audio .wav files with new names.

    :param audio_path: Audio path for kaldi/.../audio/experimentln
    :param spks_audio: A list with names for .wav audio files
    :param id_word: A list with new index for words.
    :param new_id_easy: A list with new index for pseudowords labelled as easy.
    :param pseudo_hard: A list with new index for pseudowords labelled as hard.
    :returns: None, duplicate files in folder.
    """

    if len(new_id_easy)>0: new_id_easy = new_id_easy * int(len(spks_audio)/len(new_id_easy))
    if len(new_id_hard)>0: new_id_hard = new_id_hard * int(len(spks_audio)/len(new_id_hard))
    if len(id_word)>0: id_word = id_word * int(len(spks_audio)/len(id_word))
    new_id_easy.sort()
    new_id_hard.sort()
    id_word.sort()

    index = 0

    for file in spks_audio:
        if file.endswith(".wav") and not(file.startswith(".")) and not(file.startswith("_")):
            if len(new_id_easy)>0:
                new_name = new_id_easy[index] + file[5:]
                dest_dir = audio_path + "/" + new_name
                try: shutil.copy(os.path.join(audio_path,file),dest_dir)
                except: 0

            if len(new_id_hard)>0:
                new_name = new_id_hard[index] + file[5:]
                dest_dir = audio_path + "/" + new_name
                try: shutil.copy(os.path.join(audio_path,file),dest_dir)
                except: 0

            if len(id_word)>0:
                new_name = id_word[index] + file[5:]
                dest_dir = audio_path + "/" + new_name
                try: shutil.copy(os.path.join(audio_path,file),dest_dir)
                except: 0

            index = index + 1
        # end if
    # end for

# end duplicate_audio


def create_new_id(speakers_list, pseudo_easy, pseudo_hard, objetive):
    """Generate new id for audio and kal name.

    :param speakers_list: A list with all speakers' names, e.g.: 'CA001', 'CA101', ...
    :param pseudo_easy: A list with pseudowords labelled as easy.
    :param pseudo_hard: A list with pseudowords labelled as hard.
    :param objetive: A string with ('word' 'easy' 'hard') value for selecting target in testing. For naming tracability
    :returns: Three list with numerical index of new files.
    """

    redux_spk = list()
    new_spk_id = list()
    new_spk_id_easy = list()
    new_spk_id_hard = list()

    for spk in speakers_list:
        redux_spk.append(spk[2:5])
    # end for
    # redux_spk.sort()

    possible_id = ["{0:03}".format(i) for i in range(1,999)]

    new_spk_id = [x for x in possible_id if x not in redux_spk]
    if len(pseudo_easy)>0: new_spk_id_easy = new_spk_id[0:len(speakers_list)]
    if len(pseudo_hard)>0: new_spk_id_hard = new_spk_id[-len(speakers_list):]

    if objetive=='hard':
        # If obtejive for testing is hard change names
        spk_aux = new_spk_id_hard
        new_spk_id_hard = redux_spk
        redux_spk = spk_aux
    elif objetive=='easy':
        spk_aux = new_spk_id_easy
        new_spk_id_easy = redux_spk
        redux_spk = spk_aux
    # end if

    # Modify names
    index = 0
    for spk in speakers_list:
        redux_spk[index] = spk[0:2] + redux_spk[index]
        if len(pseudo_easy)>0: new_spk_id_easy[index] = spk[0:2] + new_spk_id_easy[index]
        if len(pseudo_hard)>0: new_spk_id_hard[index] = spk[0:2] + new_spk_id_hard[index]
        index = index + 1
    # end for

    return redux_spk, new_spk_id_easy, new_spk_id_hard
# end create_new_id


def main(argv):

    # -------------------------- USER VARIABLES ----------------------------- #
    words = ["ba rre nyo", "bu ke", "ka ba ye ro", "ka ba ye te", "ka yo", "ka mi no", "ka nyo", "ka pi tu lo", "ka rro ma to", "ka rro nya", "ze bo", "chu lo", "zi ma", "zi ne", "ko li ya", "ko pa", "de ba te", "di ne ro", "fe cha", "fi lo so fo", "ge rra", "gi nyo", "xe ta", "la do", "la ti ga zo", "li ga", "lo na", "lu cha", "ma ni be la", "ma no ta zo", "ma nya na", "ma re xa da", "me ze do ra", "me di zi na", "mi ri ya", "mo te", "mu lo", "mu si ka", "no che", "no be la", "nu me ro", "pa le ti ya", "pa li yo", "pe li ku la", "pe na", "pe so", "pe ta ka", "pe ta te", "rre ti ra da", "rro ka", "sa te li te", "se nyo ri ta", "so da", "so ga", "ta le go", "ti tu lo", "to rre", "tu fo", "ba ye", "be na", "bi ga", "bi ya", "ya te", "ye ma"]

    pseudowords_easy = ["ba rre yo", "bu de", "ka ba ye mo", "ka ba ye to", "ka xo", "ka yi", "ka mi ro", "ka pi tu bo", "ka rro fa", "ka rro ma do", "ze bi", "chu so", "zi da", "zi se", "ko da", "ko li za", "de ba ti", "di ne so", "fe za", "fi lo so zo", "ge za", "gi cho", "xe ra", "la ro", "la ti ga fo", "li ya", "lo ra", "lu xa", "ma ni be za", "ma no ta go", "ma nya da", "ma re xa za", "me ze do ta", "me di zi ra", "mi ri za", "mo de", "mu no", "mu si ma", "no fe", "no be ya", "nu me so", "pa le ti rra", "pa li xo", "pe li ku za", "pe no", "pe ta", "pe ta ma", "pe ta ti", "rre ti ra za", "rro ko", "sa te li to", "se nyo ri da", "so ya", "so ma", "ta le bo", "ti tu mo", "to ye", "tu zo", "ba fe", "be ta", "bi ka", "bi la", "ya to", "ye da", "be ya fe", "be yo lu", "bi fu pe si", "bu fe lu", "ka mo", "ka po di no", "zi bu fe ni", "zi fo", "ko zi", "ko di so", "ko ga", "ko pa di", "ko pa te", "ku fe", "ku xo ba", "di ku", "di ku li te", "di la", "di ma ko", "di ra ni", "do bu", "do fe", "do ya", "fe bu xo", "fe xi", "fo bo xe ma", "fu xo", "lo fe du ne", "lu fo", "ma po", "me la ni to", "me pe", "me po", "mo ku", "mo pa so ka", "mo pe", "mo pe di ta", "na fe", "ni fu ba mi", "ni gu", "ni bo fe ma", "no fe", "no fe ba", "no lu", "pa ba ri mo", "pa de so", "pa do", "pa ne", "pa ni", "pe ku ga ta", "pe mi", "rri bu po", "se ku", "so ga li na", "so ma zi", "so ri", "so te to", "ti bo", "ti bu", "ti fe du ne", "ti yo", "za fe lu di", "za lu", "za bo lu"]

    pseudowords_hard = []

    # .wav and .kal file paths:
    # !!: Audio files are in the same folder both training and testing, are selected based on info_user folders
    audio_path = 'audio/experiment_lm/'
    info_test_path = 'info_user/test/'
    info_train_path = 'info_user/train/'
    no_kal_path = 'audio/experiment_lm/no_kal_audio'


    # Move all test files in info_user/test to info_user/train folder
    for f in os.listdir(info_test_path):
        shutil.move(os.path.join(info_test_path,f), info_train_path)

    # Asses directory structure:
    train_spks_info = list()
    train_spks_audio = list()

    for file in os.listdir(info_train_path):
        if file.endswith(".kal") and not(file.startswith(".")) and not(file.startswith("_")):
            train_spks_info.append(file)

    # Clean and reorder audio files
    crossval_spk_functions.clean_wave_files(train_spks_info, audio_path, no_kal_path)

    for file in os.listdir(audio_path):
        if file.endswith(".wav") and not(file.startswith(".")) and not(file.startswith("_")):
            train_spks_audio.append(file)

    print("\n Estos archivos .kal faltan:")
    crossval_spk_functions.check_kal_wav(train_spks_audio, train_spks_info)

    # Search for unique speakers ID
    speakers_list = list()
    for spk in train_spks_info:
        speakers_list.append(spk[0:5])  # ----    Check this if your IDs are different from above
    # end for
    speakers_list = list(set(speakers_list))


    # ------------------------ GENERATING NEW AUDIOS ------------------------ #

    train_spks_audio.sort()
    speakers_list.sort()
    train_spks_info.sort()

    id_word, new_id_easy, new_id_hard = create_new_id(speakers_list,pseudowords_easy,pseudowords_hard,objetive='easy') # 'word' 'easy' 'hard'
    duplicate_audio(audio_path,train_spks_audio,id_word,new_id_easy,new_id_hard)
    duplicate_kal(info_train_path,train_spks_info,id_word,new_id_easy,new_id_hard,words,pseudowords_easy,pseudowords_hard)

    print("\n Speakers with Words:")
    print(id_word)

    print("\n Speakers with Pseudowords easy:")
    print(new_id_easy)

    print("\n Speakers with Pseudowords hard:")
    print(new_id_hard)


# end main



# ------------------------------- MAIN SECTION -------------------------------#

if __name__ == "__main__":
   main(sys.argv)
# end if




