# basic 
import json
import pickle
import pandas as pd
import numpy as np
from tqdm.notebook import tqdm

# spacy library 설치 및 import
!python -m spacy download en_core_web_sm
import spacy

# GPU 사용 설정
spacy.prefer_gpu()

# spaCy 모델 로드
nlp = spacy.load("en_core_web_sm")

# function: separate sentences
def separate_sentence(df) :
  sentences = {}  # review id : [sentence1, sentence2...]
  for idx, row in df.iterrows() :
    doc = nlp(row['text'])
    senten = [sent.text.strip() for sent in doc.sents] # seperated sentences
    senten = [sen for sen in senten if sen] # remove empty strings 
    sentences[row['review_id']] = senten    # assign values to dictionary
  return sentences

# sentence tokenizing
sentences = separate_sentence(review)

# save pickle file
path = "your_path"
with open(path+"/file_name.pkl",'wb') as f:
  pickle.dump(sentences,f)