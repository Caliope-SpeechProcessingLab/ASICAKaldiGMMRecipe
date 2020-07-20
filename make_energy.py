#!/usr/bin/env python3
#
# This script calculates energy features for kaldi use. It uses same squeme as steps/make_mfcc.sh. This script is calle from steps/make_energy.sh
#
# Saves result in energy/ using .ark format por kaldi use.
#

import os
import sys
#import time
import kaldiio
#import itertools
import  numpy as np
import itertools as it
from scipy.io import wavfile

# print("ok")

# ----------------------- FUNCTIONS  -----------------------------------------#
def load_config():
    """ Load config parameters from conf/energy.conf

    :returns: Two float variables with values from frame_shift and frame_length, defaul values: 10, 25.
    """
    # Default values
    frame_shift=10e-3   # 10 ms
    frame_length=25e-3  # 25 ms

    f = open('conf/energy.conf')
    for l in f:
        if "--frame-shift" in l:
            l = l.split("=")
            frame_shift = float(l[1])*1e-3
        elif "--frame-length" in l:
            l = l.split("=")
            frame_length = float(l[1])*1e-3
        # end if
    # end for

    return frame_shift, frame_length
# end load_config

def moving_window(x, length, shift, step=1):
    """ Use a moving windows for data in x

    :param x: data
    :param length: length of windowns
    :param shift: shift os windows in every step
    :param step: step in data, if 1 takes data one by one, if 2 two by two, etc...
    :returns: A list with data windowed
    """
    streams = it.tee(x, length)
    return list( zip(*[it.islice(stream, i, None, step*shift) for stream, i in zip(streams, it.count(step=step))]) )
# end moving_window

def split_audio(audio,fs,kal_file):
    """ Split an audio in phonemes defined in .kal file

    :param audio: audio .wav file
    :param fs: sample frequency
    :param kal_file: kal file
    :returns: A list with audio divided
    """
    audio_split = list()

    for l in kal_file:
        l=l.split('\t')

        start = int(np.floor(float(l[0])*fs))
        end = int(np.floor(float(l[1])*fs))

        audio_split.append(audio[start:end+1])
    # end for
    return audio_split
# end split_audio

def calculate_energy(audio,fs,frame_shift,frame_length,kal_file):
    """ Calculate energy and first and second derviates of audio data using windowng.

    :param audio: audio data file
    :param fs: sample frequency
    :param frame_shift: shift os windows in every step
    :param frame_length: length of windowns
    :param kal_file: .kal annotation file
    :returns energy, delta_energy, delta_d_energy: Numpy array with values of energy, firts derivative and second derivative of audio using windowing.
    """
    # p_ref = 2e-5
    # Transfor sec to frames
    frame_shift_new = int(np.floor(frame_shift * fs))
    frame_length_new = int(np.floor(frame_length * fs))

    audio_split = split_audio(audio,fs,kal_file)

    # Recorremos el audio partido y calculamos la energía para cada pseudopalabra
    # If true, end effects will be handled by outputting only frames that completely fit in the file default = true
    # With --snip-edges=true (the default), we use a HTK-like approach to determining the number of frames-- all frames have to fit completely into the waveform, and the first frame begins at sample zero.
    energy = list()
    delta_energy = list()
    delta_d_energy = list()
    # delta_window = 2


    for frame in audio_split:

        eng = list()
        frame_windowed=moving_window(frame, frame_length_new, frame_shift_new)
        for data in frame_windowed:
            data=np.asarray(data)
            eng.append(10*np.log10( sum(data**2)/(len(data)/fs)))
        # end for
        energy.append(eng)

        delta = calculate_derivate(eng,2)
        delta_energy.append(delta)

        delta_d = calculate_derivate(delta,2)
        delta_d_energy.append(delta_d)

    # end for
    return energy, delta_energy, delta_d_energy
# end calculate_energy

def calculate_derivate(eng,delta_window):
    """ Calculate first derivate of data array.

    :param eng: input data
    :param delta_window: value of samples prev and post using in derivative calculation
    :returns derivate: First derivate of data input
    """
    derivate = list()
    prev = list()
    post = list()

    for i in range(0,delta_window):
        prev.append(eng[0])
        post.append(eng[-1])
    # end for
    eng_new = eng + post
    eng_new = prev + eng_new

    denom = sum(np.power(range(1,delta_window+1),2))
    for i in range(0+delta_window,len(eng_new)-delta_window):
        num = 0
        for k in range(1,delta_window+1):
            num = k*(eng_new[i+1]-eng_new[i-1])
        # end for
        derivate.append(num/denom)
    # end for

    return derivate
# end calculate_derivate

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

def main(argv):
    """ Main script

    :param argv: train or test path
    :returns: None
    """
    feature_name = 'energy'
    escale_16_PCM = 2**15
    #import soundfile as sf
    #ob = sf.SoundFile(os.path.join(audio_path,kal[:-3]+'wav'))
    #print('Sample rate: {}'.format(ob.samplerate))
    #print('Channels: {}'.format(ob.channels))
    #print('Subtype: {}'.format(ob.subtype))
    #16-bit PCM              -32768          +32767          int16

    # Se define el path de test o train
    path = sys.argv[1]
    folder = path.split("/")[1]
    # folder = 'train'
    kal_list = os.listdir(os.path.join('info_user',folder))

    # 1.- Cargar el archivo de configuración
    frame_shift, frame_length = load_config()

    # 2.- Cargar los audios y dividirlos en ventanas para calcular la energía
    audio_path = 'audio/experiment_lm'

    energy_dict={}
    # t = time.time()
    for kal in kal_list:
        if kal.endswith('.kal'):

            # 3.- Calcula la energía y las derivadas
            fs, audio = wavfile.read(os.path.join(audio_path,kal[:-3]+'wav'))
            audio = audio / escale_16_PCM

            kal_file = open(os.path.join('info_user',folder,kal),'r')
            kal_file = kal_file.readlines()

            energy_vector,deltae_vector,deltade_vector = calculate_energy(audio,fs,frame_shift,frame_length,kal_file)

            # Este ajuste se hace porque al generar el feature el orden es 1,2,3,... pero al guardarlos tenemos que tener 1,10,11,12,... porque es el orden que utiliza kaldi y los diccionarios.
            key_list = list()
            for i in range(0,len(energy_vector)):
                key_list.append(kal[:-4] + '-utt' + str(i))
            # end for
            key_list.sort()

            for i in range(0,len(energy_vector)):
                index = int(key_list[i][16:])
                #print(key_list[i])
                #print(index)
                energy_dict[key_list[i]] = np.vstack((np.asarray(energy_vector[index]),np.asarray(deltae_vector[index]),np.asarray(deltade_vector[index]))).T
            # end for
        # end if
    # end for
    # elapsed = time.time() - t

    # 4.- Lo guarda como un .ark y .scp
    if os.path.exists('mfcc') and len(os.listdir('mfcc'))>0:
        features_listdir = os.listdir('mfcc')
        folder_features = 'mfcc'
    elif os.path.exists('plp') and len(os.listdir('plp'))>0:
        features_listdir = os.listdir('plp')
        folder_features = 'plp'
    else:
        # No existen carpeta sgeneradas por kaldi para los features
        features_listdir = list()
        folder_features = 'none'
    # end if

    if folder_features == 'none':
        # Se cogen los features calculados y se dividen en 4. Creamos nuestro propio listdir
        d = split_dict(energy_dict, 4)
        index = 1

        for dic in d:
            destark_filename = 'raw_' + feature_name + '_' + folder + '.' + str(index) +'.ark'

            destark_filename = os.path.join(os.getcwd(),feature_name, destark_filename)
            srcscp_filename = destark_filename.replace('ark','scp')

            #print ("Writing to " + destark_filename)
            kaldiio.save_ark(destark_filename, dic, scp=srcscp_filename)
            index = index + 1
        # end for
    else:
        for file in features_listdir:
            write_dict={} # kaldiio uses features in the form of a dict
            if file.endswith('.ark') and folder in file:
                d = kaldiio.load_ark(os.path.join(folder_features, file))
                for key_kaldi, array_kaldi in d:
                    write_dict[key_kaldi] = energy_dict[key_kaldi]
                # end for
                destark_filename = file.replace(folder_features,feature_name)
                destark_filename = os.path.join(os.getcwd(),feature_name, destark_filename)
                srcscp_filename = destark_filename.replace('ark','scp')

                #print ("Writing to " + destark_filename)
                kaldiio.save_ark(destark_filename, write_dict, scp=srcscp_filename)
            #end if
        # end for
    # end if

# end main


# --------------------------- MAIN SECTION -----------------------------------#
if __name__ == "__main__":
    #print(sys.argv)
    print ("steps/make_energy.sh: Creating Energy features...")
    main(sys.argv)
    print ("steps/make_energy.sh: Succeeded creating Energy features.")
# end if





