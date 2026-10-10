"""A title classifier for "about NIME topics" versus "relevant but not about NIME".

Most cited works carry only a title in Crossref, and a title alone scores far lower against the
archives than a title with an abstract, so the sweep's similarity thresholds cannot sort them.
This classifier is trained on titles only:

- positive: the titles of the NIME papers and the curated off-NIME archive;
- negative: titles from general HCI (ACM TOCHI, Personal and Ubiquitous Computing), from music
  scholarship (Contemporary Music Review) and from music information retrieval (ISMIR), which
  stand for the theory, method, HCI and musicology that NIME papers cite without being about NIME.

The negative sources contain some NIME-like papers, and the positives some that are not; the
classifier learns the dominant vocabulary of each. Five-fold cross-validated accuracy and AUC are
reported in data/topic_stats.json. Use `nime_probability(titles)`.
"""
import json
import re
from functools import lru_cache
from pathlib import Path

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.pipeline import make_pipeline

HERE = Path(__file__).resolve().parent.parent
NEGATIVE = {"ACM Transactions on Computer-Human Interaction", "Personal and Ubiquitous Computing",
            "Contemporary Music Review", "ISMIR"}


def clean(t):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", t or "")).strip()


def training_data():
    corpus = json.loads((HERE / "data" / "corpus.json").read_text())
    pos = [clean(r["title"]) for r in corpus if r["dataset"] not in ("NIME music", "NIME installations") and r["title"]]
    neg = []
    for f in ("journals.json", "proceedings_extra.json"):
        p = HERE / "data" / f
        if p.exists():
            neg += [clean(j["title"]) for j in json.loads(p.read_text()) if j["source"] in NEGATIVE]
    have = {t.lower() for t in pos}
    neg = [t for t in neg if t and t.lower() not in have and len(t.split()) >= 3]
    return pos, neg


def make_model():
    return make_pipeline(
        TfidfVectorizer(ngram_range=(1, 2), min_df=2, sublinear_tf=True, stop_words="english",
                        token_pattern=r"(?u)\b[a-zA-Z][a-zA-Z\-]{1,}\b"),
        LogisticRegression(max_iter=2000, C=4.0, class_weight="balanced"))


@lru_cache(maxsize=1)
def model():
    pos, neg = training_data()
    X, y = pos + neg, np.array([1] * len(pos) + [0] * len(neg))
    m = make_model()
    cv = StratifiedKFold(5, shuffle=True, random_state=1)
    prob = cross_val_predict(make_model(), X, y, cv=cv, method="predict_proba")[:, 1]
    stats = {"positives": len(pos), "negatives": len(neg),
             "cv_accuracy": round(float(((prob >= 0.5) == y).mean()) * 100, 1),
             "cv_auc": round(float(roc_auc_score(y, prob)), 3),
             "cv_recall_positive": round(float((prob[y == 1] >= 0.5).mean()) * 100, 1),
             "cv_recall_negative": round(float((prob[y == 0] < 0.5).mean()) * 100, 1)}
    (HERE / "data" / "topic_stats.json").write_text(json.dumps(stats, indent=1))
    m.fit(X, y)
    return m


def nime_probability(titles):
    return model().predict_proba([clean(t) for t in titles])[:, 1]


if __name__ == "__main__":
    model()
    print((HERE / "data" / "topic_stats.json").read_text())
    tests = ["Meeting the Universe Halfway: Quantum Physics and the Entanglement of Matter and Meaning",
             "Using thematic analysis in psychology", "Where the Action Is: The Foundations of Embodied Interaction",
             "The information capacity of the human motor system in controlling the amplitude of movement",
             "Musicking: The Meanings of Performing and Listening", "The Physics of Musical Instruments",
             "Sound Actions: Conceptualizing Musical Instruments", "Ocarina: Designing the iPhone's Magic Flute",
             "Bela: An embedded platform for low-latency feedback control of sound",
             "Designing New Musical Interfaces as Research: What's the Problem?",
             "Open Sound Control: an enabling technology for musical networking",
             "Embodied Music Cognition and Mediation Technology", "A tutorial on onset detection in music signals"]
    for t, p in zip(tests, nime_probability(tests)):
        print(f"{p:.2f}  {t}")
