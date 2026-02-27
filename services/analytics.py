from collections import Counter

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

