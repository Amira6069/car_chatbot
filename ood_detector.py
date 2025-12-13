import os
import pickle
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.svm import OneClassSVM
from sklearn.feature_extraction.text import TfidfVectorizer


class OODDetector:
    def __init__(self, dataset_path='data/cars2.csv', model_path='models/ood_detector.pkl', method='isolation', contamination=0.02):
        self.dataset_path = dataset_path
        self.model_path = model_path
        self.method = method
        self.contamination = contamination
        self.vectorizer = TfidfVectorizer(max_features=2000, ngram_range=(1, 2))
        self.model = None
        self.threshold = None

        model_dir = os.path.dirname(self.model_path)
        if model_dir:
            os.makedirs(model_dir, exist_ok=True)

        if os.path.exists(self.model_path):
            try:
                self.load()
            except Exception:
                # fallback to training if load fails
                self.fit_from_dataset()
        else:
            self.fit_from_dataset()

    def _build_texts_from_df(self, df):
        texts = []
        for _, row in df.iterrows():
            parts = []
            for col in ['Make', 'Model', 'Vehicle Style', 'Transmission Type', 'Vehicle Size']:
                if col in df.columns and pd.notna(row.get(col)):
                    parts.append(str(row.get(col)))
            texts.append(' '.join(parts))
        return texts

    def fit_from_dataset(self):
        if not os.path.exists(self.dataset_path):
            # minimal fallback: fit on a single token to avoid breaking
            self.vectorizer.fit(["car"])
            if self.method == 'isolation':
                self.model = IsolationForest(contamination=self.contamination, random_state=42)
                self.model.fit(self.vectorizer.transform(["car"]).toarray())
                self.threshold = 0.0
            else:
                self.model = OneClassSVM(nu=self.contamination, kernel='rbf', gamma='scale')
                self.model.fit(self.vectorizer.transform(["car"]).toarray())
                self.threshold = 0.0
            self.save()
            return

        df = pd.read_csv(self.dataset_path)
        texts = self._build_texts_from_df(df)
        if not texts:
            texts = ["car"]

        X = self.vectorizer.fit_transform(texts)

        if self.method == 'isolation':
            model = IsolationForest(contamination=self.contamination, random_state=42)
        else:
            model = OneClassSVM(nu=self.contamination, kernel='rbf', gamma='scale')

        # Some models expect dense arrays
        try:
            model.fit(X.toarray())
        except Exception:
            model.fit(X)

        self.model = model

        # decision_function: higher -> more inlier
        try:
            scores = model.decision_function(X.toarray())
        except Exception:
            scores = model.decision_function(X)

        # set a conservative threshold based on contamination
        self.threshold = float(np.percentile(scores, max(1.0, self.contamination * 100)))

        self.save()

    def save(self):
        with open(self.model_path, 'wb') as f:
            pickle.dump({'vectorizer': self.vectorizer, 'model': self.model, 'threshold': self.threshold, 'method': self.method}, f)

    def load(self):
        with open(self.model_path, 'rb') as f:
            data = pickle.load(f)
        self.vectorizer = data['vectorizer']
        self.model = data['model']
        self.threshold = data.get('threshold', 0.0)
        self.method = data.get('method', self.method)

    def is_in_domain(self, text):
        """Return (is_in_domain:bool, score:float).
        Conservative: if anything fails, returns True (in-domain).
        """
        try:
            x = self.vectorizer.transform([text])
            
            # Heuristic: If text contains NO known words from dataset, it is likely OOD
            if x.nnz == 0:
                return False, -1.0
                
            try:
                score = float(self.model.decision_function(x.toarray())[0])
            except Exception:
                score = float(self.model.decision_function(x)[0])

            is_in = bool(score >= self.threshold)
            return is_in, score
        except Exception:
            return True, 0.0
