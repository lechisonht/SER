import tensorflow as tf
from tensorflow import keras
import pickle
import os

os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

# LOAD MODEL
model_fe_128 = keras.models.load_model("model/ResNet152_128")

with open("model/PCA_128.pkl", "rb") as f:
      pca_128 = pickle.load(f)

with open("model/SVM_128.pkl", "rb") as f:
      svm_128 = pickle.load(f)

_model_128 = [model_fe_128,pca_128,svm_128]

# DEPLOY
import json
from flask import Flask, request
from flask import render_template
from flask_cors import CORS, cross_origin

from flask import send_file
import os
import zipfile
import secrets
from path_dir import *
from process import *

app = Flask(__name__)
#app.config['JSON_AS_ASCII'] = False


CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['RESULT'] = ''
app.config['TOKEN'] = ''
app.config['HOST'] = '0.0.0.0'
app.config['PORT'] = 8889
@app.route('/app', methods=['POST'])
@cross_origin(origin='*')
def process():
    TOKEN = secrets.token_urlsafe(50) 
    app.config['TOKEN'] =  TOKEN
    path_token = create_path('client/',TOKEN)
    path_upload = create_path(path_token,'upload') + '/'
    path_result = create_path(path_token,'result') + '/'
    create_path(path_token,'subclips')
    if request.method == 'POST':
        obj = request.form
        x = request.files['audio']
        x.save(path_upload+x.filename)
        emotion, time, list_audio, running_time_1 = demo(_model_128, duration_short=15, file_path = path_upload+x.filename)
        emotion_merge, time_merge, audio_merge, running_time_2 = merge_emotion(emotion,time,list_audio)
        print(audio_merge)
        app.config['RESULT'] = path_result
        df = pd.DataFrame({'Emotion':emotion_merge,'Time':  time_merge})
        df.to_csv(path_result+'emotion.csv',index=False)
        link_download = 'http://{}:{}/download/{}'.format('192.168.1.94',app.config['PORT'],TOKEN)
        return {
                'emotion': emotion_merge,
                'time': time_merge,
                'Running time': f"{(running_time_1 + running_time_2)/60:0.4f} minutes",
                'download' : link_download
                }
    else:
        return "Please use POST method"
            

@app.route('/download/<TOKEN>')
def download_all(TOKEN = app.config['TOKEN']):
    path_result_zip = app.config['RESULT'][:-1].replace('result','RESULT.zip').replace("client/","client\\")
    zipf = zipfile.ZipFile(path_result_zip,'w', zipfile.ZIP_DEFLATED)
    for root,dirs, files in os.walk(app.config['RESULT']):
        for file in files:
            zipf.write(app.config['RESULT']+file)
    zipf.close()
    return send_file(path_result_zip,
            mimetype = 'zip',
            attachment_filename= "RESULT.zip",
            as_attachment = True)

if __name__ == '__main__':
    app.run(port=8889,host='0.0.0.0')