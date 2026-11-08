"""Indonesian SMS classifier: normal / promo / spam.

Preprocessing and features are the same as `preproccess_text` / `find_features` in
github.com/agustinustheo/sms-classifier-model (the EIConCIT 2021 paper code).
The model in `model/` is that repo's linear SVM trained on the full 4,125-message
dataset (sms-classifier-model @ b0f81ef, scikit-learn 1.9.1).
"""

import pickle
import re
from functools import lru_cache
from pathlib import Path

import nltk
from nltk.tokenize import word_tokenize

MODEL_DIR = Path(__file__).resolve().parent / "model"
LABELS = {0: "normal", 1: "promo", 2: "spam"}

_DELEET = str.maketrans("1234567890", "iseasgtbgo")


def convert_tacky_text(text):
    """Turn "alay" spelling into letters inside mixed tokens ("m4ma" -> "mama")."""
    out = []
    for word in word_tokenize(text):
        if any(c.isalpha() for c in word) and any(c.isdigit() for c in word):
            word = word.lower()
            if not (word.endswith("ribu") or word.endswith("rbu") or word.endswith("rb")):
                word = word.translate(_DELEET)
        out.append(word)
    return " ".join(out) + " "


def preprocess(text):
    processed = convert_tacky_text(text.lower())
    processed = re.sub(r"^.+@[^\.].*\.[a-z]{2,}$", " emailaddress ", processed)
    processed = re.sub(r"(\()?(\+62|62|0)(\d{2,3})?\)?[ .-]?\d{2,4}[ .-]?\d{2,4}[ .-]?\d{2,4}", " phonenumber ", processed)
    processed = re.sub(r"[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)", " webaddress ", processed)
    processed = processed.replace("http", "").replace("https", "")
    processed = re.sub(r"£|\$", "moneysymbol ", processed)
    processed = processed.replace(" rp.", " moneysymbol ").replace(" rp", " moneysymbol ")
    processed = re.sub(r"\d+(\.\d+)?", " number ", processed)
    processed = re.sub(r"[.,\/#!%\^&\*;:+{}=\-_`~()?]", " ", processed)
    processed = re.sub(r"\s+", " ", processed)
    return re.sub(r"^\s+|\s+?$", "", processed)


@lru_cache(maxsize=1)
def _load():
    """Load once per process. The pickles are this repo's own files; never load pickles you didn't create."""
    try:
        nltk.data.find("tokenizers/punkt_tab")
    except LookupError:
        nltk.download("punkt_tab", quiet=True)
    with open(MODEL_DIR / "word_features.pickle", "rb") as f:
        word_features = pickle.load(f)
    with open(MODEL_DIR / "svm_linear.pickle", "rb") as f:
        model = pickle.load(f)
    return word_features, model


def classify(text):
    word_features, model = _load()
    words = set(word_tokenize(preprocess(text)))
    features = {w: (w in words) for w in word_features}
    return LABELS[model.classify(features)]
