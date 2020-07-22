#!/usr/bin/env python3
#
# This script takes .ark files in combined_features/ and relocates them from cross validation calulation. Takes features generated and split in tran and test according to info_user/train and /test info.
#

import os
import kaldiio
import subprocess
import numpy as np
import itertools as it

# print("ok")

# ----------------------- FUNCTIONS  -----------------------------------------#
def split_dict(dict_in, chunks):
    """ Calculate first derivate of data array.

    :param dict_in: input dicctionary data
    :param chunks: number of pieces to split dicctionary
    :returns split: Splitted dicctionary
    """
    # dict_in = wavelet_dict energy_dict
    # chunks = 4
    quarter = int(np.ceil(len(dict_in)/chunks))
    i = it.cycle(range(len(dict_in)))
    split = [dict() for _ in range(chunks)]

    k = list(dict_in.keys())
    k.sort()
    for key_name in k:
        # print(key_name)
        # print(next(i))
        split[int(np.floor(next(i)/quarter))][key_name] = dict_in[key_name]
    #end for
    return split
# end split_dict


def main(folder):
    print ("Relocating features...")

    # folder = 'train'

    if folder == 'train':
        featuresCombined_path = 'combined_features'
        infouser_path = 'info_user'

        ark_list = os.listdir(featuresCombined_path)

        # 1.- Load .ark data and save in global dict
        global_dict={}

        for ark in ark_list:
            if 'raw_data' in ark and ark.endswith('.ark'):
                 d = kaldiio.load_ark(os.path.join(featuresCombined_path, ark))
                 for key_kaldi, array_kaldi in d:
                     global_dict[key_kaldi] = array_kaldi
            # end if
        # end for

        # 2.- Generate train and test dict
        kal_train = os.listdir(os.path.join(infouser_path, 'train'))
        kal_train = [k[:-4] for k in kal_train] # -4 delete .kal string
        kal_train.sort()
        kal_test = os.listdir(os.path.join(infouser_path, 'test'))
        kal_test = [k[:-4] for k in kal_test]
        kal_test.sort()

        train_dict = {}
        test_dict = {}

        global_list = list(global_dict.keys())
        global_list.sort()

        for key_kaldi in global_list:
            if key_kaldi[:-5] in kal_train:
                train_dict[key_kaldi] = global_dict[key_kaldi]
            elif key_kaldi[:-5] in kal_test:
                test_dict[key_kaldi] = global_dict[key_kaldi]
            # end if
        # end for


        # 3.- Save both dictionary as .ark files
        for f in ark_list:
            os.remove(os.path.join(featuresCombined_path, f))

        num_split = int(len([s for s in ark_list if ('data_'+folder) in str(s)])/2)

        split_train = split_dict(train_dict, num_split)
        split_test = split_dict(test_dict, num_split)

        index = 1
        for dic in split_train:
            destark_filename = 'raw_data_train.' + str(index) +'.ark'
            destark_filename = os.path.join(os.getcwd(),featuresCombined_path, destark_filename)
            srcscp_filename = destark_filename.replace('ark','scp')
            kaldiio.save_ark(destark_filename, dic, scp=srcscp_filename)
            index = index + 1
        # end for

        index = 1
        for dic in split_test:
            destark_filename = 'raw_data_test.' + str(index) +'.ark'
            destark_filename = os.path.join(os.getcwd(),featuresCombined_path, destark_filename)
            srcscp_filename = destark_filename.replace('ark','scp')
            kaldiio.save_ark(destark_filename, dic, scp=srcscp_filename)
            index = index + 1
        # end for
    # end if

    # 4.- Calculate rest of makeFeats.sh
    bashCommand = "bash local/copy_scp_all.sh " + folder
    process = subprocess.Popen(bashCommand,shell=True)
    output, error = process.communicate()

    bashCommand = "bash utils/data/fix_data_dir.sh data/" + folder
    process = subprocess.Popen(bashCommand,shell=True)
    output, error = process.communicate()

    bashCommand = "steps/compute_cmvn_stats.sh data/" +folder+ " exp/make_combined_features/" +folder+ " combined_features || exit 1;"
    process = subprocess.Popen(bashCommand,shell=True)
    output, error = process.communicate()

    bashCommand = "utils/validate_data_dir.sh data/" + folder
    process = subprocess.Popen(bashCommand,shell=True)
    output, error = process.communicate()

    print ("Features relocated.")
# end main




