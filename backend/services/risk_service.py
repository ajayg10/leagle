import joblib
import os
import logging

logger = logging.getLogger(__name__)

class RiskService:
    _instance = None
    _model = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RiskService, cls).__new__(cls)
            cls._instance._load_model()
        return cls._instance

    def _load_model(self):
        model_path = "/home/perseuskyogre/Projects/CodeWizards/backend/ml/risk_scorer_v1.joblib"
        if os.path.exists(model_path):
            try:
                self._model = joblib.load(model_path)
                logger.info(f"✅ Local Risk Scorer loaded from {model_path}")
            except Exception as e:
                logger.error(f"❌ Failed to load Risk Scorer: {e}")
        else:
            logger.warning("⚠️ Risk Scorer model not found. Local scoring will be skipped.")

    def predict_risk(self, text: str) -> str:
        if self._model and text:
            try:
                # Get the prediction
                prediction = self._model.predict([text])[0]
                return prediction
            except Exception as e:
                logger.error(f"⚠️ Error during local risk prediction: {e}")
        return "UNKNOWN"

    def predict_risk_proba(self, text: str) -> dict:
        if self._model and text:
            try:
                # If the classifier supports predict_proba
                if hasattr(self._model.named_steps['clf'], 'predict_proba'):
                    probas = self._model.predict_proba([text])[0]
                    classes = self._model.classes_
                    return {cls: float(prob) for cls, prob in zip(classes, probas)}
            except Exception as e:
                logger.debug(f"Probabilities not available: {e}")
        return {}
