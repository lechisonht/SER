# import 
from samplerate.converters import resample
import cv2
import librosa
import pandas as pd
import soundfile as sf
from tqdm import tqdm
import os

# Get duration of source audio
from mutagen.mp3 import MP3
from mutagen.wave import WAVE

# function to convert the seconds into readable format
def convert(seconds):
    hours = seconds // 3600
    seconds %= 3600
    mins = seconds // 60
    seconds %= 60
    time_string = f'{hours}h:{mins}m:{seconds}s'
    return hours,mins,seconds,time_string

def get_duration(filename):
    if filename.split('.')[-1] in ['mp3', 'MP3']:
        audio = MP3(filename)
    elif filename.split('.')[-1] in ['wav', 'WAV']:
        audio = WAVE(filename)
    else:
        print('System only accept .wav or .mp3 file')
        return 0
    
    audio_info = audio.info    
    length_in_secs = int(audio_info.length)
    hours, mins, seconds, time_str = convert(length_in_secs)

    src_duration = hours*3600 + mins*60 + seconds
    return src_duration

# Extract subclips from an audio
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
    
def extract_clips(filename, duration_short):
    # if not os.path.exists('subclips'):
    #     os.mkdir('subclips')
    # else:
    #     clear_file('subclips')
    src_duration = get_duration(filename)
    if src_duration <= duration_short:
        return [filename]
    else:
        files = []
        count = 1
        duration_of_clip = duration_short #in seconds, duration of final audio clip
        src_duration = src_duration #in seconds, the duration of the original audio
        for i in range(0, src_duration +1 , duration_of_clip):
            out_fname = filename.split('.')[0]
            path_name = ''
            path_name = f'{out_fname}_clip{count}.wav'
            path_name=path_name.replace('upload','subclips')
            ffmpeg_extract_subclip(filename, i, i + duration_of_clip,targetname=path_name)
            files.append(path_name)
            count += 1
        return files

# Converte video to audio
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip, ffmpeg_extract_audio

def get_audio_from_video(filename):
    des_file = filename.split('.')[0]+'.wav'
    ffmpeg_extract_audio(filename,des_file)
    return des_file 

# Clear folder
def clear_file(folder):
    for file in os.listdir(folder):
        os.remove(os.path.join(folder,file))

# Convert mp3 -> wav
from os import path
from pydub import AudioSegment

def convert_audio(filename):
    des_file = filename.split('.')[0]+'.wav'
    sound = AudioSegment.from_file(filename)
    sound.export(des_file, format="wav")
    return des_file