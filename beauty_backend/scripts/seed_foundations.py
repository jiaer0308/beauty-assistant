import json
import os
import mysql.connector
from pathlib import Path
import webcolors
import numpy as np
import math
from skimage.color import rgb2lab

# --- Configuration ---
DB_HOST = os.environ.get("DB_HOST", "www.dcs5604.com")
DB_USER = os.environ.get("DB_USER", "baDB")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "Panda24685l$")
DB_NAME = os.environ.get("DB_NAME", "beauty_assisant")

JSON_FILE_PATH = Path(__file__).parent.parent / "app" / "data" / "lipsticks.json"

# ⚠️ NOTE: Change this to a high number (e.g., 500) or remove the cap when you want to seed everything!
LIMIT_ITEMS = 500

# ---------------------------------------------------------------------------
# Season ID Reference (matches DB `seasons` table):
#   1: Bright Spring   2: True Spring    3: Light Spring
#   4: Light Summer    5: True Summer    6: Soft Summer
#   7: Soft Autumn     8: True Autumn    9: Dark Autumn
#  10: Dark Winter    11: True Winter   12: Bright Winter
# ---------------------------------------------------------------------------

def map_base_makeup_to_seasons(hex_code: str) -> list:
    """
    Map a hex colour to best-matching season IDs based on CIELAB values.
    Tuned for Lipstick, Lip Gloss, and Lip Stain.
    Season IDs match the DB `seasons` table.
    """
    hex_code = hex_code.strip()
    if not hex_code.startswith('#'):
        hex_code = '#' + hex_code

    try:
        rgb_uint8 = webcolors.hex_to_rgb(hex_code)
    except (ValueError, AttributeError):
        return []

    rgb_norm = np.array([[[c / 255.0 for c in rgb_uint8]]], dtype=np.float64)
    lab = rgb2lab(rgb_norm)[0][0]
    L, a, b = float(lab[0]), float(lab[1]), float(lab[2])

    matched_seasons = []

    # Guard against division by zero (a* is virtually never 0 in lip products)
    safe_a = abs(a) + 0.0001

    # Derived colour dimensions
    chroma    = math.sqrt(a**2 + b**2)   # Saturation / clarity
    hue_ratio = b / safe_a               # >0.40 = warm orange-red; <0.20 = cool pink-berry

    # --- Dimension 1: Depth (by L*) ---
    depth = "medium"
    if L > 55:   depth = "light"
    elif L < 45: depth = "deep"

    # --- Dimension 2: Temperature (by hue ratio b/|a|) ---
    temp = "neutral"
    if   hue_ratio > 0.40: temp = "warm"   # orange-red, brick, caramel
    elif hue_ratio < 0.20: temp = "cool"   # rose, berry, plum

    # --- Dimension 3: Clarity (by chroma) ---
    clarity = "medium"
    if   chroma > 48: clarity = "bright"
    elif chroma < 32: clarity = "soft"

    # ==========================================
    # Core decision tree — Depth is primary axis
    # ==========================================
    if depth == "deep":
        if temp == "warm":
            matched_seasons.extend([9, 8])          # Dark Autumn, True Autumn
            if clarity == "bright":
                matched_seasons.append(2)           # True Spring (vivid deep reds)
        elif temp == "cool":
            matched_seasons.extend([10, 11])        # Dark Winter, True Winter
            if clarity == "bright":
                matched_seasons.append(12)          # Bright Winter
        else:  # neutral
            matched_seasons.extend([9, 10])         # Dark Autumn, Dark Winter
            if clarity == "bright":
                matched_seasons.extend([12, 1])     # Bright Winter, Bright Spring (oxblood)

    elif depth == "light":
        if temp == "warm":
            matched_seasons.extend([3, 2])          # Light Spring, True Spring
            if clarity == "soft":
                matched_seasons.extend([7, 9])      # Soft Autumn, Dark Autumn (burnt oranges)
        elif temp == "cool":
            matched_seasons.extend([4, 5])          # Light Summer, True Summer
            if clarity == "soft":
                matched_seasons.append(6)           # Soft Summer
        else:  # neutral
            matched_seasons.extend([3, 4])          # Light Spring, Light Summer
            if clarity == "soft":
                matched_seasons.extend([6, 7])      # Soft Summer, Soft Autumn

    else:  # medium
        if temp == "warm":
            if clarity == "bright":
                matched_seasons.extend([1, 2])      # Bright Spring, True Spring
            elif clarity == "soft":
                matched_seasons.extend([8, 7, 9])   # True Autumn, Soft Autumn, Dark Autumn
            else:
                matched_seasons.extend([8, 2, 9])   # True Autumn, True Spring, Dark Autumn
        elif temp == "cool":
            if clarity == "bright":
                matched_seasons.extend([12, 11])    # Bright Winter, True Winter
            elif clarity == "soft":
                matched_seasons.extend([5, 6, 10])  # True Summer, Soft Summer, Dark Winter
            else:
                matched_seasons.extend([5, 11, 10]) # True Summer, True Winter, Dark Winter
        else:  # neutral
            if clarity == "bright":
                matched_seasons.extend([1, 12])     # Bright Spring, Bright Winter (true red)
            elif clarity == "soft":
                matched_seasons.extend([6, 7])      # Soft Summer, Soft Autumn (dusty rose)
            else:
                matched_seasons.extend([8, 11, 9, 10])  # True Autumn, True Winter, Dark Autumn, Dark Winter

    return list(set(matched_seasons))


def parse_cosmetic_data(json_list):
    results = []
    for item in json_list:
        product_type = item.get("product_type")
        category = item.get("category")
        
        category_name = "Lipstick"
        if product_type == "foundation":
            if category == "concealer":
                category_name = "Concealer"
            elif category == "bb_cc":
                category_name = "BB/CC Cream"
            elif category == "contour":
                category_name = "Contour"
            elif category == "powder":
                category_name = "Powder"
            elif category == "cream":
                category_name = "Cream"
            elif category == "highlighter":
                category_name = "Highlighter"
            elif category == "liquid":
                category_name = "Liquid Foundation"
            elif category == "mineral":
                category_name = "Mineral"

        elif product_type == "lipstick":
            if category == "lipstick":
                category_name = "Lipstick"
            elif category == "lip_gloss":
                category_name = "Lip Gloss"
            elif category == "lip_stain":
                category_name = "Lip Stain"

        brand_name = item.get("brand", "Unknown Brand")
        if brand_name: brand_name = brand_name.strip()
            
        product_name = item.get("name", "Unknown Product")
        if product_name: product_name = product_name.strip()
            
        image_url = item.get("api_featured_image")

        colors = item.get("product_colors", [])
        if not colors:
            continue
            
        for color in colors:
            hex_value = color.get("hex_value")
            colour_name = color.get("colour_name")
            
            if not hex_value or not colour_name:
                continue
                
            full_shade_name = colour_name
            
            results.append({
                "product_name": product_name,
                "brand_name": brand_name,
                "category_name": category_name,
                "shade_name": full_shade_name,
                "hex_code": hex_value,
                "image_url": image_url
            })
            
    return results

def seed_database():
    print("🚀 Starting Foundation Seeding Process...")

    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = conn.cursor()
        print("✅ Connected to database.")
    except Exception as e:
        print(f"❌ Failed to connect to database: {e}")
        return

    try:
        with open(JSON_FILE_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"✅ Loaded JSON file with {len(data)} total records.")
    except Exception as e:
        print(f"❌ Failed to load JSON file: {e}")
        return

    parsed_items = parse_cosmetic_data(data)
    print(f"✅ Parsed {len(parsed_items)} individual shades.")

    category_cache = {}
    brand_cache = {}

    def get_or_create_category(name: str) -> int:
        if name in category_cache:
            return category_cache[name]
        cursor.execute("SELECT id FROM categories WHERE name = %s", (name,))
        row = cursor.fetchone()
        if row:
            category_cache[name] = row[0]
        else:
            cursor.execute("INSERT INTO categories (name) VALUES (%s)", (name,))
            category_cache[name] = cursor.lastrowid
            print(f"   ✨ Created category: '{name}'")
        return category_cache[name]

    def get_or_create_brand(name: str) -> int:
        if name in brand_cache:
            return brand_cache[name]
        cursor.execute("SELECT id FROM brands WHERE name = %s", (name,))
        row = cursor.fetchone()
        if row:
            brand_cache[name] = row[0]
        else:
            cursor.execute("INSERT INTO brands (name) VALUES (%s)", (name,))
            brand_cache[name] = cursor.lastrowid
            print(f"   ✨ Created brand: '{name}'")
        return brand_cache[name]

    shades_inserted = 0
    mappings_inserted = 0
    shades_skipped = 0
    processed_products = set()

    for item in parsed_items:
        if item["product_name"] not in processed_products:
            if len(processed_products) >= LIMIT_ITEMS:
                break
            processed_products.add(item["product_name"])
            print(f"\n   → Processing: '{item['product_name']}' [{item['category_name']}]")

        try:
            brand_id = get_or_create_brand(item["brand_name"])
            category_id = get_or_create_category(item["category_name"])
            product_name = item["product_name"]
            hex_code = item["hex_code"]
            shade_name = item["shade_name"]
            image_url = item["image_url"]
        except Exception as e:
            shades_skipped += 1
            continue

        try:
            cursor.execute(
                """SELECT id FROM cosmetic_products
                   WHERE brand_id = %s AND category_id = %s
                         AND hex_code = %s AND shade_name = %s""",
                (brand_id, category_id, hex_code, shade_name)
            )
            existing = cursor.fetchone()
        except Exception:
            shades_skipped += 1
            continue

        if existing:
            cosmetic_id = existing[0]
        else:
            try:
                cursor.execute(
                    """INSERT INTO cosmetic_products
                       (brand_id, category_id, product_name, shade_name, hex_code, image_url, is_active)
                       VALUES (%s, %s, %s, %s, %s, %s, TRUE)""",
                    (brand_id, category_id, product_name, shade_name, hex_code, image_url)
                )
                cosmetic_id = cursor.lastrowid
                shades_inserted += 1
            except Exception as e:
                print(f"   ❌ Insert failed: {e}")
                shades_skipped += 1
                conn.rollback()
                continue

        try:
            season_ids = map_base_makeup_to_seasons(hex_code)
        except Exception:
            season_ids = []

        for season_id in season_ids:
            try:
                cursor.execute(
                    """SELECT 1 FROM cosmetic_season_mappings
                       WHERE cosmetic_id = %s AND season_id = %s""",
                    (cosmetic_id, season_id)
                )
                if cursor.fetchone():
                    continue

                cursor.execute(
                    """INSERT INTO cosmetic_season_mappings (cosmetic_id, season_id)
                       VALUES (%s, %s)""",
                    (cosmetic_id, season_id)
                )
                mappings_inserted += 1
            except Exception:
                conn.rollback()

    try:
        conn.commit()
    except Exception as e:
        print(f"❌ Final commit failed: {e}")
        conn.rollback()

    print(f"\n🎉 Seeding Complete!")
    print(f"   - Distinct products processed  : {len(processed_products)} / {LIMIT_ITEMS}")
    print(f"   - Shades inserted              : {shades_inserted}")
    print(f"   - Season mappings inserted     : {mappings_inserted}")

    cursor.close()
    conn.close()

if __name__ == "__main__":
    seed_database()