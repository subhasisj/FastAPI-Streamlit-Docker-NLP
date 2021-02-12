# https://github.com/kumarvc/Fastapi-docker-kubernetes-streamlit/blob/master/app/main.py

# https://medium.com/analytics-vidhya/deploying-a-nlp-model-with-docker-and-fastapi-d972779d8008

# https://www.analyticsvidhya.com/blog/2020/12/streamlit-web-api-for-nlp-tweet-sentiment-analysis/

# https://testdriven.io/blog/fastapi-streamlit/#docker-compose

from fastapi import FastAPI
import dill
import os
import numpy as np
import uvicorn
from pydantic import BaseModel
import pandas as pd
import spacy 
from sentence_transformers import SentenceTransformer


PKL_FILENAME = "model.pkl"
MODELS_PATH = "./Models/"
MODEL_FILE_PATH = os.path.join(MODELS_PATH,PKL_FILENAME)
SENTENCE_BERT = SentenceTransformer('paraphrase-distilroberta-base-v1')
nlp = spacy.load('en_core_web_sm')


def load_model():
    with open(MODEL_FILE_PATH,'rb') as file:
        return dill.load(file)

LOADED_MODEL = load_model()

app = FastAPI(title="Ham or Spam API", description="API to predict if a SMS is ham or spam")


class Data(BaseModel):
    text:str



def make_inference_df(input_text):

    model_input_dict = {}
    input_row_list = []
    

    spacy_raw = nlp(input_text)
    # pos_tags = [t.pos_ for t in spacy_raw]

    model_input_dict['text'] = input_text
    model_input_dict['raw_pos'] =  ' '.join([t.pos_ for t in spacy_raw])
    model_input_dict['sentence-bert'] = SENTENCE_BERT.encode(input_text)

    input_row_list.append(model_input_dict)

    model_input_df = pd.DataFrame(input_row_list)
    return model_input_df

@app.get("/")
def read_root():
    return {"message": "Welcome from the API"}

@app.post("/predict")
def predict(data:Data):

    model_input_df = make_inference_df(data.text)
    prediction = LOADED_MODEL.predict_proba(model_input_df)
    print(data.text)
    ham_probability = 1 - prediction[:,1][0]
    spam_probability = prediction[:,1][0]
    print(spam_probability)
    return {
        
        "Text" : data.text,
        "prediction": "SPAM" if  prediction[:,1][0] > 0.5 else "HAM",
        "SPAM" : float(spam_probability),
        "HAM" : float(ham_probability),

    }


if __name__ == '__main__':
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)