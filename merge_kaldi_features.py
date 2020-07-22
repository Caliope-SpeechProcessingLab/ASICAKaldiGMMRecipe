#!/usr/bin/env python3
#
# This script takes the folders with the features calculated by kaldi or others (like openSmile) and merge the .ark and .scp
# files in the /data/ folder.
#------------------------------------------------------------------------------------------------------------------
# Variables:
#   Inputs:
#     * folder_in: name of folders with features calculated.
#   Outputs:
#     * folder_out: /data/ folder where combined data is saved.
#------------------------------------------------------------------------------------------------------------------
# Authors:
#   - Main programmer: Andres Lozano Durán
#   - Main Supervisor: Ignacio Moreno Torres
#   - Second Supervisor: Enrique Nava Baro
#
# EXAMPLE OF USE
# You need to generate the features in different folder in kaldi. This is used after all features are calculated, but before normalization.
# -----------------------------------------------------------------------------
# cd custom_kaldi
# python3 merge_kaldi_features.py plp mfcc combined_features
# cd ..
# -----------------------------------------------------------------------------
# Eg:
# python3 merge_kaldi_features.py folderIn1 folderIn2 ... folderOut
# python3 merge_kaldi_features.py plp mfcc combined_features
#


import os
import re
import sys
import shutil
import kaldiio
# import subprocess
import numpy as np


def copy_and_overwrite(from_path, to_path):
    """ Copy and overweite folder

    :param from_path: path data original
    :param to_path: path data destination
    :returns: None
    """
    if os.path.exists(to_path):
        shutil.rmtree(to_path)
    shutil.copytree(from_path, to_path)
# end copy_and_overwrite

def create_data_folder(folder_name):
    """ Create a new data folder

    :param folder_name: name of folder
    :returns: None
    """
    if os.path.exists(folder_name):
        shutil.rmtree(folder_name)
    os.makedirs(folder_name)
# end create_data_folder

def folder_empty(folder_name):
    """ Check if folder is empty

    :param folder_name: name of folder
    :returns listOfEmptyDirs:List of empty directories in folder
    """
    # Create a List
    listOfEmptyDirs = list()

    # Iterate over the directory tree and check if directory is empty
    for dirName in folder_name:
        for (dirpath, dirnames, filenames) in os.walk(dirName):
            if len(dirnames) == 0 and len(filenames) == 0:
                listOfEmptyDirs.append(dirpath)

    return listOfEmptyDirs
# end folder_empty

def load_ark_matrix(folder_name,file_name):
    """ Load .ark file matrix

    :param folder_name: name of folder with .ark data, e.g, 'plp' 'mfcc'
    :param file_name: name of .ark file to load
    :returns write_dict: Dicctionary with data from -ark file
    """
    # Function to load a .ark file and see it in a matrix
    # matrix1 = load_ark_matrix('plp','raw_plp_test.1.ark')
    # matrix2 = load_ark_matrix('mfcc','raw_mfcc_test.1.ark')

    parent_path = os.path.dirname(os.getcwd())
    name_file_ark = os.path.join(parent_path, folder_name, file_name)

    write_dict={} # kaldiio uses features in the form of a dict
    d = kaldiio.load_ark(name_file_ark)
    for key_kaldi, array_kaldi in d:
        write_dict[key_kaldi] = array_kaldi

    return write_dict
# end load_ark_matrix

def calculate_num_cep(feature_name):
    """ Calculate the number of ceps employed in function of the feature name

    :param feature_name: name of features to check e.g, 'mfcc', 'plp'
    :returns numCeps: Number of ceps used in .confg file
    """
    # feature_name = 'mfcc' ''plp' 'plp_pitch
    # Calculate the number of ceps employed in function of the feature name
    config_folder = 'conf'

    configFile = open(os.path.join(config_folder, feature_name+'.conf'))
    configFile = configFile.read()
    configList = re.split(' |\t|\n|=',configFile)
    posNumceps = configList.index('--num-ceps')
    if feature_name == 'mfcc':
        numCeps = int(configList[posNumceps+1]) - 1
    else:
        numCeps = int(configList[posNumceps+1])

    return numCeps
# end calculate_num_cep

def args_function(args):
    """ Check args in script

    :param args: arguments for script
    :returns: None
    """
    if args != []:
        return args[1:]
    else:
        raise ValueError('You need to specify folder for features')
# end args_function

#---------------------------------MAIN-----------------------------------------
if __name__ == "__main__":

    # sys.argv = ['merge_kaldi_features.py','mfcc','energy','combined_features']
    # sys.argv = ['merge_kaldi_features.py','plp','mfcc','energy','combined_features']
    args = args_function(sys.argv)
    # print(sys.argv)
    # parent_path = os.path.dirname(os.getcwd())
    print(sys.argv)
    folder_in = args[:-1]
    folder_out = args[-1]
    data_name = 'data'

    listEmpty = folder_empty(folder_in)
    if listEmpty != []:
        s = listEmpty + 'folder contains EMPTY FOLDERS: '
        raise ValueError(s + str(listEmpty))

    # Acces folder and merge .ark and .scp files
    list_file = os.listdir(folder_in[0])

    for file_ark in list_file:

        if file_ark.endswith('.ark'):
            write_dict={} # kaldiio uses features in the form of a dict

            for folder in folder_in:
                # folder = 'mfcc' folder = 'plp' folder = 'energy'
                # file_ark = 'raw_mfcc_train.1.ark'
                name_file_ark = file_ark;
                name_file_ark = name_file_ark.replace(folder_in[0],folder)

                d = kaldiio.load_ark(os.path.join(folder, name_file_ark))
                for key_kaldi, array_kaldi in d:
                    8
                    # key_kaldi = a1
                    # array_kaldi = a2
#                    a1 = 'CA212QL3_M20-utt12'
#                    a2 = write_dict[a1]
#                    if key_kaldi == 'CA212QL3_M20-utt12':
#                        a = array_kaldi
#                        write_dict['CA101QL3_H32-utt1']

                    # numCeps = calculate_num_cep(folder)
                    # Some features like energy can have dim (xx,) wich makes dimensional error
                    if array_kaldi.ndim == 1:
                        array_kaldi=np.atleast_2d(array_kaldi).T
                    # end if
                    try:
                        write_dict[key_kaldi] = np.concatenate((write_dict[key_kaldi],array_kaldi),axis=1)
                        # write_dict[key_kaldi] = np.concatenate((write_dict[key_kaldi],array_kaldi[:,:numCeps]),axis=1)
                    except:
                        # Este es el caso en el que todavía no se ha introducido ningún dato
                            # write_dict[key_kaldi] = array_kaldi[:,:numCeps]
                        if key_kaldi not in write_dict:
                            write_dict[key_kaldi] = array_kaldi
                        else:
                           diff = len(array_kaldi)-len(write_dict[key_kaldi])
                           if diff>0:
                               array_kaldi = array_kaldi[:-diff]
                           else:
                               array_kaldi=np.concatenate((array_kaldi,np.zeros((-diff,array_kaldi.shape[1]))),axis=0)
                           # end if
                           write_dict[key_kaldi] = np.concatenate((write_dict[key_kaldi],array_kaldi),axis=1)
                        # end if

                    # end try
                # end for
            # end for

            destark_filename = name_file_ark.replace(folder_in[-1],data_name)
            destark_filename = os.path.join(os.getcwd(),folder_out, destark_filename)
            srcscp_filename = destark_filename.replace('ark','scp')

            print ("Writing to " + destark_filename)
            kaldiio.save_ark(destark_filename, write_dict, scp=srcscp_filename)
        # end if
    # end for

#end if




