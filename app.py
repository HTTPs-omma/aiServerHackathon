import nltk
import re
import pickle
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow import keras
import requests
from sklearn.preprocessing import LabelEncoder
from dotenv import load_dotenv
import os
load_dotenv()
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime

import models.model

# Ensure necessary NLTK resources are downloaded
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

def date_diff_too_short(domain, days):
    whois_key = os.getenv('WHOISKEY')
    # 요청을 보내고 응답을 받습니다
    query = "http://apis.data.go.kr/B551505/whois/domain_name?serviceKey=" + whois_key + "&query="+ domain + "&answer=xml";
    request = urllib.request.urlopen(query).read().decode("utf-8")

    # XML 파일을 파싱합니다.
    root = ET.fromstring(request)
    
    # <regDate> 태그를 찾아 날짜 텍스트를 date_text에 저장합니다.
    for date in root.iter('regDate'):
        date_text = date.text
        break

    # 오늘 날짜를 가져옵니다.
    today = datetime.today()
    
    # 날짜 텍스트를 날짜 변수로 바꿉니다.
    regDate = datetime.strptime(date_text, "%Y. %m. %d.")
    
    # 날짜 차이를 계산합니다
    difference = today - regDate  
    
    # 등록일과 오늘 날짜가 days 일도 차이가 안 나면 True, 아니면 False 반환
    if difference.days < days :
        return True
    else:
        return False

# Load Stopwords and Initialize Lemmatizer
STOPWORDS = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()


# Function to clean and preprocess URL data
def preprocess_url(url):
    url = url.lower()  # Convert to lowercase
    url = re.sub(r'https?://', '', url)  # Remove http or https
    url = re.sub(r'www\.', '', url)  # Remove www
    url = re.sub(r'[^a-zA-Z0-9]', ' ', url)  # Remove special characters
    url = re.sub(r'\s+', ' ', url).strip()  # Remove extra spaces
    tokens = word_tokenize(url)  # Tokenize
    tokens = [word for word in tokens if word not in STOPWORDS]  # Remove stopwords
    tokens = [lemmatizer.lemmatize(word) for word in tokens]  # Lemmatization
    return ' '.join(tokens)

# Function to clean and preprocess HTML data
def preprocess_html(html):
    html = re.sub(r'<[^>]+>', ' ', html)  # Remove HTML tags
    html = html.lower()  # Convert to lowercase
    html = re.sub(r'https?://', '', html)  # Remove http or https
    html = re.sub(r'[^a-zA-Z0-9]', ' ', html)  # Remove special characters
    html = re.sub(r'\s+', ' ', html).strip()  # Remove extra spaces
    tokens = word_tokenize(html)  # Tokenize
    tokens = [word for word in tokens if word not in STOPWORDS]  # Remove stopwords
    tokens = [lemmatizer.lemmatize(word) for word in tokens]  # Lemmatization
    return ' '.join(tokens)

# Load trained model
model = keras.models.load_model('new_phishing_detection_model.keras')

# Define maximum length and number of words
max_url_length = 180
max_html_length = 2000
max_words = 10000

# Load the fitted tokenizers
with open('url_tokenizer.pkl', 'rb') as file:
    url_tokenizer = pickle.load(file)

with open('html_tokenizer.pkl', 'rb') as file:
    html_tokenizer = pickle.load(file)

# Load the label encoder
with open('label_encoder.pkl', 'rb') as file:
    label_encoder = pickle.load(file)

# Define the prediction function
def predict_phishing(url, html):
    cleaned_url = preprocess_url(url)
    cleaned_html = preprocess_html(html)

    new_url_sequences = url_tokenizer.texts_to_sequences([cleaned_url])
    new_url_padded = pad_sequences(new_url_sequences, maxlen=max_url_length, padding='post', truncating='post')

    new_html_sequences = html_tokenizer.texts_to_sequences([cleaned_html])
    new_html_padded = pad_sequences(new_html_sequences, maxlen=max_html_length, padding='post', truncating='post')

    new_predictions_prob = model.predict([new_url_padded, new_html_padded])
    new_predictions = (new_predictions_prob > 0.6).astype(int)  # Adjust threshold if needed

    predicted_category = label_encoder.inverse_transform(new_predictions)[0]
    predicted_probability = f"{new_predictions_prob[0][0]:.4f}"
    
    return predicted_category.capitalize(), predicted_probability





from flask import Flask, request, jsonify
import json
import models
from flask_cors import CORS
app = Flask(__name__)
CORS(app)  # 모든 도메인에 대해 CORS를 허용
cors = CORS(app, resources={r"/*": {"origins": "*"}})


@app.route('/predict', methods=["POST"])
def predict():
    data = request.get_json()
    url = data["url"]
    html = data["html"]
    print(url)
    
    predict_dict = predict_phishing(url, html)
    predict_dict["recentlyRegisteredURL"] = False
    # predict_dict["recentlyRegisteredURL"] = date_diff_too_short(url, 7)
    
    
    
    return jsonify(predict_dict)

@app.route('/postUrl', methods=["POST"])
def postUrl():
    data = request.get_json()
    url = data["url"]
    
    userdb = models.model.UserUrl()
    isSuccess : bool = userdb.createRecord(url)
    if isSuccess == True :
        return url, 200
    if isSuccess == False :
        return url, 404
    
    
@app.route('/getUrl', methods=["GET"])
def getUrl():
    userdb = models.model.UserUrl()
    rows = userdb.readRecord()
    return rows
    
if __name__ == '__main__':
    app.run('0.0.0.0', port=8084, debug=True)

