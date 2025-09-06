def nutri_score(nutrients):
    # Negative points (bad nutrients: 0 to 40)
    energy = nutrients.get("energy_kcal", 0)
    sugars = nutrients.get("sugars_g", 0)
    saturated_fat = nutrients.get("saturated_fat_g", 0)
    sodium = (nutrients.get("salt_g", 0) or 0) * 400  # Salt -> sodium mg

    neg_points = 0
    # Energy
    for threshold, pts in [(3350, 10), (3015, 9), (2680, 8), (2345, 7), (2010, 6), (1675, 5), (1340, 4), (1005, 3), (670, 2), (335, 1)]:
        if energy > threshold: neg_points += pts; break
    # Sugars
    for threshold, pts in [(45, 10), (40, 9), (36, 8), (31, 7), (27, 6), (22.5, 5), (18, 4), (13.5, 3), (9, 2), (4.5, 1)]:
        if sugars > threshold: neg_points += pts; break
    # Sat Fat
    for threshold, pts in [(10, 10), (9, 9), (8, 8), (7, 7), (6, 6), (5, 5), (4, 4), (3, 3), (2, 2), (1, 1)]:
        if saturated_fat > threshold: neg_points += pts; break
    # Sodium (mg)
    for threshold, pts in [(900, 10), (810, 9), (720, 8), (630, 7), (540, 6), (450, 5), (360, 4), (270, 3), (180, 2), (90, 1)]:
        if sodium > threshold: neg_points += pts; break

    # Positive points (good nutrients: 0 to 15)
    fiber = nutrients.get("fiber_g", 0) or 0
    protein = nutrients.get("proteins_g", 0) or 0
    pos_points = 0
    for threshold, pts in [(4.7, 5), (3.7, 4), (2.8, 3), (1.9, 2), (0.9, 1)]:
        if fiber > threshold: pos_points += pts; break
    for threshold, pts in [(8.0, 5), (6.4, 4), (4.8, 3), (3.2, 2), (1.6, 1)]:
        if protein > threshold: pos_points += pts; break
    score = neg_points - pos_points
    # Band logic (simplified version)
    if score <= -1:
        band = "Green (A-B)"
    elif score <= 2:
        band = "Yellow (C)"
    else:
        band = "Red (D-E)"
    return score, band
