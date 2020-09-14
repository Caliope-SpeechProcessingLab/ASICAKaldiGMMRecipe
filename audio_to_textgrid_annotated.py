#!/usr/bin/env python3
#
# This script takes an audio file and annotates it automatically in kaldi .kal
# format and .TextGrid praat format.
#
# Folder prerequisistes:
#   audio/experiment_lm/    contains audio data for training Kaldi
#   info_user/test/         must be empty
#   info_user/train/        contains .kal files for training Kaldi
#   audio_no_annotated/     audio files with no .kal associated to be automatically annotated
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
# Use:
#   python3 audio_to_textgrid_annotated.py train    trains the model and performs annotation
#   python3 audio_to_textgrid_annotated.py test     only performs annotation
#
#
# Outputs:
#   audio/experiment_lm/no_kal_audio/       folder with all audio files in audio/experiment_lm with no .kal in info_user/train
#   audio_annotated/kaldi_annotated         .kal files annotated
#   audio_annotated/textgrid_annotated      .TextGrid files annotated
#
# IMPORTANT: After annotation, .TextGrid files must be reviwed manually and reconvert to .kal files for ensuring accuracy.
#
# Packages:
#   pandas:         pip3 install pandas
#   parselmouth:    pip3 install praat-parselmouth
#       https://github.com/YannickJadoul/Parselmouth
#       https://billdthompson.github.io/assets/output/Jadoul2018.pdf
#
# Funtion to interrupt program with CTRL-C
#

import os
import re
import sys
import shutil
import subprocess
import parselmouth
from parselmouth.praat import call
#import pandas as pd
#import result_format
import crossval_spk_functions

# ----------------------------- FUNCTIONS  ---------------------------------- #
def create_data_path(path_name):
    """Takes path_name and create a folder with that path. If exits, removes it before creation.

    :param path_name: name of the path to create.
    :returns: None.
    """
    if os.path.exists(path_name):
        shutil.rmtree(path_name)
    # end if
    os.makedirs(path_name)
#end create_data_path


def audio_to_textgrid(audio_no_annot_path, textgrid_path):
    """Generates .TextGrid files from audio using Praat.

    :param audio_no_annot_path: path with audio not annotated.
    :param textgrid_path: path with textgrid generated.
    :returns: None.
    """
    create_data_path(textgrid_path)

    audio_files = os.listdir(audio_no_annot_path)
    print("Procesing " + str(len(audio_files)) + " audio files with Praat, can take a while...")

    data_mod = round(len(audio_files)/10)
    index_mod = 1

    for audio in audio_files:

        sound = parselmouth.Sound(os.path.join(audio_no_annot_path, audio))

        # Take each audio file and convert to textGrid with praat
        noise_reduction = call(sound, "Remove noise", 0.0, 1.0, 0.025, 80, 10000, 40, 'Spectral subtraction') # 'silent', 'sounding'
        manipulation = call(noise_reduction, "To TextGrid (silences)", 100, 0.0, -65.0, 0.8, 0.2, '', 'sounding') # 'silent', 'sounding'   # 0.8, 0.2
                                                                                       # minimun silent and sound intervals
        text_audio = audio[:-4] + '.TextGrid'
        call(manipulation, "Save as text file", os.path.join(textgrid_path, text_audio))

        # Show progresion
        try:
            if index_mod % data_mod == 0:  # it means 10%, 20%, ...
                print(str(int(index_mod/data_mod * 10))+"% ",end="\r")
        except:
            print('',end="\r")
        #end try
        index_mod += 1
    # end for

    # Modelate audio and make corrections to TextGrid created
    # !!: separation_between_words gives the times between word, i.e. duration of the silences
    #    separation_between_words = modelate_audio(info_user_train_path)
    #
    #    mean_sepa = np.mean(separation_between_words)
    #    std_sepa = np.std(separation_between_words)
    #    min_separation_silences = mean_sepa - 3*std_sepa
# end audio_to_textgrid


def modelate_audio(path_name):
    """Takes a path with manually generated kaldi files and calculates diferent metric.

    :param path_name: path with audio not annotated.
    :param textgrid_path: path with annotations.
    :returns separation_between_words: Separations between words in order to identify wrong silents.
    """
    # path_name = info_user_train_path

    # Calculate separation between words in order to identify wrong silents
    separation_between_words = []    # save length of 'sounding' period separation
    # kal_file ='CA562QL1_H50.kal'
    for kal_file in os.listdir(path_name):
        if kal_file.endswith('.kal') and not kal_file.endswith("00.kal"):
            kaldi_text = open(os.path.join(path_name, kal_file))
            kaldi_text = kaldi_text.read()
            kaldi_text = re.split(r'[\n\t]+', kaldi_text)

            if kaldi_text[-1] == '':    # check if last field is empty
                kaldi_text = kaldi_text[:-1]

            num_words = len(kaldi_text)/4

            for i in range(int(num_words)-1):
                separation_between_words.append(float(kaldi_text[(i+1)*4]) - float(kaldi_text[i*4]))
         # end if
    # end for

    return separation_between_words
# end modelate_audio


def textgrid_to_kal(textgrid_path, kaldi_path):
    """Takes textgrid and convert to kal.

    :param textgrid_path: path with textgrid annotations.
    :param kaldi_path: folder when saving kaldi files.
    :returns: None.
    """
    create_data_path(kaldi_path)

    for file in os.listdir(textgrid_path):

        textgrid_file = open(os.path.join(textgrid_path, file))
        kaldi_file = open(os.path.join(kaldi_path, file[:-9]+".kal"),'a')

        # Variables for textgrid structure
        line_kaldi = list()
        actual = []
        prev = []
        prev_prev = []

        for i, line in enumerate(textgrid_file):
            # refresh variable values
            prev_prev = prev
            prev = actual
            actual = line

            if "sounding" in actual:
                # Found "sounding" text
                time_start = prev_prev.split()
                line_kaldi.append(time_start[-1] + '\t')

                time_end = prev.split()
                line_kaldi.append(time_end[-1] + '\t')

                line_kaldi.append("so so so\t")
                line_kaldi.append("s_o s_o s_o\n")

                # Write in text and delete list
                kaldi_file.writelines(line_kaldi)
                line_kaldi = list()
            # end if
        # end for
        textgrid_file.close()
        kaldi_file.close()
    # end for
# end textgrid_to_kal


def results_to_kal_annot(results_raw_path,kaldi_path,kaldi_annotated_path):
    """Save results to kaldi format file annotations.

    :param results_raw_path: folder with results/raw after testing.
    :param kaldi_path: folder with kaldi files.
    :param kaldi_annotated_path: folder when saving kaldi files.
    :returns: None.
    """
    create_data_path(kaldi_annotated_path)

    for file in os.listdir(results_raw_path):

        raw_file = open(os.path.join(results_raw_path, file))
        kal_file = open(os.path.join(kaldi_path, file[:-8]+".kal"),'r')
        kal_annotated_file = open(os.path.join(kaldi_annotated_path, file[:-8]+".kal"),'a')

        list_kal_annotated = [None] * sum(1 for line in open(os.path.join(kaldi_path, file[:-8]+".kal"),'r'))

        kal_lines = kal_file.readlines()
        for i, line in enumerate(raw_file):
            if "hyp" in line :

                word_kaldi = line.split()
                word_kaldi = word_kaldi[2:]

                line_index = line.replace('hyp', '   ')
                line_index = line_index.replace(file[:-8]+'-utt', '')
                line_index = int(line_index[:4])
                # print(line_index)

                line_kal_file = kal_lines[line_index]

                # Fix manuaaly the letters to avoid symbols like ' " [ ] ...
                line_to_file = ''
                for words in word_kaldi:
                    if words != "***":    # ***
                        line_to_file = line_to_file + words + ' '
                line_to_file = line_to_file[:-1]
                line_kal_file = line_kal_file.replace('so so so', line_to_file)

                vowels = ['a','e','i','o','u']
                vowels_mod = ['_a','_e','_i','_o','_u']
                for i in range(0,len(vowels)):
                    line_to_file = line_to_file.replace(vowels[i],vowels_mod[i])

                line_kal_file = line_kal_file.replace('s_o s_o s_o', line_to_file)

                list_kal_annotated[line_index] = line_kal_file
            # end if
        # end for
        list_kal_annotated = list(filter(None, list_kal_annotated))

        for line in list_kal_annotated:
            kal_annotated_file.write(line)

    raw_file.close()
    kal_file.close()
    kal_annotated_file.close()
    # end for
# end results_to_kal_annot


def kal_annot_to_textgrid_annot(kaldi_annotated_path, textgrid_path, textgrid_annotated_path):
    """Save annotations in kaldi format to textgrid format.

    :param kaldi_annotated_path: path to kaldi annotations folder.
    :param textgrid_path: textgrid orginal path.
    :param textgrid_annotated_path: textgrid with annotated path.
    :returns: None.
    """
    create_data_path(textgrid_annotated_path)

    for file in os.listdir(kaldi_annotated_path):
        # file = 'MA800_M28_NAT.kal'

        kaldi_annotated_file = open(os.path.join(kaldi_annotated_path, file))
        word_kaldi = kaldi_annotated_file.readlines()

        kaldi_annotated_file_tier2 = open(os.path.join(kaldi_annotated_path, file))
        fonol_kaldi = kaldi_annotated_file_tier2.readlines()

        textgrid_file = open(os.path.join(textgrid_path, file[:-4]+".TextGrid"),'r')
        textgrid_annotated_file = open(os.path.join(textgrid_annotated_path, file[:-4]+".TextGrid"),'w')

        tier2 = list()
        line_aux = ""
        line_aux_tier2 = ""
        prev = ""
        prev_prev = ""
        for i, line in enumerate(textgrid_file):
            prev_prev = prev
            prev = line_aux
            line_aux = line
            line_aux_tier2 = line

            # Need to create another file with tier2
            if i > 7:
                if "sounding" in line:
                    fon_kaldi = fonol_kaldi.pop(0)
                    fon_kaldi_aux = fon_kaldi.split()

                    if len(fon_kaldi_aux)>1:
                        t1 = float(fon_kaldi_aux[0])
                        t2 = float(fon_kaldi_aux[1])
                    # end if

                    fon_kaldi_aux = fon_kaldi_aux[-int((len(fon_kaldi_aux)-2)/2):]

                    # Fix manuaaly the letters to avoid symbols like ' " [ ] ...
                    line_to_file = ''
                    for words in fon_kaldi_aux:
                        line_to_file = line_to_file + words + ' '
                    line_to_file = line_to_file[:-1]

                    t1_prev_prev = float(prev_prev.split()[2])

                    if t1 == t1_prev_prev or t2 == t1_prev_prev:
                        tier2.append(line_aux_tier2.replace('sounding', line_to_file))
                    else:
                        tier2.append(line_aux_tier2.replace('sounding', ""))
                        fonol_kaldi.insert(0,fon_kaldi)
                    # end if
                elif "silences" in line:
                    tier2.append(line_aux_tier2.replace('silences', "fonol."))
                elif "item [1]" in line:
                    tier2.append(line_aux_tier2.replace('item [1]', "item [2]"))
                else:
                    tier2.append(line_aux_tier2)
            # end if i > 7

            if "sounding" in line:
                w_kaldi = word_kaldi.pop(0)
                w_kaldi_aux = w_kaldi.split()

                if len(w_kaldi_aux)>1:
                        t1 = float(w_kaldi_aux[0])
                        t2 = float(w_kaldi_aux[1])
                    # end if
                w_kaldi_aux = w_kaldi_aux[2:2+int((len(w_kaldi_aux)-2)/2)]

                # Fix manuaaly the letters to avoid symbols like ' " [ ] ...
                line_to_file = ''
                for words in w_kaldi_aux:
                    line_to_file = line_to_file + words + ' '
                line_to_file = line_to_file[:-1]

                t1_prev_prev = float(prev_prev.split()[2])

                if t1 == t1_prev_prev or t2 == t1_prev_prev:
                    textgrid_annotated_file.write(line_aux.replace('sounding', line_to_file))
                else:
                    textgrid_annotated_file.write(line_aux.replace('sounding', ""))
                    word_kaldi.insert(0,w_kaldi)
                # end if
            elif "silences" in line:
                textgrid_annotated_file.write(line_aux.replace('silences', "Transcripción"))
            elif "size = 1" in line and (line>="size = 1"):
                #print(line)
                textgrid_annotated_file.write(line_aux.replace('1', "2"))
            else:
                textgrid_annotated_file.write(line_aux)
           # end if
        # end for

        for line in tier2:
            textgrid_annotated_file.write(line)

        kaldi_annotated_file.close()
        textgrid_file.close()
        textgrid_annotated_file.close()
    # end for
# end kal_annot_to_textgrid_annot


def fix_kal_annot(kaldi_annotated_path):
    """Takes a list of words and correct the words kaldi understood.

    :param kaldi_annotated_path: path to kaldi annotations folder.
    :returns: None.
    """

    words = ['sa te li te', 'ma nya na', 'ka rro nya', 'bi ga', 'ko li ya', 'ma re xa da', 'pe so', 'la do', 'ka rro ma to', 'di ne ro', 'mo te', 'ko da', 'no che', 'ka yo', 'ka pi tu lo', 'ba ye', 'so ga', 'ko pa', 'mu lo', 'zi ma', 'be na', 'mu si ka', 'fi lo so fo', 'mi ri ya', 'ma ni be la', 'lu cha', 'lo na', 'bu ke', 'ye ma', 'ma no ta zo', 'pe ta ka', 'ka mi no', 'so da', 'ka nyo', 'ge rra', 'no be la', 'la ti ga zo', 'rro ka', 'ze bo', 'pa li yo', 'pe na', 'bi ya', 'rre ti ra da', 'me di zi na', 'ya te', 'ti tu lo', 'pa le ti ya', 'chu lo', 'li ga', 'nu me ro', 'tu fo', 'fe cha', 'ka ba ye te', 'gi nyo', 'zi ne', 'se nyo ri ta', 'pe li ku la', 'to rre', 'ba rre nyo', 'ta le go']

    words2 = ['s_a t_e l_i t_e', 'm_a ny_a n_a', 'k_a rr_o ny_a', 'b_i g_a', 'k_o l_i y_a', 'm_a r_e x_a d_a', 'p_e s_o', 'l_a d_o', 'k_a rr_o m_a t_o', 'd_i n_e r_o', 'm_o t_e', 'k_o d_a', 'n_o ch_e', 'k_a y_o', 'k_a p_i t_u l_o', 'b_a y_e', 's_o g_a', 'k_o p_a', 'm_u l_o', 'z_i m_a', 'b_e n_a', 'm_u s_i k_a', 'f_i l_o s_o f_o', 'm_i r_i y_a', 'm_a n_i b_e l_a', 'l_u ch_a', 'l_o n_a', 'b_u k_e', 'y_e m_a', 'm_a n_o t_a z_o', 'p_e t_a k_a', 'k_a m_i n_o', 's_o d_a', 'k_a ny_o', 'g_e rr_a', 'n_o b_e l_a', 'l_a t_i g_a z_o', 'rr_o k_a', 'z_e b_o', 'p_a l_i y_o', 'p_e n_a', 'b_i y_a', 'rr_e t_i r_a d_a', 'm_e d_i z_i n_a', 'y_a t_e', 't_i t_u l_o', 'p_a l_e t_i y_a', 'ch_u l_o', 'l_i g_a', 'n_u m_e r_o', 't_u f_o', 'f_e ch_a', 'k_a b_a y_e t_e', 'g_i ny_o', 'z_i n_e', 's_e ny_o r_i t_a', 'p_e l_i k_u l_a', 't_o rr_e', 'b_a rr_e ny_o', 't_a l_e g_o']

    for file in os.listdir(kaldi_annotated_path):

        kal_file = open(os.path.join(kaldi_annotated_path, file),"r")
        list_of_lines = kal_file.readlines()

        # file = 'MA800_M28_NAT.kal'
        # lines = list_of_lines[54]
        # index = 54

        index = 0
        for lines in list_of_lines:
            l = lines.split('\t')
            if len(list_of_lines)>len(words) and len(l[2].split(' '))<2: # l[2] == "" or
                error = list_of_lines.pop(index)
                #print(error)
                #print(index)
            else:
                if l[2] != words[index]:
                    l[2] = words[index]
                    l[3] = words2[index]+'\n'

                    list_of_lines[index] = '\t'.join(l)
                # end if
            index = index + 1
        # end for

        kal_file = open(os.path.join(kaldi_annotated_path, file),"w")
        kal_file.writelines(list_of_lines)
        kal_file.close()
# end fix_kal_annot


def main(argv):
    """Main script

    :param argv: arguments of script.
    :returns: None.
    """

    # ----------------------- ARGUMENT PARSING -------------------------------#
    modeTrain = True
    if len(sys.argv) == 1:
        print("\nNo argument indicated. Kaldi ASR is performing train.\n")
    elif sys.argv[1] == 'test':
        modeTrain = False
    else:
        print("\nWrong argument indicated. Kaldi ASR is performing train.\n")
    # end if


    # Path path with data
    audio_path = 'audio/experiment_lm'
    no_kal_path = 'audio/experiment_lm/no_kal_audio'
    audio_no_annot_path = 'audio_no_annotated'    # audio files to be annotated
    audio_annot_path = 'audio_annotated'          # audio files to be annotated

    textgrid_path = os.path.join(audio_annot_path,'textgrid')                       # textgrid generated by praat
    kaldi_path = os.path.join(audio_annot_path,'kaldi')                             # kaldi from praat
    results_raw_path = 'results/raw'
    kaldi_annotated_path = os.path.join(audio_annot_path,'kaldi_annotated')         # kal generated by kaldi
    textgrid_annotated_path = os.path.join(audio_annot_path,'textgrid_annotated')

    info_user_test_path = 'info_user/test'
    info_user_train_path = 'info_user/train'


    # Check for audio files with no .kal
    train_spks_info = list()
    for file in os.listdir(info_user_train_path):
        if file.endswith(".kal") and not(file.startswith(".")) and not(file.startswith("_")):
            train_spks_info.append(file)
    crossval_spk_functions.clean_wave_files(train_spks_info, audio_path, no_kal_path)


    # path to save results
    create_data_path(audio_annot_path)
    create_data_path(results_raw_path)


    # From audio .wav to .TextGrid with praat
    audio_to_textgrid(audio_no_annot_path, textgrid_path)

    # From .TextGrid to .kal
    textgrid_to_kal(textgrid_path, kaldi_path)


    # If train is indicated we train the GMM/Nnet defined in the path

    # Copy audio no-annotated into audio path
    audio_list = os.listdir(audio_no_annot_path)
    for f in audio_list:
        shutil.copy(os.path.join(audio_no_annot_path,f), audio_path)
    crossval_spk_functions.clean_wave_files(train_spks_info, audio_path, no_kal_path)

    # Train model if indicated
    if modeTrain:
        bashCommand = "python3 run.py --train"
        process = subprocess.Popen(bashCommand,shell=True)
        output, error = process.communicate()

    # Test after training using
    # Copy kal generated to info_user/test
    kal_list = os.listdir(kaldi_path)
    for f in kal_list:
        # f = 'MA803_NAT_H28.kal'
        # Move audio and .kal file to make test
        shutil.copy(os.path.join(kaldi_path,f), info_user_test_path)
        shutil.copy(os.path.join(no_kal_path,f[:-3]+'wav'), audio_path)

        bashCommand = "python3 run.py --test"
        process = subprocess.Popen(bashCommand,shell=True)
        output, error = process.communicate()

        # Result format from raw
        #results_decode_path = 'exp/tri1/decode/scoring_kaldi/wer_details/'

        try:
            results_decode_path = 'exp/nnet2/nnet2_simple/decode/scoring_kaldi/wer_details/'
            speaker = crossval_spk_functions.save_raw_result(results_decode_path)
        except:
            results_decode_path = 'exp/tri1/decode/scoring_kaldi/wer_details/'
            speaker = crossval_spk_functions.save_raw_result(results_decode_path)

        # result_format.extract_results(True, speaker)
        os.remove(os.path.join(info_user_test_path,f))
        os.remove(os.path.join(audio_path,f[:-3]+'wav'))
    # end for


    # Delete audio and kal moved previous
    for f in audio_list:
        # os.remove(os.path.join(audio_path,f))
        os.remove(os.path.join(no_kal_path,f))

    # From results/raw to kaldi annotated
    results_to_kal_annot(results_raw_path,kaldi_path,kaldi_annotated_path)

    fix_kal_annot(kaldi_annotated_path)

    # From kaldi annotated to textgrid annotated
    kal_annot_to_textgrid_annot(kaldi_annotated_path, textgrid_path, textgrid_annotated_path)

# end main


# ----------------------------- MAIN SECTION -------------------------------- #
if __name__ == "__main__":
   main(sys.argv)
# end if









