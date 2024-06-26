from flask import Flask, request, jsonify
from flask_cors import CORS
import re
from nltk.stem.snowball import SnowballStemmer
import numpy as np
import pickle

with open('stopwords.txt', 'r') as f:
	stopwords = f.read().splitlines()

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


@app.route('/sentiment-prediction', methods=['POST'])
def predict():
    
	text = request.get_json()['text']
	count_vect = pickle.load(open('count_vectorizer.pkl', 'rb'))
	tfidf_transformer = pickle.load(open('tfidf_transformer.pkl', 'rb'))
	model = pickle.load(open('sentiment_model.pkl', 'rb'))
	label_encoder = pickle.load(open('label_encoder.pkl', 'rb'))
    
	preprocessed_text = text_preprocessing(text, "english", 2)
	new_text_bag_of_words = count_vect.transform([preprocessed_text])
	new_text_tf = tfidf_transformer.transform(new_text_bag_of_words)

	return jsonify({"probabilities": predict_probability(model, new_text_tf, label_encoder)})


def predict_probability(model, new_text_tf, label_encoder):
	probabilities = model.predict_proba(new_text_tf)
	sentiment_classes = label_encoder.classes_
	sentiment_probabilities = zip(sentiment_classes, probabilities[0])

	total_probability = np.sum(probabilities)
	percentage_per_sentiment = {}

	for sentiment, probability in sentiment_probabilities:
		percentage = ((probability / total_probability) * 100).round(2)
		percentage_per_sentiment[sentiment] = percentage

	sentiment_probabilities = []
	for sentiment, percentage in percentage_per_sentiment.items():
		sentiment_probabilities.append({
			"sentiment": sentiment,
			"percentage": percentage
		})
    
	return sentiment_probabilities

def text_preprocessing(text, language, minWordSize):
    text = re.sub('[^a-zA-Z]', ' ', text)
    text = text.lower()
    words = text.split()
    stop_words = set(stopwords)
    text_no_stop_words = ' '
    words = [w for w in words if not w in stop_words]
    words = [w for w in words if len(w) >= minWordSize]
    whitelist = ["n't", "not", "no"]
    for word in text.split():
        if word not in stop_words or word in whitelist:
            text_no_stop_words = text_no_stop_words + word + ' '
    text_stemmer = ' '
    stemmer = SnowballStemmer(language)
    for w in text_no_stop_words.split():
        text_stemmer = text_stemmer + stemmer.stem(w) + ' '
    text_no_short_words = ' '
    for w in text_stemmer.split():
        if len(w) >= minWordSize:
            text_no_short_words = text_no_short_words + w + ' '

    return text_no_short_words

if __name__ == "__main__":
    app.run(debug=True, port=5000, host='localhost')