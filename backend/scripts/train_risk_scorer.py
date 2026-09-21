import sys
import os
import pandas as pd
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def train_model(csv_path: str, model_output_path: str):
    logger.info(f"📂 Loading dataset from {csv_path}...")
    
    # Load dataset
    df = pd.read_csv(csv_path)
    
    # Ensure columns exist
    if 'case_text' not in df.columns or 'priority' not in df.columns:
        logger.error("❌ CSV must contain 'case_text' and 'priority' columns.")
        return
    
    # Clean data
    df = df.dropna(subset=['case_text', 'priority'])
    
    X = df['case_text']
    y = df['priority']
    
    logger.info(f"📊 Dataset size: {len(df)} samples")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Create Pipeline: TF-IDF + Logistic Regression
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(max_features=10000, stop_words='english', ngram_range=(1, 2))),
        ('clf', LogisticRegression(max_iter=1000, class_weight='balanced'))
    ])
    
    logger.info("🚀 Training the local Risk Scorer model...")
    pipeline.fit(X_train, y_train)
    
    # Evaluate
    y_pred = pipeline.predict(X_test)
    logger.info("\n" + classification_report(y_test, y_pred))
    
    # Save model
    os.makedirs(os.path.dirname(model_output_path), exist_ok=True)
    joblib.dump(pipeline, model_output_path)
    logger.info(f"✅ Model saved to {model_output_path}")

if __name__ == "__main__":
    DATA_PATH = "/home/perseuskyogre/Projects/CodeWizards/backend/data/training/legal_text_classified_priority.csv"
    MODEL_PATH = "/home/perseuskyogre/Projects/CodeWizards/backend/ml/risk_scorer_v1.joblib"
    
    train_model(DATA_PATH, MODEL_PATH)
