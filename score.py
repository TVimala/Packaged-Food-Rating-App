import logging
def calculate_score(nutrients):
    """
    Computes a Nutri-Score style health score with explanations!
    """
    score = 0
    drivers = []
    evidence = []
    # --- NEGATIVE POINTS ---
    energy = nutrients.get("energy_kcal", 0)
    sugars = nutrients.get("sugars_g", 0)
    saturated_fat = nutrients.get("saturated_fat_g", 0)
    sodium = (nutrients.get("salt_g", 0) or 0) * 400
    neg_points = 0

    # Energy
    for threshold, pts in [(3350, 10), (3015, 9), (2680, 8), (2345, 7), (2010, 6), (1675, 5), (1340, 4), (1005, 3), (670, 2), (335, 1)]:
        if energy > threshold:
            neg_points += pts
            drivers.append(f"Very high energy: {energy} kcal/100g")
            evidence.append(f"Energy > {threshold} kcal/100g (Nutri-Score)")
            break
    # Sugars
    for threshold, pts in [(45, 10), (40, 9), (36, 8), (31, 7), (27, 6), (22.5, 5), (18, 4), (13.5, 3), (9, 2), (4.5, 1)]:
        if sugars > threshold:
            neg_points += pts
            drivers.append(f"High sugar content: {sugars}g/100g")
            evidence.append(f"Sugars > {threshold}g/100g (Nutri-Score / UK NHS)")
            break
    # Saturated Fat
    for threshold, pts in [(10, 10), (9, 9), (8, 8), (7, 7), (6, 6), (5, 5), (4, 4), (3, 3), (2, 2), (1, 1)]:
        if saturated_fat > threshold:
            neg_points += pts
            drivers.append(f"High saturated fat: {saturated_fat}g/100g")
            evidence.append(f"Saturated fat > {threshold}g/100g (Nutri-Score / UK NHS)")
            break
    # Sodium (as salt)
    for threshold, pts in [(900, 10), (810, 9), (720, 8), (630, 7), (540, 6), (450, 5), (360, 4), (270, 3), (180, 2), (90, 1)]:
        if sodium > threshold:
            neg_points += pts
            drivers.append(f"High sodium (as salt): {sodium/400:.2f}g/100g")
            evidence.append(f"Sodium > {threshold}mg/100g (~{threshold/400:.2f}g salt) (WHO, UK NHS)")
            break

    # --- POSITIVE POINTS ---
    fiber = nutrients.get("fiber_g", 0) or 0
    protein = nutrients.get("proteins_g", 0) or 0
    pos_points = 0

    for threshold, pts in [(4.7, 5), (3.7, 4), (2.8, 3), (1.9, 2), (0.9, 1)]:
        if fiber > threshold:
            pos_points += pts
            drivers.append(f"Good fiber content: {fiber}g/100g")
            evidence.append(f"Fiber > {threshold}g/100g (EU guideline for health claim)")
            break
    for threshold, pts in [(8.0, 5), (6.4, 4), (4.8, 3), (3.2, 2), (1.6, 1)]:
        if protein > threshold:
            pos_points += pts
            drivers.append(f"Good protein content: {protein}g/100g")
            evidence.append(f"Protein > {threshold}g/100g (Nutri-Score bonus)")
            break

    score = neg_points - pos_points

    # Band logic
    if score <= -1:
        band = "Green (A-B, Healthy)"
    elif score <= 2:
        band = "Yellow (C, Moderate)"
    else:
        band = "Red (D-E, Less Healthy)"
    logging.info(f"Score: {score}, Band: {band}")
    return score, band, drivers, evidence
