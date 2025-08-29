from flask import Flask, render_template, request, jsonify
import numpy as np
import learning
from train import predict
import vectorize
from werkzeug.exceptions import BadRequest
import json

app = Flask(__name__)

# --- Preprocess---
def preprocess(text, vocab):
    # text must be a list of sentence
    #X = vectorize.BoW(corpus=text, vocabConnu=vocab).get_BoW_matrix()
    X = vectorize.TF_IDF(corpus=text, vocabConnu=vocab).compute_tf_idf_matrix()
    return X

# def load_model_from_json(path, model_type):
#     with open(path, "r") as f:
#         params = json.load(f)

#     if model_type == "logistic":
#         model = learning.LogisticRegression()
#         model.weights = np.array(params["weights"])
#         model.bias = params["bias"]
#     elif model_type == "naive_bayes":
#         model = learning.GaussianNB()
#         model.classes_ = np.array(params["classes"])
#         model.mean_ = np.array(params["mean"])
#         model.var_ = np.array(params["var"])
#         model.priors_ = np.array(params["priors"])
#     else:
#         raise ValueError("Unknown model type")

#     return model



# --- Routes ---
@app.route("/")
def index():
    return render_template("index.html")



model = None   # pas fixé au démarrage
@app.route("/set_model", methods=["POST"])
def set_model():
    global model
    global vocab
    choice = request.form.get("model")
    if choice == "logistic":
        model = learning.LogisticRegression()
        vocab = model.load("LogisticRegressionFR.json")   # charge les paramètres et retourne le vocabulaires associé
    elif choice == "naive_bayes":
        model = learning.GaussianNB()
        vocab = model.load("GaussianNBfr.json")


SENTIMENT = {
    0: "negative",
    1: "positive"
}


@app.route("/predict", methods=["POST"])
def predict():

    if model is None or vocab is None:
        return jsonify({"error": "Aucun modèle sélectionné. Choisissez un modèle d'abord."}), 400

    # 1. vérifier que c'est du json
    if not request.is_json:
        return jsonify({"error": "content-type must be application/json",
                        "content-type": request.content_type}), 400
    

    # 2. récupérer et valider le champ
    try:
        data = request.get_json()
    except BadRequest:
        return jsonify({"error": "invalid json"}), 400
    
    comment = data.get("text")
    if not isinstance(comment, str) or not comment:
        return jsonify({"error": "champ réquis"}), 400

    # 3. préprocessing ---> features + probas
    try:
        X = preprocess(comment, vocab)
        probas = model.predict_proba(X)
        preds = [int(np.argmax(p)) for p in probas]
    except Exception as e:
        # internal error
        return jsonify({"error": "Erreur interne lors de la prédiction",
                        "details": str(e)}), 500

    # 4. renvoyer JSON propre
    
    return jsonify({
        "classes_predites" : [SENTIMENT[pred] for pred in preds],
        "distribution": [arr.tolist() for arr in probas]
    })

if __name__ == "__main__":
    app.run(debug=True)