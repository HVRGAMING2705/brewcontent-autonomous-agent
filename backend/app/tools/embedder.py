from sentence_transformers import SentenceTransformer
from typing import List
import numpy as np

_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
_model: SentenceTransformer | None = None


def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(_MODEL_NAME)
    return _model


class Embedder:
    """Generates 384-dim embeddings using all-MiniLM-L6-v2."""

    def embed_text(self, text: str) -> List[float]:
        """Embed a single string and return a plain Python list of floats."""
        model = _get_model()
        vector: np.ndarray = model.encode(text, normalize_embeddings=True)
        return vector.tolist()
