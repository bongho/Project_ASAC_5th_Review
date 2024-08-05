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

# replace unnecessary part of sentence
def replace_in_sentence(df) :
  df['text'] = df['text'].str.replace(r'\n', ' ', regex=True)
  df['text'] = df['text'].str.replace(r'\(\?*\)', ' ', regex=True)
  df['text'] = df['text'].str.replace(r'\(\?,\s*\?\)', ' ', regex=True)
  return df

# separate sentences
def separate_sentence(df) :
  df = replace_in_sentence(df) # 공백처리
  tokenizer = PunktSentenceTokenizer() # 문장분리 토크나이저
  sentences = {}  # 리뷰id : [문장1, 문장2...]

  for idx, row in df.iterrows() :
    temp = tokenizer.tokenize(row['text'])  # 분리된 문장들
    sentences[row['review_id']] = temp      # 딕셔너리에 저장
  return sentences

# save variable
sentences = separate_sentence(review)

# add column matching by review id
review['sentences'] = review['review_id'].map(sentences)

# save file
# review.to_csv(path, index=False)

# extract keyword per sentence
keys = list(sentences.keys())
keywords_dict = {}
kw_model = KeyBERT()

# if stopped in progress
# with open(path + '/file_name.pkl', 'rb') as f :
#     keywords_dict = pickle.load(f)

with tqdm(total=len(sentences)) as pbar :
  for key in keys :
    if key in keywords_dict :
      pass
    else : 
      temp_kw = []
      for sen in sentences[key] :
        kws = kw_model.extract_keywords(sen, keyphrase_ngram_range=(1,1), stop_words=None, top_n=1)
        kw = kws[0][0] if kws else ''
        temp_kw.append(kw) 
      keywords_dict[key] = temp_kw
    pbar.update(1)
    # save pickle per 10000 keywords
    if len(keywords_dict)%10000 == 0 : 
      with open(path + '/file_name.pkl', 'wb') as f :
        pickle.dump(keywords_dict, f)