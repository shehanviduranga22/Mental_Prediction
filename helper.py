import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import re
import string
import pickle
import json
import random

from nltk.stem import PorterStemmer
ps = PorterStemmer()

with open('static/model/model.pickle', 'rb') as f:
    model = pickle.load(f)

import nltk
with open('static/model/nltk_data/corpora/stopwords/english', 'r') as file:
    sw = file.read().splitlines()

vocab = pd.read_csv('static/model/vocablary.txt', header=None)
tokens = vocab[0].tolist()

def preprocessing(text):
    data = pd.DataFrame([text], columns=['statement'])
    data["statement"] = data["statement"].astype(str).apply(lambda x: " ".join(word.lower() for word in x.split()))
    
    data["statement"] = data["statement"].astype(str).apply(
        lambda x: " ".join(re.sub(r'https?://\S+|www\.\S+', '', word)for word in x.split()))
    
    data["statement"] = data["statement"].astype(str).apply(
        lambda x: x.translate(str.maketrans('', '', string.punctuation)))
    
    data["statement"] = data["statement"].astype(str).apply(
        lambda x: re.sub(r'\d+', '', x))
    
    data["statement"] = data["statement"].astype(str).apply(
        lambda x: " ".join(word for word in x.split() if word.lower() not in sw))
    
    data["statement"] = data["statement"].astype(str).apply(
        lambda x: " ".join(ps.stem(x) for x in x.split()))

    return data ["statement"]


def vectorizer(ds):
    vectorized_lst = []

    for sentence in ds:
        sentence_lst = np.zeros(len(tokens))

        for i in range(len(tokens)):
            if tokens[i] in sentence.split():
                sentence_lst[i] = 1

        vectorized_lst.append(sentence_lst)

    vectorized_lst_new = np.asarray(vectorized_lst, dtype = np.float32)

    return vectorized_lst_new


def get_prediction(vectorized_txt):
    prediction = model.predict(vectorized_txt)[0]

    instruction = None  # safety

    with open("instructions.json", "r", encoding="utf-8") as file:
        intents = json.load(file)

    for intent in intents["intents"]:
        if intent["tag"] == prediction:
            instruction = random.choice(intent["pattersns"])
            break

    return prediction, instruction
