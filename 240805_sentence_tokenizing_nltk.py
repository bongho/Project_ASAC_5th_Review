# basic 
import json
import pickle
import pandas as pd
import numpy as np
from tqdm.notebook import tqdm

# NLTK, Tokenizer
import nltk
from nltk.tokenize import PunktSentenceTokenizer
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer

# Keybert
# run below code if it's not installed 
# !pip install keybert
from keybert import KeyBERT

# drive mount
from google.colab import drive
drive.mount('/content/drive')

# load review file
path = "your_path"
review = pd.read_csv(path + "/file_name.csv")

# nltk data download
nltk.download('punkt')
nltk.download('stopwords')

# function: replace unnecessary part of sentence
def replace_in_sentence(df) :
  df['text'] = df['text'].str.replace(r'\n', ' ', regex=True)
  df['text'] = df['text'].str.replace(r'\(\?*\)', ' ', regex=True)
  df['text'] = df['text'].str.replace(r'\(\?,\s*\?\)', ' ', regex=True)
  return df

# function: separate sentences
def separate_sentence(df) :
  df = replace_in_sentence(df) # 공백처리
  tokenizer = PunktSentenceTokenizer() # 문장분리 토크나이저
  sentences = {}  # 리뷰id : [문장1, 문장2...]

  for idx, row in df.iterrows() :
    temp = tokenizer.tokenize(row['text'])  # 분리된 문장들
    sentences[row['review_id']] = temp      # 딕셔너리에 저장
  return sentences

# sentence tokenizing
sentences = separate_sentence(review)

# save pickle file
path = "your_path"
with open(path+"/file_name.pkl",'wb') as f:
  pickle.dump(sentences,f)