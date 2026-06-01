"""
Run once (or periodically) to build locations.json — a pool of validated
Street View coordinates. The app then picks from this pool instantly.

Usage: python generate_pool.py
"""

import json
import random
from streetview import search_panoramas

# (lat_min, lat_max, lng_min, lng_max, weight)
# Weight is proportional to approximate land area / Street View coverage density
LAND_BOXES = [
    (25,  70,  -125,  -60,  12),   # North America (mainland)
    (15,  25,  -105,  -75,   4),   # Central America / Mexico
    (-55, 15,   -82,  -34,  10),   # South America
    (35,  70,   -10,   40,  14),   # Europe
    (-35, 37,   -18,   52,   8),   # Africa
    (30,  75,    25,   65,   6),   # Russia / Central Asia (west)
    (40,  75,    60,  135,   6),   # Russia / Central Asia (east)
    ( 5,  40,    60,  100,   8),   # South Asia (India, Pakistan)
    ( 1,  55,   100,  145,  10),   # East / SE Asia
    (30,  45,   130,  145,   4),   # Japan / Korean peninsula
    (-45, -10,  110,  155,   5),   # Australia
    (-47,  -1,  165,  179,   1),   # New Zealand
]

POOL_SIZE = 200
OUT_FILE = "locations.json"


def weighted_random_box():
    total = sum(w for *_, w in LAND_BOXES)
    r = random.uniform(0, total)
    cumulative = 0
    for lat_min, lat_max, lng_min, lng_max, w in LAND_BOXES:
        cumulative += w
        if r <= cumulative:
            return lat_min, lat_max, lng_min, lng_max
    return LAND_BOXES[-1][:4]


def find_valid_location(max_attempts=10):
    for _ in range(max_attempts):
        lat_min, lat_max, lng_min, lng_max = weighted_random_box()
        lat = random.uniform(lat_min, lat_max)
        lng = random.uniform(lng_min, lng_max)
        panos = search_panoramas(lat=lat, lon=lng)
        if panos:
            p = panos[0]
            return {"lat": p.lat, "lng": p.lon, "id": p.pano_id}
    return None


def main():
    pool = []
    attempts = 0
    print(f"Building pool of {POOL_SIZE} locations...")
    while len(pool) < POOL_SIZE:
        attempts += 1
        loc = find_valid_location()
        if loc:
            pool.append(loc)
            print(f"  [{len(pool)}/{POOL_SIZE}] {loc['lat']:.4f}, {loc['lng']:.4f}")

    with open(OUT_FILE, "w") as f:
        json.dump(pool, f, indent=2)

    hit_rate = POOL_SIZE / attempts * 100
    print(f"\nDone. {POOL_SIZE} locations saved to {OUT_FILE} ({hit_rate:.1f}% hit rate)")


if __name__ == "__main__":
    main()
