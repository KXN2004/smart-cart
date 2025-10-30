import random
from datetime import date, timedelta

# Define brand IDs and corresponding realistic brand types for product matching
brands = {
    "b1a23f10-9f4e-4c21-9b1d-abcde000001": "Nike",
    "b1a23f10-9f4e-4c21-9b1d-abcde000002": "Adidas",
    "b1a23f10-9f4e-4c21-9b1d-abcde000003": "Uniqlo",
    "b1a23f10-9f4e-4c21-9b1d-abcde000004": "Zara",
    "b1a23f10-9f4e-4c21-9b1d-abcde000005": "H&M",
    "b1a23f10-9f4e-4c21-9b1d-abcde000006": "Levis",
    "b1a23f10-9f4e-4c21-9b1d-abcde000007": "Gucci",
    "b1a23f10-9f4e-4c21-9b1d-abcde000008": "Prada",
    "b1a23f10-9f4e-4c21-9b1d-abcde000009": "Burberry",
    "b1a23f10-9f4e-4c21-9b1d-abcde000010": "Chanel",
    "b1a23f10-9f4e-4c21-9b1d-abcde000011": "Dior",
    "b1a23f10-9f4e-4c21-9b1d-abcde000012": "Saint Laurent",
    "b1a23f10-9f4e-4c21-9b1d-abcde000013": "Tommy Hilfiger",
    "b1a23f10-9f4e-4c21-9b1d-abcde000014": "Ralph Lauren",
    "b1a23f10-9f4e-4c21-9b1d-abcde000015": "Moncler",
    "b1a23f10-9f4e-4c21-9b1d-abcde000016": "Stone Island",
    "b1a23f10-9f4e-4c21-9b1d-abcde000017": "Acne Studios",
    "b1a23f10-9f4e-4c21-9b1d-abcde000018": "Balenciaga",
    "b1a23f10-9f4e-4c21-9b1d-abcde000019": "Maison Margiela",
    "b1a23f10-9f4e-4c21-9b1d-abcde000020": "Patagonia",
    "b1a23f10-9f4e-4c21-9b1d-abcde000021": "The North Face",
    "b1a23f10-9f4e-4c21-9b1d-abcde000022": "COS",
    "b1a23f10-9f4e-4c21-9b1d-abcde000023": "Comme des Garçons",
    "b1a23f10-9f4e-4c21-9b1d-abcde000024": "G-Star RAW",
    "b1a23f10-9f4e-4c21-9b1d-abcde000025": "Gentle Monster",
}

categories = [
    "SHIRTS",
    "PANTS",
    "DRESSES",
    "JACKETS",
    "SHOES",
    "ACCESSORIES",
    "UNDERWEAR",
    "ACTIVEWEAR",
    "OUTERWEAR",
    "SLEEPWEAR",
    "SWIMWEAR",
    "SOCKS",
]

# Price ranges per brand type (simplified)
brand_price_ranges = {
    "Nike": (30, 200),
    "Adidas": (25, 180),
    "Uniqlo": (15, 60),
    "Zara": (20, 100),
    "H&M": (10, 80),
    "Levis": (40, 120),
    "Gucci": (800, 3500),
    "Prada": (700, 3000),
    "Burberry": (600, 2500),
    "Chanel": (1000, 4000),
    "Dior": (900, 3500),
    "Saint Laurent": (800, 3000),
    "Tommy Hilfiger": (50, 200),
    "Ralph Lauren": (60, 250),
    "Moncler": (1000, 2000),
    "Stone Island": (200, 600),
    "Acne Studios": (150, 500),
    "Balenciaga": (700, 1500),
    "Maison Margiela": (400, 1000),
    "Patagonia": (80, 200),
    "The North Face": (70, 250),
    "COS": (50, 200),
    "Comme des Garçons": (100, 500),
    "G-Star RAW": (60, 200),
    "Gentle Monster": (200, 400),
}

# Helper to generate random dates between 2023-01-01 and 2025-10-01
start_date = date(2023, 1, 1)
end_date = date(2025, 10, 1)


def random_date():
    delta = end_date - start_date
    return start_date + timedelta(days=random.randint(0, delta.days))


# Generate 100 realistic mock items
items = []
for i in range(1, 101):
    brand_id, brand_name = random.choice(list(brands.items()))
    category = random.choice(categories)
    price_min, price_max = brand_price_ranges[brand_name]
    marked_price = round(random.uniform(price_min, price_max), 2)
    discounted_price = round(marked_price * random.uniform(0.7, 0.95), 2)
    quantity = (
        random.randint(5, 200) if price_max < 500 else random.randint(5, 50)
    )  # Luxury lower stock
    restocked_at = random_date().isoformat()
    name = f"{brand_name} {category.title()} {i}"
    description = f"High-quality {category.lower()} by {brand_name}."
    # Escape quotes for SQL
    name = name.replace("'", "''")
    description = description.replace("'", "''")
    items.append(
        f"({i}, '{name}', '{description}', {marked_price}, {discounted_price}, {quantity}, '{brand_id}', '{category}', '{restocked_at}')"
    )

# Combine into full SQL insert
sql = (
    "INSERT INTO Item (id, name, description, marked_price, discounted_price, quantity, brand, category, restocked_at) VALUES\n"
    + ",\n".join(items)
    + ";"
)
print(sql)
