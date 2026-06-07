# core/similarity.py
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from core.storage import load_ideas

def get_similar_ideas(idea_id, top=5):
    ideas = load_ideas()
    if len(ideas) < 2:
        return []

    # Text aus Titel + Content kombinieren
    texts = []
    ids = []
    for idea in ideas:
        text = idea.get("title", "") + " " + idea.get("content", "")
        texts.append(text.strip())
        ids.append(idea["id"])

    # TF-IDF berechnen
    vectorizer = TfidfVectorizer(min_df=1, stop_words=None)
    try:
        tfidf_matrix = vectorizer.fit_transform(texts)
    except ValueError:
        return []

    # Index der Ziel-Idee finden
    if idea_id not in ids:
        return []
    idx = ids.index(idea_id)

    # Ähnlichkeit berechnen
    similarities = cosine_similarity(tfidf_matrix[idx], tfidf_matrix).flatten()
    similarities[idx] = 0  # eigene Idee ausschließen

    # Top N ähnlichste Ideen
    top_indices = similarities.argsort()[::-1][:top]
    result = []
    for i in top_indices:
        if similarities[i] > 0:
            result.append({
                "idea": ideas[i],
                "score": round(float(similarities[i]), 2)
            })
    return result