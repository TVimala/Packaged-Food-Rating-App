
def calculate_score(nutrients):
    """
    Computes an advanced health score:
    - Normalized 0-100 scale (easier for users).
    - Also maps to Nutri-Score A-E for familiarity.
    """

    score_raw = 0
    drivers = []
    evidence = []

    # --- Extract nutrients safely ---
    energy = nutrients.get("energy_kcal", 0)
    sugars = nutrients.get("sugars_g", 0)
    added_sugars = nutrients.get("added_sugars_g", 0) or 0
    saturated_fat = nutrients.get("saturated_fat_g", 0) or 0
    sodium = (nutrients.get("salt_g", 0) or 0) * 400
    fiber = nutrients.get("fiber_g", 0) or 0
    protein = nutrients.get("proteins_g", 0) or 0
    fruit_pct = nutrients.get("fruit_veg_pct", 0) or 0
    ultra_processed = nutrients.get("ultra_processed", False)

    neg_points = 0
    pos_points = 0

    # --- NEGATIVE POINTS ---
    # Energy
    for threshold, pts in [(3350, 10), (3015, 9), (2680, 8), (2345, 7), (2010, 6),
                           (1675, 5), (1340, 4), (1005, 3), (670, 2), (335, 1)]:
        if energy > threshold:
            neg_points += pts
            drivers.append(f"Very high energy: {energy} kcal/100g")
            evidence.append(f"Energy > {threshold} kcal/100g")
            break

    # Total sugars
    for threshold, pts in [(45, 10), (40, 9), (36, 8), (31, 7), (27, 6),
                           (22.5, 5), (18, 4), (13.5, 3), (9, 2), (4.5, 1)]:
        if sugars > threshold:
            neg_points += pts
            drivers.append(f"High sugar content: {sugars} g/100g")
            evidence.append(f"Sugars > {threshold} g/100g")
            break

    # Added sugars – stronger penalty
    if added_sugars > 5:
        penalty = min(10, int(added_sugars // 5))
        neg_points += penalty
        drivers.append(f"Added sugars: {added_sugars} g/100g")
        evidence.append("WHO: limit added sugar < 10% of daily energy")

    # Saturated fat
    for threshold, pts in [(10, 10), (9, 9), (8, 8), (7, 7), (6, 6),
                           (5, 5), (4, 4), (3, 3), (2, 2), (1, 1)]:
        if saturated_fat > threshold:
            neg_points += pts
            drivers.append(f"High saturated fat: {saturated_fat} g/100g")
            evidence.append(f"Saturated fat > {threshold} g/100g")
            break

    # Sodium
    for threshold, pts in [(900, 10), (810, 9), (720, 8), (630, 7), (540, 6),
                           (450, 5), (360, 4), (270, 3), (180, 2), (90, 1)]:
        if sodium > threshold:
            neg_points += pts
            drivers.append(f"High sodium: {sodium/400:.2f} g salt/100g")
            evidence.append(f"Sodium > {threshold} mg/100g")
            break

    # Ultra-processed foods → extra penalty
    if ultra_processed:
        neg_points += 3
        drivers.append("Ultra-processed food penalty")
        evidence.append("Based on NOVA classification: avoid UPFs")

    # --- POSITIVE POINTS ---
    # Fiber
    for threshold, pts in [(4.7, 5), (3.7, 4), (2.8, 3), (1.9, 2), (0.9, 1)]:
        if fiber > threshold:
            pos_points += pts
            drivers.append(f"Good fiber: {fiber} g/100g")
            evidence.append(f"Fiber > {threshold} g/100g")
            break

    # Protein
    for threshold, pts in [(8.0, 5), (6.4, 4), (4.8, 3), (3.2, 2), (1.6, 1)]:
        if protein > threshold:
            pos_points += pts
            drivers.append(f"Good protein: {protein} g/100g")
            evidence.append(f"Protein > {threshold} g/100g")
            break

    # Fruit/Vegetables content
    if fruit_pct >= 80:
        pos_points += 5
        drivers.append(f"High fruit/veg content: {fruit_pct}%")
        evidence.append("Nutri-Score bonus for ≥80% fruit/veg")
    elif fruit_pct >= 60:
        pos_points += 2
        drivers.append(f"Moderate fruit/veg content: {fruit_pct}%")
        evidence.append("Nutri-Score bonus for ≥60% fruit/veg")

    # --- FINAL SCORE ---
    score_raw = neg_points - pos_points

    # Normalize raw score → 0–100 health index
    score_norm = max(0, min(100, int(100 - ((score_raw + 15) * 2.0))))  

    # --- Health Index Bands ---
    if score_norm >= 80:
        band = "Healthy"
        grade = "A"
    elif score_norm >= 65:
        band = "Lightly Healthy"
        grade = "B"
    elif score_norm >= 50:
        band = "Moderate"
        grade = "C"
    elif score_norm >= 35:
        band = "Less Healthy"
        grade = "D"
    else:
        band = "Unhealthy"
        grade = "E"
    return score_norm, grade, band, drivers, evidence
