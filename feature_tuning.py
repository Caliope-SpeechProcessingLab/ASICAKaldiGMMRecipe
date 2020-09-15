#!/usr/bin/env python3
#
# python3 feature_tuning.py
#
#


import os
import shutil
import subprocess
#import pandas as pd
#import result_format
import crossval_spk_functions
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math


# ----------------------------- FUNCTIONS  ---------------------------------- #
def ageGroup(edad):
    """Take edad and classifies acording to two possible classes.

    :param edad: age of speaker.
    :returns: ageGroup with value 2 or 5.
    """
    if edad in ["00","50","51","52","54","55","56","57"]:
        ageGroup="5"
    else:
        ageGroup="2"
    # end if
    return (ageGroup)
# end ageGroup


def split_spk(info_user_train_path):
    """Split spk list in train and test class according to class proporcionality

    :param info_user_train_path: path of train .kal files
    :returns: c_train, c_test with list of speakers name for each class.
    """

    list_spk = os.listdir(info_user_train_path)
    list_spk.sort()

    c_H2 = list()
    c_M2 = list()
    c_H5 = list()
    c_M5 = list()

    c_train = list()
    c_test = list()

    for spk in os.listdir(info_user_train_path):
        c =''
        age_group = ageGroup(spk[10:12])
        name = spk[:5]

        c = c+spk[9]
        c = c+age_group

        if c == 'H2':
            c_H2.append(name)
        elif c == 'M2':
            c_M2.append(name)
        elif c == 'H5':
            c_H5.append(name)
        elif c == 'M5':
            c_M5.append(name)
        # end if
    # end for

    c_H2 = list(set(c_H2))
    c_M2 = list(set(c_M2))
    c_H5 = list(set(c_H5))
    c_M5 = list(set(c_M5))

    c_train.extend(c_H2[:int(len(c_H2)/2)])
    c_test.extend(c_H2[int(len(c_H2)/2):])

    c_train.extend(c_M2[:int(len(c_M2)/2)])
    c_test.extend(c_M2[int(len(c_M2)/2):])

    c_train.extend(c_H5[:int(len(c_H5)/2)])
    c_test.extend(c_H5[int(len(c_H5)/2):])

    c_train.extend(c_M5[:int(len(c_M5)/2)])
    c_test.extend(c_M5[int(len(c_M5)/2):])

    return c_train, c_test
# end split_spk


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


def total_accuracy(data,feature_list,values_features,path):
    ## Aciertos en general
    values_int = [int(x) for x in values_features]
    spk_list = list(set(list(data["Speaker ID"])))

    accuracy = list()
    for values in values_int:
        mean_spk = list()
        for spk in spk_list:
            mean_aux = np.mean(data.loc[(data["Value"] == values) & (data["Speaker ID"] == spk), ["Correct"]])
            if not math.isnan(mean_aux):
                mean_spk.append(mean_aux)
            # end if
        # end for spk
        accuracy.append(np.mean(mean_spk))
    # end for values

    plt.figure(num=None, figsize=(16, 12), dpi=120, facecolor='w', edgecolor='k')
    plt.stem(values_int,accuracy)
    plt.ylabel('Accuracy')
    plt.xlabel('Valor parámetro '+feature_list)
    plt.title('Accuracy total, max='+str(np.round(np.max(accuracy),2))+' '+feature_list+'='+str(values_int[accuracy.index(max(accuracy))]))
    plt.grid()
    #plt.show()
    plt.ylim(0,1)
    plt.savefig(os.path.join(path,'accuracy total.png'))
    plt.close()
# end total_accuracy


def sex_accuracy(data,feature_list,values_features,path,l_sex):
    ## Aciertos en general
    values_int = [int(x) for x in values_features]
    spk_list = list(set(list(data["Speaker ID"])))

    accuracy = list()
    for values in values_int:
        mean_spk = list()
        for spk in spk_list:
            if l_sex == 'H':
                mean_aux = np.mean(data.loc[(data["Value"] == values) & (data["Sex"] == l_sex) & (data["Speaker ID"] == spk), ["Correct"]])
            elif l_sex == 'M':
                mean_aux = np.mean(data.loc[(data["Value"] == values) & (data["Sex"] == l_sex) & (data["Speaker ID"] == spk), ["Correct"]])
            # end if
            if not math.isnan(mean_aux):
                mean_spk.append(mean_aux)
            # end if
        # end for spk
        accuracy.append(np.mean(mean_spk))
    # end for values

    plt.figure(num=None, figsize=(16, 12), dpi=120, facecolor='w', edgecolor='k')
    plt.stem(values_int,accuracy)
    plt.ylabel('Accuracy')
    plt.xlabel('Valor parámetro '+feature_list)
    plt.grid()
    plt.ylim(0,1)
    if l_sex == 'H':
        plt.title('Accuracy hombres, max='+str(np.round(np.max(accuracy),2))+' '+feature_list+'='+str(values_int[accuracy.index(max(accuracy))]))
        plt.savefig(os.path.join(path,'accuracy hombres.png'))
    elif l_sex == 'M':
        plt.title('Accuracy mujeres, max='+str(np.round(np.max(accuracy),2))+' '+feature_list+'='+str(values_int[accuracy.index(max(accuracy))]))
        plt.savefig(os.path.join(path,'accuracy mujeres.png'))
    # end if
    #plt.show()
    plt.close()
# end sex_accuracy


def age_accuracy(data,feature_list,values_features,path,l_age):
    ## Aciertos en general
    values_int = [int(x) for x in values_features]
    spk_list = list(set(list(data["Speaker ID"])))

    accuracy = list()
    for values in values_int:
        mean_spk = list()
        for spk in spk_list:
            if l_age == 2:
                mean_aux = np.mean(data.loc[(data["Value"] == values) & (data["AgeGroup"] == l_age) & (data["Speaker ID"] == spk), ["Correct"]])
            elif l_age == 5:
                mean_aux = np.mean(data.loc[(data["Value"] == values) & (data["AgeGroup"] == l_age) & (data["Speaker ID"] == spk), ["Correct"]])
            # end if
            if not math.isnan(mean_aux):
                mean_spk.append(mean_aux)
            # end if
        # end for spk
        accuracy.append(np.mean(mean_spk))
    # end for values

    plt.figure(num=None, figsize=(16, 12), dpi=120, facecolor='w', edgecolor='k')
    plt.stem(values_int,accuracy)
    plt.ylabel('Accuracy')
    plt.xlabel('Valor parámetro '+feature_list)
    plt.grid()
    plt.ylim(0,1)
    if l_age == 2:
        plt.title('Accuracy edad 2, max='+str(np.round(np.max(accuracy),2))+' '+feature_list+'='+str(values_int[accuracy.index(max(accuracy))]))
        plt.savefig(os.path.join(path,'accuracy edad 2.png'))
    elif l_age == 5:
        plt.title('Accuracy edad 5, max='+str(np.round(np.max(accuracy),2))+' '+feature_list+'='+str(values_int[accuracy.index(max(accuracy))]))
        plt.savefig(os.path.join(path,'accuracy edad 5.png'))
    # end if
    #plt.show()
    plt.close()
# end sex_accuracy

def type_accuracy(data,feature_list,values_features,path,type):
    ## Aciertos en general
    values_int = [int(x) for x in values_features]
    spk_list = list(set(list(data["Speaker ID"])))

    accuracy = list()
    for values in values_int:
        mean_spk = list()
        for spk in spk_list:
            if type == "CorrManner":
                mean_aux = np.mean(data.loc[(data["Value"] == values) & (data["Speaker ID"] == spk), ["CorrManner"]])
            elif type == "CorrVoice":
                mean_aux = np.mean(data.loc[(data["Value"] == values) & (data["Speaker ID"] == spk), ["CorrVoice"]])
            elif type == "CorrPlace":
                mean_aux = np.mean(data.loc[(data["Value"] == values) & (data["Speaker ID"] == spk), ["CorrPlace"]])
            # end if
            if not math.isnan(mean_aux):
                mean_spk.append(mean_aux)
            # end if
        # end for spk
        accuracy.append(np.mean(mean_spk))
    # end for values

    plt.figure(num=None, figsize=(16, 12), dpi=120, facecolor='w', edgecolor='k')
    plt.stem(values_int,accuracy)
    plt.ylabel('Accuracy')
    plt.xlabel('Valor parámetro '+feature_list)
    plt.grid()
    plt.ylim(0,1)
    if type == "CorrManner":
        plt.title('Accuracy modo, max='+str(np.round(np.max(accuracy),2))+' '+feature_list+'='+str(values_int[accuracy.index(max(accuracy))]))
        plt.savefig(os.path.join(path,'accuracy modo.png'))
    elif type == "CorrVoice":
        plt.title('Accuracy sonoridad, max='+str(np.round(np.max(accuracy),2))+' '+feature_list+'='+str(values_int[accuracy.index(max(accuracy))]))
        plt.savefig(os.path.join(path,'accuracy sonoridad.png'))
    elif type == "CorrPlace":
        plt.title('Accuracy lugar, max='+str(np.round(np.max(accuracy),2))+' '+feature_list+'='+str(values_int[accuracy.index(max(accuracy))]))
        plt.savefig(os.path.join(path,'accuracy lugar.png'))
    # end if
    #plt.show()
    plt.close()
# end sex_accuracy


def main():
    """Main script

    :returns: None.
    """

    # Path path with data
    audio_path = 'audio/experiment_lm'
    no_kal_path = 'audio/experiment_lm/no_kal_audio'

    result_spk= 'results/'
    #results_raw_path = 'results/raw'
    result_reformat = 'results/reformat/'

    info_user_test_path = 'info_user/test'
    info_user_train_path = 'info_user/train'

    combined_features_path = 'combined_features';

    #results_feat = 'tuning'
    conf_path = 'conf/'

    # Features and values
    feat_name = 'mfcc'
    feature_list = 'num-mel-bins'
    values_features = ['14','18','22','26','30','34']

    # 'num-ceps'        # ['4','6','10','12','14','16','18','20','22','24','26']
    # frame-length      # ['10','15','20','25','30','35','40']
    # frame-shift       # ['5','10','15','20','25','30']
    # cepstral-lifter   # ['14','18','22','26','30']
    # num-mel-bins      # ['14','18','22','26','30','34']

    # Reorder spk files
    for file in os.listdir(info_user_test_path):
        if file.endswith(".kal") and not(file.startswith(".")) and not(file.startswith("_")):
                shutil.move(os.path.join(info_user_test_path,file),info_user_train_path)
            # end if
        # end if
    # end for


    # Check for audio files with no .kal
    train_spks_info = list()
    for file in os.listdir(info_user_train_path):
        if file.endswith(".kal") and not(file.startswith(".")) and not(file.startswith("_")):
            train_spks_info.append(file)
    crossval_spk_functions.clean_wave_files(train_spks_info, audio_path, no_kal_path)


    # Path to save results
    # create_data_path(results_feat)

    # Class split
    c_train, c_test = split_spk(info_user_train_path)

    # Reorder spk files
    for file in os.listdir(info_user_train_path):
        if file.endswith(".kal") and not(file.startswith(".")) and not(file.startswith("_")):
            name = file[0:5]
            if name in c_test:
                shutil.move(os.path.join(info_user_train_path,file),info_user_test_path)
            # end if
        # end if
    # end for

    for f in os.listdir(combined_features_path):
        os.remove(os.path.join(combined_features_path, f))
    # end for

    # Loop for results calculation

    # Default value
    file = open(conf_path+feat_name+'.conf','r')
    for line in file:
        if feature_list in line:
            default = line
        # end if
    # end for

    for values in values_features:

        # Change values in file
        with open(conf_path+feat_name+'.conf', 'r') as file:
            data = file.readlines()
        # end with

        for line in data:
            if feature_list in line:
                idx = data.index(line)
                data[idx] = '--' + feature_list + '=' + values + '\n'
            # end if
        # end for

        with open(conf_path+feat_name+'.conf', 'w') as file:
            file.writelines(data)


        # Make run.py
        bashCommand = "python3 run.py --train --test"
        process = subprocess.Popen(bashCommand,shell=True)
        output, error = process.communicate()


        # Delete combined features (may produce errors in executions)
        for f in os.listdir(combined_features_path):
            os.remove(os.path.join(combined_features_path, f))
        # end for


        # Save results in different forlder and change name
        resultFilename = 'results/resultSimple'
        shutil.copy(resultFilename, resultFilename+'_'+feature_list+'_'+values)
        os.remove(resultFilename)
        # os.rename(resultFilename, resultFilename+'_'+feature_list+values)

        # Save raw results and csv
        results_decode_path = 'exp/tri1/decode/scoring_kaldi/wer_details/'
        crossval_spk_functions.save_raw_result_tuning(results_decode_path,feature_list+'_'+values)

    # end for values


    # Change values in file to defaults
    with open(conf_path+feat_name+'.conf', 'r') as file:
        data = file.readlines()
    # end with

    for line in data:
        if feature_list in line:
            idx = data.index(line)
            data[idx] = default
        # end if
    # end for

    with open(conf_path+feat_name+'.conf', 'w') as file:
        file.writelines(data)

    # Reorder spk files
    for file in os.listdir(info_user_test_path):
        if file.endswith(".kal") and not(file.startswith(".")) and not(file.startswith("_")):
                shutil.move(os.path.join(info_user_test_path,file),info_user_train_path)
            # end if
        # end if
    # end for



    ## --------------------- Guarda los resultados ---------------------------

    # Take .csv result and reformat for SPSS analysis
    for file in os.listdir(result_spk):
        if file.endswith(".csv"):
            bashCommand = "python3 result_reformat4_tuning.py " + os.path.join(result_spk,file) + " " + os.path.join(result_reformat,file[:-4])+'_reformat.csv'
            process = subprocess.Popen(bashCommand,shell=True)
            output, error = process.communicate()

    # Global results for SPSS
    # """ SE HA COMENTADO PARA HACER LOS CÁLCULOS POR PARTES """
    crossval_spk_functions.global_result_reformat_tuning(result_reformat)
    os.rename(result_reformat+'global_result_reformat.txt', result_reformat+'global_result_'+feature_list+'.txt')
    ## --------------------- Guarda los resultados ---------------------------


    file = result_reformat+'global_result_'+feature_list+'.txt'

    data = pd.read_csv(file, sep="\t", header='infer')
    #data = data.iloc[1:]
    data.columns = ["N", "Speaker ID", "Task", "Evaluation", "Hit", "Correct", "Target", "Response", "Target Utterance", "AgeGroup", "Sex", "Feature", "Value", "CorrManner", "CorrVoice", "CorrPlace", "Last"]
    data = data.drop(['N', 'Last'], axis=1)

    total_accuracy(data,feature_list,values_features,result_reformat)

    sex_accuracy(data,feature_list,values_features,result_reformat,'H')
    sex_accuracy(data,feature_list,values_features,result_reformat,'M')

    age_accuracy(data,feature_list,values_features,result_reformat,2)
    age_accuracy(data,feature_list,values_features,result_reformat,5)

    type_accuracy(data,feature_list,values_features,result_reformat,"CorrManner")
    type_accuracy(data,feature_list,values_features,result_reformat,"CorrVoice")
    type_accuracy(data,feature_list,values_features,result_reformat,"CorrPlace")
# end main


# ----------------------------- MAIN SECTION -------------------------------- #
if __name__ == "__main__":
   # main(sys.argv)
   main()
# end if







