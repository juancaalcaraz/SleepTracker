from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer

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
def get_topics_by_quality(df, quality_label, n_top=5):
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
