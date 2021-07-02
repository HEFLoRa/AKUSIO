# -*- coding: utf-8 -*-
"""
Created on Wed Aug 14 10:06:49 2019

@author: Sebastian
"""

# Beat tracking example
import librosa
import librosa.display
import numpy as np
from keras.models import Sequential
from keras.models import load_model


#1. load model with model=loadModel() (load CNN)
#2. recognition(filename,model) (filename=WAV-File)


#load audio
def recognition(y,model):
    #y, sr = librosa.load(filename,sr=16000)
    sr=16000
    #Frame size
    N = int(50*10**(-3)*sr)
    #overlapping
    S=int((1/2)*N)
    #calc stft
    D = np.abs(librosa.stft(y=y,n_fft=N,hop_length=S))
    D = D**2    
    
    #log mel spectogram
    M = librosa.feature.melspectrogram(sr=sr,S=D, n_mels=64)    
    vec=1e-30
    M=np.log(M+vec)
    
    
    #normalize spectogram
    mu = np.mean(M,axis=1)[:,np.newaxis]
    sigma=np.sqrt(np.var(M,axis=1))[:,np.newaxis]+1e-30
    M_norm = (M-mu)/(sigma)
    
    
    #input spectogram
    Mproj = np.array([M_norm[i][1:(len(M_norm[0])-1)] for i in range(len(M_norm))])
    
    #input vector
    vec=Mproj
    vec=np.expand_dims(vec, axis=-1)
    vec=vec.reshape([1,64, 399,1])

    
    #predict and write to file
    #model.compile()
    pred=model.predict(vec)#.tofile("pred", sep=' ', format="%f")
    weights = 0.15 * np.ones(19)
    weights[1]=0.2
    weights[10]=0.6
    prob_vec=estimate_prob(pred,weights)
    
    return prob_vec
    


def loadModel():
    #load cnn
    model = Sequential()
    model= load_model("CNN")
    return model

# estimates probabilities of detected bird classes
def estimate_prob(pred,weights):
    prob_vec = np.zeros(19)
    for i in range(19):
        prob_vec[i]=0
        if pred[0,i]>0.7*weights[i]:
            prob_vec[i]=0.25
        if pred[0,i]>1.*weights[i]:
            prob_vec[i]=0.5
        if pred[0,i]>0.2+weights[i]:
            prob_vec[i]=0.7
    return prob_vec




    
