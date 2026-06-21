from loguru import logger

VALID_CATEGORIES = [
    "Food & Dining",
    "Transport",
    "Shopping",
    "Bills & Utilities",
    "Health",
    "Entertainment",
    "Education",
    "Travel",
    "Personal Care",
    "Other",
]

CATEGORY_KEYWORDS = {
    "Food & Dining": ["restaurant", "food", "cafe", "pizza", "burger", "eat", "lunch", "dinner",
                      "breakfast", "biryani", "shawarma", "chai", "dhaba", "kfc", "mcdonalds",
                      "subway", "bbq", "grill", "bakery", "sweets", "mithai"],
    "Transport": ["uber", "careem", "fuel", "petrol", "bus", "taxi", "parking", "transport",
                  "rickshaw", "train", "metro", "toll", "cng", "indriver"],
    "Shopping": ["shop", "mall", "store", "amazon", "daraz", "clothes", "shoes", "shirt",
                 "jeans", "dress", "fashion", "outlet", "market", "bazar"],
    "Bills & Utilities": ["electric", "gas", "water", "internet", "wifi", "bill", "utility",
                          "k-electric", "sui", "ptcl", "jazz", "telenor", "zong", "ufone",
                          "recharge", "mobile", "phone", "subscription"],
    "Health": ["doctor", "hospital", "pharmacy", "medicine", "clinic", "health", "dawakhana",
               "lab", "test", "checkup", "dentist", "chemist"],
    "Entertainment": ["netflix", "movie", "cinema", "game", "spotify", "youtube", "park",
                      "concert", "ticket", "fun", "arcade", "bowling"],
    "Education": ["school", "college", "university", "course", "book", "tuition", "fee",
                  "stationery", "academy", "coaching", "library"],
    "Travel": ["hotel", "flight", "airline", "pia", "airblue", "serene", "trip", "tour",
               "booking", "hostel", "airbnb", "visa", "passport", "travel"],
    "Personal Care": ["salon", "barber", "haircut", "spa", "beauty", "cosmetics", "makeup",
                      "shampoo", "soap", "grooming", "parlour"],
}


async def categorize_expense(description: str, amount: float) -> dict:
    """
    Categorize expense using keyword matching.
    Returns: {"category": str, "confidence": float, "reasoning": str}
    """
    desc_lower = description.lower()

    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in desc_lower:
                logger.info(f"Categorized '{description}' → {category} (keyword: '{keyword}')")
                return {
                    "category": category,
                    "confidence": 0.85,
                    "reasoning": f"Matched keyword '{keyword}'"
                }

    logger.info(f"Categorized '{description}' → Other (no keyword match)")
    return {
        "category": "Other",
        "confidence": 0.5,
        "reasoning": "No matching category found"
    }