"""
Ashtakoot Guna Milan (8-fold compatibility matching) - classical Vedic matching system.
Total possible score: 36 points across 8 kootas.
Rules follow the standard system used by Lahiri-based panchang software.
"""
from astro_core import NAKSHATRAS, RASHIS

# ---------- Reference tables keyed by nakshatra index (0-26) ----------

# Varna (spiritual class) by RASHI (moon sign), not nakshatra
VARNA_BY_RASHI = {
    0: "Kshatriya", 1: "Vaishya", 2: "Shudra", 3: "Brahmin", 4: "Kshatriya", 5: "Vaishya",
    6: "Shudra", 7: "Brahmin", 8: "Kshatriya", 9: "Vaishya", 10: "Shudra", 11: "Brahmin",
}
VARNA_RANK = {"Brahmin": 4, "Kshatriya": 3, "Vaishya": 2, "Shudra": 1}

# Vashya group by rashi index
VASHYA_GROUP_BY_RASHI = {
    0: "Chatushpad", 1: "Chatushpad", 2: "Manav", 3: "Jalachar", 4: "Vanachar", 5: "Manav",
    6: "Manav", 7: "Keeta", 8: "Manav_half_Chatushpad_half", 9: "Chatushpad_half_Jalachar_half",
    10: "Manav", 11: "Jalachar",
}
# Vashya score matrix (simplified standard table), max 2 points
VASHYA_SCORE = {
    ("Chatushpad", "Chatushpad"): 2, ("Manav", "Manav"): 2, ("Jalachar", "Jalachar"): 2,
    ("Keeta", "Keeta"): 2, ("Vanachar", "Vanachar"): 1,
    ("Chatushpad", "Manav"): 1, ("Manav", "Chatushpad"): 1,
    ("Chatushpad", "Jalachar"): 0.5, ("Jalachar", "Chatushpad"): 0.5,
    ("Manav", "Jalachar"): 1, ("Jalachar", "Manav"): 1,
    ("Vanachar", "Chatushpad"): 0.5, ("Chatushpad", "Vanachar"): 0,
    ("Vanachar", "Manav"): 0, ("Manav", "Vanachar"): 0.5,
    ("Keeta", "Manav"): 0.5, ("Manav", "Keeta"): 0.5,
}

# Nakshatra -> Tara group counting is computed by index distance, not a table

# Yoni (physical/sexual compatibility) by nakshatra index -> animal
YONI_ANIMAL = {
    0: "Horse", 1: "Elephant", 2: "Sheep", 3: "Serpent", 4: "Serpent", 5: "Dog",
    6: "Cat", 7: "Sheep", 8: "Cat", 9: "Rat", 10: "Rat", 11: "Cow",
    12: "Buffalo", 13: "Tiger", 14: "Buffalo", 15: "Tiger", 16: "Deer", 17: "Deer",
    18: "Dog", 19: "Monkey", 20: "Mongoose", 21: "Monkey", 22: "Lion", 23: "Horse",
    24: "Lion", 25: "Cow", 26: "Elephant",
}
YONI_ENEMY_PAIRS = {
    frozenset(["Cat", "Rat"]), frozenset(["Cow", "Tiger"]), frozenset(["Snake", "Mongoose"]),
    frozenset(["Serpent", "Mongoose"]), frozenset(["Dog", "Deer"]), frozenset(["Monkey", "Sheep"]),
    frozenset(["Lion", "Elephant"]), frozenset(["Horse", "Buffalo"]),
}
YONI_SAME_GROUP_OPPOSITE_GENDER = {"Sheep": "Sheep"}  # placeholder, most same-yoni pairs score 4

# Graha Maitri: friendship of rashi lords
RASHI_LORD = {
    0: "Mars", 1: "Venus", 2: "Mercury", 3: "Moon", 4: "Sun", 5: "Mercury",
    6: "Venus", 7: "Mars", 8: "Jupiter", 9: "Saturn", 10: "Saturn", 11: "Jupiter",
}
FRIENDSHIP = {
    "Sun": {"friend": ["Moon", "Mars", "Jupiter"], "enemy": ["Venus", "Saturn"], "neutral": ["Mercury"]},
    "Moon": {"friend": ["Sun", "Mercury"], "enemy": [], "neutral": ["Mars", "Jupiter", "Venus", "Saturn"]},
    "Mars": {"friend": ["Sun", "Moon", "Jupiter"], "enemy": ["Mercury"], "neutral": ["Venus", "Saturn"]},
    "Mercury": {"friend": ["Sun", "Venus"], "enemy": ["Moon"], "neutral": ["Mars", "Jupiter", "Saturn"]},
    "Jupiter": {"friend": ["Sun", "Moon", "Mars"], "enemy": ["Mercury", "Venus"], "neutral": ["Saturn"]},
    "Venus": {"friend": ["Mercury", "Saturn"], "enemy": ["Sun", "Moon"], "neutral": ["Mars", "Jupiter"]},
    "Saturn": {"friend": ["Mercury", "Venus"], "enemy": ["Sun", "Moon", "Mars"], "neutral": ["Jupiter"]},
}

# Gana (temperament) by nakshatra index
GANA = {
    0: "Deva", 1: "Manushya", 2: "Rakshasa", 3: "Manushya", 4: "Deva", 5: "Manushya",
    6: "Deva", 7: "Deva", 8: "Rakshasa", 9: "Rakshasa", 10: "Manushya", 11: "Manushya",
    12: "Deva", 13: "Rakshasa", 14: "Deva", 15: "Rakshasa", 16: "Deva", 17: "Rakshasa",
    18: "Rakshasa", 19: "Manushya", 20: "Manushya", 21: "Deva", 22: "Rakshasa", 23: "Rakshasa",
    24: "Manushya", 25: "Manushya", 26: "Deva",
}

# Nadi (health/genetic lineage) by nakshatra index
NADI = {
    0: "Aadi", 1: "Madhya", 2: "Antya", 3: "Aadi", 4: "Madhya", 5: "Antya",
    6: "Aadi", 7: "Madhya", 8: "Antya", 9: "Aadi", 10: "Madhya", 11: "Antya",
    12: "Aadi", 13: "Madhya", 14: "Antya", 15: "Aadi", 16: "Madhya", 17: "Antya",
    18: "Aadi", 19: "Madhya", 20: "Antya", 21: "Aadi", 22: "Madhya", 23: "Antya",
    24: "Aadi", 25: "Madhya", 26: "Antya",
}


def varna_koota(boy_rashi_idx, girl_rashi_idx):
    b, g = VARNA_BY_RASHI[boy_rashi_idx], VARNA_BY_RASHI[girl_rashi_idx]
    score = 1 if VARNA_RANK[b] >= VARNA_RANK[g] else 0
    return score, 1, f"Groom varna {b}, bride varna {g}"


def vashya_koota(boy_rashi_idx, girl_rashi_idx):
    bg = VASHYA_GROUP_BY_RASHI[boy_rashi_idx]
    gg = VASHYA_GROUP_BY_RASHI[girl_rashi_idx]
    # collapse split groups to their primary category for scoring simplicity
    simplify = lambda x: x.split("_")[0]
    bg, gg = simplify(bg), simplify(gg)
    score = VASHYA_SCORE.get((bg, gg), 1)
    return score, 2, f"Groom group {bg}, bride group {gg}"


def tara_koota(boy_nak_idx, girl_nak_idx):
    # count nakshatras from boy to girl and girl to boy, mod 9, groups of 3 are auspicious
    def tara_group_score(from_idx, to_idx):
        count = ((to_idx - from_idx) % 27) + 1
        remainder = count % 9
        # Classical rule: Tara groups 1,3,5,7,9 (i.e. remainder 1,3,5,7,0) are auspicious (Janma,
        # Sampat, Kshema, Sadhana, Mitra/Parama-Mitra); groups 2,4,6,8 are inauspicious.
        return 1.5 if remainder in (1, 3, 5, 7, 0) else 0

    s1 = tara_group_score(boy_nak_idx, girl_nak_idx)
    s2 = tara_group_score(girl_nak_idx, boy_nak_idx)
    score = s1 + s2
    return score, 3, f"Boy nakshatra #{boy_nak_idx+1}, girl nakshatra #{girl_nak_idx+1}"


def yoni_koota(boy_nak_idx, girl_nak_idx):
    b_animal = YONI_ANIMAL[boy_nak_idx]
    g_animal = YONI_ANIMAL[girl_nak_idx]
    if b_animal == g_animal:
        score = 4
    elif frozenset([b_animal, g_animal]) in YONI_ENEMY_PAIRS:
        score = 0
    else:
        score = 2  # neutral/friendly pairing default
    return score, 4, f"Groom yoni {b_animal}, bride yoni {g_animal}"


def graha_maitri_koota(boy_rashi_idx, girl_rashi_idx):
    b_lord = RASHI_LORD[boy_rashi_idx]
    g_lord = RASHI_LORD[girl_rashi_idx]
    if b_lord == g_lord:
        score = 5
    elif g_lord in FRIENDSHIP[b_lord]["friend"] and b_lord in FRIENDSHIP[g_lord]["friend"]:
        score = 5
    elif g_lord in FRIENDSHIP[b_lord]["enemy"] or b_lord in FRIENDSHIP[g_lord]["enemy"]:
        score = 0
    elif g_lord in FRIENDSHIP[b_lord]["friend"] or b_lord in FRIENDSHIP[g_lord]["friend"]:
        score = 4
    else:
        score = 3  # neutral
    return score, 5, f"Groom rashi lord {b_lord}, bride rashi lord {g_lord}"


def gana_koota(boy_nak_idx, girl_nak_idx):
    b_gana = GANA[boy_nak_idx]
    g_gana = GANA[girl_nak_idx]
    if b_gana == g_gana:
        score = 6
    elif {b_gana, g_gana} == {"Deva", "Manushya"}:
        score = 5
    elif {b_gana, g_gana} == {"Manushya", "Rakshasa"}:
        score = 1
    elif {b_gana, g_gana} == {"Deva", "Rakshasa"}:
        score = 0
    else:
        score = 0
    return score, 6, f"Groom gana {b_gana}, bride gana {g_gana}"


def bhakoot_koota(boy_rashi_idx, girl_rashi_idx):
    diff = abs(boy_rashi_idx - girl_rashi_idx)
    diff = min(diff, 12 - diff) if diff > 6 else diff
    # classical inauspicious distances: 6/8 (Shadashtak) and 2/12 (Dwirdwadash)
    raw_diff = (girl_rashi_idx - boy_rashi_idx) % 12
    inauspicious = raw_diff in (1, 5, 6, 8, 11) or ((boy_rashi_idx - girl_rashi_idx) % 12) in (1, 5, 6, 8, 11)
    score = 0 if inauspicious else 7
    return score, 7, f"Groom rashi {RASHIS[boy_rashi_idx]}, bride rashi {RASHIS[girl_rashi_idx]}"


def nadi_koota(boy_nak_idx, girl_nak_idx):
    b_nadi = NADI[boy_nak_idx]
    g_nadi = NADI[girl_nak_idx]
    score = 0 if b_nadi == g_nadi else 8
    return score, 8, f"Groom nadi {b_nadi}, bride nadi {g_nadi}"


def compute_ashtakoot(boy_moon: dict, girl_moon: dict) -> dict:
    b_nak, g_nak = boy_moon["nakshatra_index"], girl_moon["nakshatra_index"]
    b_rashi, g_rashi = boy_moon["rashi_index"], girl_moon["rashi_index"]

    kootas = {}
    kootas["Varna"] = varna_koota(b_rashi, g_rashi)
    kootas["Vashya"] = vashya_koota(b_rashi, g_rashi)
    kootas["Tara"] = tara_koota(b_nak, g_nak)
    kootas["Yoni"] = yoni_koota(b_nak, g_nak)
    kootas["Graha Maitri"] = graha_maitri_koota(b_rashi, g_rashi)
    kootas["Gana"] = gana_koota(b_nak, g_nak)
    kootas["Bhakoot"] = bhakoot_koota(b_rashi, g_rashi)
    kootas["Nadi"] = nadi_koota(b_nak, g_nak)

    total_score = sum(v[0] for v in kootas.values())
    max_score = sum(v[1] for v in kootas.values())  # should be 36

    nadi_dosha = kootas["Nadi"][0] == 0
    bhakoot_dosha = kootas["Bhakoot"][0] == 0

    return {
        "kootas": kootas,
        "total_score": total_score,
        "max_score": max_score,
        "nadi_dosha": nadi_dosha,
        "bhakoot_dosha": bhakoot_dosha,
    }


if __name__ == "__main__":
    from astro_core import compute_moon_position
    # placeholder manual test using fixed nakshatra/rashi (bypassing geocoding, since sandbox blocks it)
    boy = {"nakshatra_index": 4, "rashi_index": 1}   # Mrigashira, Taurus
    girl = {"nakshatra_index": 13, "rashi_index": 6}  # Chitra, Libra
    result = compute_ashtakoot(boy, girl)
    for name, (score, maxs, note) in result["kootas"].items():
        print(f"{name}: {score}/{maxs}  ({note})")
    print(f"TOTAL: {result['total_score']}/{result['max_score']}")
