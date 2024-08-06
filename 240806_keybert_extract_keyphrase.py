# add column matching by review id
review['sentences'] = review['review_id'].map(sentences)

# save file
# review.to_csv(path+'/file_name.csv'), index=False)

# extract keyword per sentence
keys = list(sentences.keys())
keywords_dict = {}
kw_model = KeyBERT()

with tqdm(total=len(sentences)) as pbar :
  for key in keys :
    if key in keywords_dict :
      continue
    else : 
      temp_kw = []
      for sen in sentences[key] :
        kws = kw_model.extract_keywords(sen, keyphrase_ngram_range=(1,1), stop_words=None, top_n=1)
        kw = kws[0][0] if kws else ''
        temp_kw.append(kw) 
      keywords_dict[key] = temp_kw
      pbar.update(1)
    # save pickle per 1000 keywords
    if len(keywords_dict)%1000 == 0 : 
      with open(path + '/file_name.pkl', 'wb') as f :
        pickle.dump(keywords_dict, f)
  # save pickle file when it ended
  with open(path + '/file_name.pkl', 'wb') as f :
    pickle.dump(keywords_dict, f)