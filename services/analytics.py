from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import NMF

def get_top_habits_by_quality(df, quality_label, n_top=3):
    """
    Filtra el DataFrame por calidad y cuenta la frecuencia de los hábitos.
    quality_label: 0 (Mala), 1 (Regular), 2 (Buena)
    """
    # 1. Filtrar por la calidad deseada
    subset = df[df["prediction"] == quality_label]
    
    if subset.empty:
        return []

    # 2. Extraer y limpiar hábitos
    all_habits = []
    for habits_str in subset["habits"].dropna().astype(str):
        if habits_str.strip():
            # Separamos por coma y quitamos espacios
            lista = [h.strip() for h in habits_str.split(",")]
            all_habits.extend(lista)
    
    # 3. Contar frecuencias
    return Counter(all_habits).most_common(n_top)

# Lista de palabras a ignorar.
STOPWORDS_ES = {
    "el", "la", "los", "las", "un", "una", "unos", "unas", "de", "del", "y", "e", "o", "u",
    "en", "a", "ante", "con", "contra", "desde", "para", "por", "según", "sin", "sobre",
    "que", "qué", "quien", "quienes", "cual", "cuales", "este", "esta", "esto", "estos", "estas",
    "mi", "tu", "su", "me", "te", "se", "lo", "yo", "nos", "soñé", "sueño", "había", "estaba", "tenía"
}

def get_topics_by_quality(df, quality_label, n_topics=3, n_top_words=5):
    """
    Filtra por calidad de sueño y extrae tópicos usando TF-IDF + NMF.
    
    Args:
        df: DataFrame con registros de sueño
        quality_label: etiqueta de calidad.
        n_topics: número de tópicos a extraer
        n_top_words: palabras más representativas por tópico
    """

    # 1. Filtrar por calidad
    subset = df[df["prediction"] == quality_label].copy()
    textos = subset["dream_journal"].dropna().astype(str).tolist()

    # 2. Validación mínima
    textos_validos = [t for t in textos if len(t.strip()) > 10]

    if len(textos_validos) < 4:
        return None

    try:
        # 3. Vectorización TF-IDF
        vectorizer = TfidfVectorizer(
            stop_words=STOPWORDS_ES,
            max_features=1000,
            ngram_range=(1, 2)
        )

        tfidf_matrix = vectorizer.fit_transform(textos_validos)

        # 4. Modelo NMF
        nmf_model = NMF(
            n_components=n_topics,
            random_state=42
        )

        W = nmf_model.fit_transform(tfidf_matrix)
        H = nmf_model.components_

        feature_names = vectorizer.get_feature_names_out()

        topics = []

        # 5. Extraer palabras principales por tópico
        for topic_idx, topic in enumerate(H):

            top_indices = topic.argsort()[-n_top_words:][::-1]

            top_words = [
                (feature_names[i], float(topic[i]))
                for i in top_indices
            ]

            topics.append({
                "topic_id": topic_idx,
                "words": top_words
            })

        return topics

    except Exception as e:
        print(f"Error generando tópicos: {e}")
        return None

def _get_topics_by_quality(df, quality_label, n_top=5):
    """
    Filtra por calidad y extrae los tópicos más relevantes usando TF-IDF.
    """
    # 1. Filtrar y limpiar nulos
    subset = df[df["prediction"] == quality_label].copy()
    textos = subset["dream_journal"].dropna().astype(str).tolist()
    
    # 2. Validación de datos mínimos (Ej: al menos 3 relatos con texto real)
    textos_validos = [t for t in textos if len(t.strip()) > 10]
    
    if len(textos_validos) < 3:
        return None # Indica que no hay datos suficientes para este segmento

    # 3. Procesamiento TF-IDF
    try:
        vectorizer = TfidfVectorizer(
            stop_words=STOPWORDS_ES, 
            max_features=n_top,
            ngram_range=(1, 2) # (1, 2) para frases de dos palabras
        )
        tfidf_matrix = vectorizer.fit_transform(textos_validos)
        
        # Obtener palabras y sus pesos acumulados
        feature_names = vectorizer.get_feature_names_out()
        scores = tfidf_matrix.sum(axis=0).A1
        
        return sorted(zip(feature_names, scores), key=lambda x: x[1], reverse=True)
    except:
        return None
