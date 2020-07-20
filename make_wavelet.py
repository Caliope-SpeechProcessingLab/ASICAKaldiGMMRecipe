#!/usr/bin/env python3
#
# This script calculates wavelet features for kaldi use. It uses same squeme as steps/make_mfcc.sh. This script is calle from steps/make_wavelet.sh
#
# Saves result in wavelet/ using .ark format por kaldi use.
#

import os
import sys
#import time
import pywt
import kaldiio
import pywt.data
import scipy.stats

import  numpy as np
import itertools as it
from scipy.io import wavfile
from collections import Counter

# print("ok")

# ----------------------- FUNCTIONS  -----------------------------------------#

def load_config_frame(folder):
    """ Load config parameters from conf/folder.conf

    :returns: Two float variables with values from frame_shift and frame_length, defaul values: 10, 25.
    """
    # Default values
    frame_shift=10e-3   # 10 ms
    frame_length=25e-3  # 25 ms

    f = open('conf/' + folder + '.conf')
    for l in f:
        if "--frame-shift" in l:
            l = l.split("=")
            frame_shift = float(l[1])*1e-3
        elif "--frame-length" in l:
            l = l.split("=")
            frame_length = float(l[1])*1e-3

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

    return audio_split
# split_audio


def calculate_energy(list_values,fs,level):
    """ Compute energy from data.

    :param list_values: List with values of data for energy caculation
    :param fs: sample frequency from original data
    :param level: level of wavelet decomposition for fs compensatio
    :returns: Three values with energy, first derivative and second derivative
    """
    return (10*np.log10( sum(list_values**2)/(len(list_values)/(fs/2**(level-1)))))
# end calculate_energy


#def calculate_entropy(list_values):
#    counter_values = Counter(list_values).most_common()
#    probabilities = [elem[1]/len(list_values) for elem in counter_values]
#    entropy=scipy.stats.entropy(probabilities)
#    return entropy
#
#def calculate_statistics(list_values):
#    n5 = np.nanpercentile(list_values, 5)
#    n25 = np.nanpercentile(list_values, 25)
#    n75 = np.nanpercentile(list_values, 75)
#    n95 = np.nanpercentile(list_values, 95)
#    median = np.nanpercentile(list_values, 50)
#    mean = np.nanmean(list_values)
#    std = np.nanstd(list_values)
#    var = np.nanvar(list_values)
#    rms = np.nanmean(np.sqrt(list_values**2))
##    return [n5, n25, n75, n95, median, mean, std, var, rms] #
#    return list([n5, n25, n75, n95, median, mean, std, var, rms])
#
##def calculate_crossings(list_values):
##    zero_crossing_indices = np.nonzero(np.diff(np.array(list_values) &gt; 0))[0]
##    no_zero_crossings = len(zero_crossing_indices)
##    mean_crossing_indices = np.nonzero(np.diff(np.array(list_values) &gt; np.nanmean(list_values)))[0]
##    no_mean_crossings = len(mean_crossing_indices)
##    return [no_zero_crossings, no_mean_crossings]
#
#def get_features(list_values):
#    #entropy = calculate_entropy(list_values)
##    crossings = calculate_crossings(list_values)
#    statistics = calculate_statistics(list_values)
#    return statistics # crossings +[entropy] +

def calculate_wavelet(audio,fs,frame_shift,frame_length,kal_file):
    """ Calculate wavelet features

    :param audio: audio data file
    :param fs: sample frequency
    :param frame_shift: shift os windows in every step
    :param frame_length: length of windowns
    :param kal_file: .kal annotation file
    :returns wavelet: Numpy array with values of wavelet features.
    """
    # p_ref = 2e-5
    # Transfor sec to frames
    frame_shift_new = int(np.floor(frame_shift * fs))
    frame_length_new = int(np.floor(frame_length * fs))

    audio_split = split_audio(audio,fs,kal_file)

    # Recorremos el audio partido y calculamos los wavelet para cada pseudopalabra
    # If true, end effects will be handled by outputting only frames that completely fit in the file default = true
    # With --snip-edges=true (the default), we use a HTK-like approach to determining the number of frames-- all frames have to fit completely into the waveform, and the first frame begins at sample zero.
    wavelet = list()
    for frame in audio_split:

        wave_vector = list()
        frame_windowed=moving_window(frame, frame_length_new, frame_shift_new)
        # frame_windowed tiene para cada utterance todas las ventanas que se pueden calcular sobre la señal
        for data in frame_windowed:
            #
#            mfcc_aux[0] = 10*np.log10( sum(data**2)/(len(data)/fs)/(p_ref) )

            # cA: approximation -> low pass filter
            # cD: detail -> high pass filter
            waveletname = 'db8'

            wp = pywt.WaveletPacket(data,wavelet=waveletname,mode='symmetric')

            max_level = wp.maxlevel-2
            name_node = list()
            for ii in range(max_level+1):
                name_node = name_node + ([node.path for node in wp.get_level(ii,'freq')])
            # end for

            features = list()
            # Tenemos todos los nombres, solo queda ir calculando los features para cada datos
            for n in name_node:
                features.append(calculate_energy(wp[n].data,fs,level=len(n)))
                #features = features + get_features(wp[n].data)

#            features = list()
#                (cA, cD) = pywt.dwt(data_full, waveletname)
#
#                features = features + get_features(cA)
#                data_full = cA
#            # end for
#            features = features + get_features(cD)

            wave_vector.append(features)
        # end for data
        wave_vector = np.asarray(wave_vector)
        wavelet.append(wave_vector)
    # end for frame
#            cA5, cD5, cD4, cD3, cD2, cD1 = pywt.wavedec(data,'db8',level=5)
#
#            import matplotlib.pyplot as plt
#            ax1=plt.subplot(3,3,1); plt.plot(data); plt.title('data')
#            plt.subplot(3,3,2,sharey=ax1); plt.plot(cD1); plt.title('cD1')
#            plt.subplot(3,3,3,sharey=ax1); plt.plot(cD2); plt.title('cD2')
#            plt.subplot(3,3,4,sharey=ax1); plt.plot(cD3); plt.title('cD3')
#            plt.subplot(3,3,5,sharey=ax1); plt.plot(cD4); plt.title('cD4')
#            plt.subplot(3,3,6,sharey=ax1); plt.plot(cD5); plt.title('cD5')
#            plt.subplot(3,3,7,sharey=ax1); plt.plot(cA5); plt.title('cA5')
#             wave = list()
#            wave_eng = list()
#
#            wave.append(cD1)
#            wave.append(cD2)
#            wave.append(cD3)
#            wave.append(cD4)
#            wave.append(cD5)
#            wave.append(cA5)
#
#            import matplotlib.pyplot as plt
#            ax1=plt.subplot(1,2,1); plt.plot(data); plt.title('data')
#            plt.subplot(1,2,2,sharey=ax1); plt.plot(cD1); plt.title('cD1')
#
#            for w in wave:
#                # w = wave[0]
#                wave_eng.append(  10*np.log10 (sum(w**2) / ( len(w)/(fs/len(data)/len(w)) ) )    )
#                #wave_eng.append(10*np.log10( sum(abs(w)**2) ))
#                #wave_eng.append(10*np.log10( sum(w**2)/(len(w)/fs)) )
#                #            data_energy = sum(data**2)/(len(data)/fs)
#
#            # end for
#            wave_eng=np.atleast_2d(wave_eng)
#            wave_vector = np.vstack([wave_vector,wave_eng]) if wave_vector.size else wave_eng
#        # end for

    return wavelet
# end calculate_wavelet

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
    feature_name = 'wavelet'
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
    frame_shift, frame_length = load_config_frame(feature_name)

    # 2.- Cargar los audios y dividirlos en ventanas para calcular la energía
    audio_path = 'audio/experiment_lm'

    wavelet_dict={}
    # t = time.time()
    for kal in kal_list:
        if kal.endswith('.kal'):

            # 3.- Calcula la energía y las derivadas
            fs, audio = wavfile.read(os.path.join(audio_path,kal[:-3]+'wav'))
            audio = audio / escale_16_PCM

            kal_file = open(os.path.join('info_user',folder,kal),'r')
            kal_file = kal_file.readlines()

            wavelet_vector = calculate_wavelet(audio,fs,frame_shift,frame_length,kal_file)

            # Este ajuste se hace porque al generar el feature el orden es 1,2,3,... pero al guardarlos tenemos que tener 1,10,11,12,... porque es el orden que utiliza kaldi y los diccionarios.
            key_list = list()
            for i in range(0,len(wavelet_vector)):
                key_list.append(kal[:-4] + '-utt' + str(i))
            # end for
            key_list.sort()

            for i in range(0,len(wavelet_vector)):
                index = int(key_list[i][16:])
                #print(key_list[i])
                #print(index)
                wavelet_dict[key_list[i]] = wavelet_vector[index]
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
        d = split_dict(wavelet_dict, 4)
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
                    write_dict[key_kaldi] = wavelet_dict[key_kaldi]
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
    print ("steps/make_wavelet.sh: Creating Wavelet features...")
    main(sys.argv)
    print ("steps/make_wavelet.sh: Succeeded creating Wavelet features.")
# end if












