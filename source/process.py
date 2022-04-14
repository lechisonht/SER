import pickle
import numpy as np
import os

#for loading and visualizing audio files
import librosa

#to play audio
import IPython.display as ipd
import cv2
import sounddevice as sd
from scipy.io.wavfile import write
import wavio as wv
import time
from IPython.display import clear_output

from preprocess import *

# DEMO
def demo(model_128, duration_short = 10, file_path=0):
    tic=time.perf_counter()
    #model [resnet,pca,svm]
    new_audio,new_samplerate = [],0
    
    # Record audio
    if file_path==0:
        freq = 44100
        sr = freq
        duration = duration_short
        print('Recording. Please talk anything...')
        audio = sd.rec(int(duration * freq), samplerate=freq, channels=2)
        sd.wait()
        print('analyzing emotions in audio...')
        sf.write('input.wav', audio, sr)
        list_audio = ['input.wav']
        
    # Input audio file or video
    else:
        if file_path.split('.')[-1] in ['mp4', 'MP4', 'avi', 'AVI']:  #input video clip
            file_audio = get_audio_from_video(file_path)
        else:
            file_audio = convert_audio(file_path)
        list_audio = extract_clips(file_audio, duration_short)
    
    emotions = []
    times = []
    start_time = 0
    for i in tqdm(range(len(list_audio))):
        file = list_audio[i]
        new_audio ,new_samplerate = librosa.load(file)
        length = 851895
        new_audio = librosa.util.fix_length(new_audio,length)
        
        sample_128 = new_audio
        sr_128 = new_samplerate
        mfcc_128 = librosa.feature.mfcc(sample_128, sr=sr_128,n_mfcc=128)
        mfcc_128_3d = cv2.merge((mfcc_128.T,mfcc_128.T,mfcc_128.T))
        fm_128 = model_128[0].predict(np.array([mfcc_128_3d]))
        fm_pca_128 = model_128[1].transform(fm_128)

        prob = model_128[2].predict_proba(fm_pca_128)[0]
        if prob[1]>0.5:
            emotion = 'NEUTRAL'
        else:
            emotion = 'ANGRY - Probability: {}%'.format(np.round(prob[0]*100,2))
        emotions.append(emotion)
        end_time = start_time + duration_short
        times.append('{} - {}'.format(start_time, end_time))
        start_time = end_time
    toc=time.perf_counter() 
    return emotions, times, list_audio,toc-tic

# Concatenate audio
from moviepy.editor import concatenate_audioclips, AudioFileClip

def concatenate_audio_moviepy(audio_clip_paths, output_path):
    clips = [AudioFileClip(c) for c in audio_clip_paths]
    final_clip = concatenate_audioclips(clips)
    final_clip.write_audiofile(output_path)

def find_emotion(emotions):
    index_emotion = []
    name_emotion = []
    emotion = ''
    for i in range(len(emotions)):
        if emotions[i].split(' - ')[0] != emotion:
            index_emotion.append(i)
            name_emotion.append(emotions[i].split(' - ')[0])
            emotion = emotions[i].split(' - ')[0]
    
    for i in range(len(name_emotion)):
        if name_emotion[i] == "ANGRY":
            if i == len(name_emotion)-1:
                temp_e = emotions[index_emotion[i]:]
                probability = []
                for j in range(len(temp_e)):
                    probability.append(float(temp_e[j].split(' - ')[1].split(' ')[1][:-1]))
                name_emotion[i] = name_emotion[i] + f' - Probability: {np.array(probability).mean()}%'
            else:
                temp_e = emotions[index_emotion[i]:index_emotion[i+1]]
                probability = []
                for j in range(len(temp_e)):
                    probability.append(float(temp_e[j].split(' - ')[1].split(' ')[1][:-1]))
                name_emotion[i] = name_emotion[i] + f' - Probability: {np.array(probability).mean()}%'
    
    return index_emotion, name_emotion

def merge_emotion(emotions,times,list_files):
    tic=time.perf_counter()
    index, emotion = find_emotion(emotions)
    list_file_merge = []
    list_times = []
    for i in range(len(index)):
        if i == len(index) - 1:
            list_file = list_files[index[i]:]
            path_name = list_files[0][:-5]
            path_name=path_name.replace("subclips","result")
            time_e = str(convert(int(times[index[i]].split(' - ')[0]))[-1])+" - "+str(convert(int(times[-1].split(' - ')[1]))[-1])
            path_name = path_name.replace(path_name.split('/')[-1], emotion[i].split(' - ')[0] + ' ' + time_e.replace(':', '') + '.wav')
            list_file_merge.append(path_name)
            list_times.append(time_e)
            concatenate_audio_moviepy(list_file,path_name)
        else:
            list_file = list_files[index[i]:index[i+1]]
            path_name = list_files[0][:-5]
            path_name=path_name.replace("subclips","result")
            time_e = str(convert(int(times[index[i]].split(' - ')[0]))[-1])+" - "+str(convert(int(times[index[i+1]-1].split(' - ')[1]))[-1])
            path_name = path_name.replace(path_name.split('/')[-1], emotion[i].split(' - ')[0] + ' ' + time_e.replace(':', '') + '.wav')
            list_file_merge.append(path_name)
            list_times.append(time_e)
            concatenate_audio_moviepy(list_file,path_name)
    clear_output()
    toc=time.perf_counter()
    return emotion, list_times,list_file_merge,toc-tic