"""Idempotent seed script for CookKart product catalogue (Phase 4 completion).

Usage (from backend/):
  .\\.venv\\Scripts\\python.exe seed_catalog.py

Inserts demonstration catalogue categories/products if missing. Safe to run multiple times.
Does not delete or overwrite existing records.
"""

from __future__ import annotations

from decimal import Decimal

from sqlalchemy import select

from app.database.session import SessionLocal
from app.models.catalog import Product, ProductCategory


CATEGORIES = [
    {
        "name": "South Indian Staples",
        "slug": "south-indian-staples",
        "description": "Essential staples commonly used in South Indian home cooking.",
    },
    {
        "name": "Rice & Grains",
        "slug": "rice-and-grains",
        "description": "Everyday rice, millets, and grain essentials for Indian meals.",
    },
    {
        "name": "Pulses & Dals",
        "slug": "pulses-and-dals",
        "description": "Lentils and pulses for dals, sambars, and protein-rich dishes.",
    },
    {
        "name": "Spices & Masalas",
        "slug": "spices-and-masalas",
        "description": "Whole spices and spice mixes for aromatic Indian cooking.",
    },
    {
        "name": "Vegetables",
        "slug": "vegetables",
        "description": "Fresh vegetable staples for everyday curries and sides.",
    },
    {
        "name": "Fruits",
        "slug": "fruits",
        "description": "Popular fruits for snacking, breakfast, and desserts.",
    },
    {
        "name": "Dairy & Eggs",
        "slug": "dairy-and-eggs",
        "description": "Dairy essentials and eggs for cooking and daily use.",
    },
    {
        "name": "Cooking Essentials",
        "slug": "cooking-essentials",
        "description": "Oils, flours, sweeteners, and pantry basics for the kitchen.",
    },
]

# Demonstration catalogue records only (not real-time inventory or sales claims).
# image_url uses external URLs where practical; frontend provides fallbacks if unavailable.
PRODUCTS = [
    # South Indian Staples
    ("south-indian-staples", "Idli Rice", "idli-rice-5kg", "Parboiled rice suited for soft idlis and dosas.", "320.00", "kg", "5 kg", True, "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2d/Rice_Grains_1.jpg/960px-Rice_Grains_1.jpg"),
    ("south-indian-staples", "Dosa Rice", "dosa-rice-5kg", "Short-grain rice ideal for crisp dosas.", "300.00", "kg", "5 kg", True, "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6e/Uncooked_ST25_rice_on_bamboo_surface.jpg/960px-Uncooked_ST25_rice_on_bamboo_surface.jpg"),
    ("south-indian-staples", "Urad Dal Whole", "urad-dal-whole-1kg", "Whole black gram for idli/dosa batter and traditional recipes.", "185.00", "kg", "1 kg", True, "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6f/Black_gram.jpg/960px-Black_gram.jpg"),
    ("south-indian-staples", "Urad Dal Split", "urad-dal-split-1kg", "Split urad dal for tempering, vadas, and chutneys.", "175.00", "kg", "1 kg", True, "https://upload.wikimedia.org/wikipedia/commons/thumb/0/09/%E0%AE%89%E0%AE%B4%E0%AF%81%E0%AE%A8%E0%AF%8D%E0%AE%A4%E0%AF%81_3.JPG/960px-%E0%AE%89%E0%AE%B4%E0%AF%81%E0%AE%A8%E0%AF%8D%E0%AE%A4%E0%AF%81_3.JPG"),
    ("south-indian-staples", "Roasted Rava (Sooji)", "roasted-rava-1kg", "Roasted semolina for upma, kesari, and quick tiffin dishes.", "78.00", "kg", "1 kg", True, "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c6/Sa_semolina_far.jpg/960px-Sa_semolina_far.jpg"),
    ("south-indian-staples", "Rice Flour", "rice-flour-1kg", "Fine rice flour for dosas, appams, and snacks.", "65.00", "kg", "1 kg", True, "https://upload.wikimedia.org/wikipedia/commons/1/19/Two_kinds_of_rice_flour.jpg"),
    ("south-indian-staples", "Poha (Flattened Rice)", "poha-medium-1kg", "Medium flattened rice for aval upma and quick breakfasts.", "72.00", "kg", "1 kg", True, "https://images.unsplash.com/photo-1604329760661-e71dc83f8f26?auto=format&fit=crop&w=800&q=80"),
    ("south-indian-staples", "Tamarind", "tamarind-block-500g", "Tamarind block for sambar, rasam, and puliyogare.", "95.00", "g", "500 g", True, "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c1/Tamarind2.jpg/960px-Tamarind2.jpg"),
    ("south-indian-staples", "Jaggery Powder", "jaggery-powder-1kg", "Natural jaggery powder for sweets and traditional recipes.", "110.00", "kg", "1 kg", True, "https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/An_image_of_jaggery_powder.JPG/960px-An_image_of_jaggery_powder.JPG"),

    # Rice & Grains
    ("rice-and-grains", "Sona Masoori Rice", "sona-masoori-rice-5kg", "Light aromatic rice for everyday South Indian meals.", "360.00", "kg", "5 kg", True, "https://upload.wikimedia.org/wikipedia/commons/thumb/2/29/Masoori_Rice_%285193854729%29.jpg/960px-Masoori_Rice_%285193854729%29.jpg"),
    ("rice-and-grains", "Basmati Rice", "basmati-rice-5kg", "Long-grain basmati rice for biryani and pulao.", "720.00", "kg", "5 kg", True, "https://images.unsplash.com/photo-1586201375761-83865001e31c?auto=format&fit=crop&w=800&q=80"),
    ("rice-and-grains", "Brown Rice", "brown-rice-1kg", "Whole-grain brown rice for wholesome meals.", "145.00", "kg", "1 kg", True, "https://upload.wikimedia.org/wikipedia/commons/d/d1/Reis_-_Sorte_C_voll.jpg"),
    ("rice-and-grains", "Foxtail Millet", "foxtail-millet-1kg", "Nutritious millet suitable for upma, pongal, and salads.", "160.00", "kg", "1 kg", True, "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f1/Food_grain_foxtail_millet.jpg/960px-Food_grain_foxtail_millet.jpg"),
    ("rice-and-grains", "Little Millet", "little-millet-1kg", "Versatile little millet for healthy everyday cooking.", "155.00", "kg", "1 kg", True, "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f8/A_closeup_fo_Samai_millet_with_husk.JPG/960px-A_closeup_fo_Samai_millet_with_husk.JPG"),
    ("rice-and-grains", "Whole Wheat Atta", "whole-wheat-atta-5kg", "Stone-ground whole wheat flour for chapatis and parathas.", "260.00", "kg", "5 kg", True, "https://upload.wikimedia.org/wikipedia/commons/1/11/Wheat-flour.jpg"),
    ("rice-and-grains", "Vermicelli (Semiya)", "vermicelli-semiya-500g", "Roasted semiya for upma and payasam.", "55.00", "g", "500 g", True, "https://images.unsplash.com/photo-1621996346565-e3dbc646d9a9?auto=format&fit=crop&w=800&q=80"),

    # Pulses & Dals
    ("pulses-and-dals", "Toor Dal", "toor-dal-1kg", "Split pigeon peas for sambar and everyday dal.", "210.00", "kg", "1 kg", True, "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a2/Tur_Dal.JPG/960px-Tur_Dal.JPG"),
    ("pulses-and-dals", "Moong Dal", "moong-dal-1kg", "Split yellow moong dal for light dals and khichdi.", "165.00", "kg", "1 kg", True, "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2a/Moong_Dal.jpg/960px-Moong_Dal.jpg"),
    ("pulses-and-dals", "Masoor Dal", "masoor-dal-1kg", "Red lentils for quick-cooking dals and soups.", "150.00", "kg", "1 kg", True, "https://upload.wikimedia.org/wikipedia/commons/3/38/Masoor_dal.JPG"),
    ("pulses-and-dals", "Chana Dal", "chana-dal-1kg", "Split Bengal gram for dals, sundal, and snacks.", "140.00", "kg", "1 kg", True, "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a5/Chana_Dal_%28split_Bengal_gram%29.JPG/960px-Chana_Dal_%28split_Bengal_gram%29.JPG"),
    ("pulses-and-dals", "Kabuli Chana", "kabuli-chana-1kg", "White chickpeas for chole and salads.", "190.00", "kg", "1 kg", True, "https://images.unsplash.com/photo-1515543904379-3d757afe72e4?auto=format&fit=crop&w=800&q=80"),
    ("pulses-and-dals", "Rajma", "rajma-1kg", "Red kidney beans for rajma curry and hearty meals.", "175.00", "kg", "1 kg", True, "https://images.unsplash.com/photo-1551462147-ff29053bfc14?auto=format&fit=crop&w=800&q=80"),
    ("pulses-and-dals", "Green Gram Whole", "green-gram-whole-1kg", "Whole moong for sprouts, sundal, and curries.", "155.00", "kg", "1 kg", True, "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a1/Vigna.radiata.seeds.jpg/960px-Vigna.radiata.seeds.jpg"),

    # Spices & Masalas
    ("spices-and-masalas", "Turmeric Powder", "turmeric-powder-200g", "Ground turmeric for color and flavor in Indian cooking.", "58.00", "g", "200 g", True, "https://upload.wikimedia.org/wikipedia/commons/thumb/9/90/Kunyit_Bubuk.jpg/960px-Kunyit_Bubuk.jpg"),
    ("spices-and-masalas", "Red Chilli Powder", "red-chilli-powder-200g", "Vibrant chilli powder for heat and color.", "85.00", "g", "200 g", True, "https://upload.wikimedia.org/wikipedia/commons/0/00/BolivianChilePowder2.JPG"),
    ("spices-and-masalas", "Coriander Powder", "coriander-powder-200g", "Aromatic coriander powder for curries and gravies.", "65.00", "g", "200 g", True, "https://upload.wikimedia.org/wikipedia/commons/thumb/6/64/Coriander_powder.JPG/960px-Coriander_powder.JPG"),
    ("spices-and-masalas", "Cumin Seeds", "cumin-seeds-200g", "Whole jeera for tempering and spice blends.", "120.00", "g", "200 g", True, "https://upload.wikimedia.org/wikipedia/commons/thumb/6/61/Whole_Cumin_Seeds.jpg/960px-Whole_Cumin_Seeds.jpg"),
    ("spices-and-masalas", "Mustard Seeds", "mustard-seeds-200g", "Mustard seeds for South Indian tempering.", "48.00", "g", "200 g", True, "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b4/Mustard_black.JPG/960px-Mustard_black.JPG"),
    ("spices-and-masalas", "Black Pepper Whole", "black-pepper-whole-100g", "Whole black peppercorns for rasam and seasoning.", "110.00", "g", "100 g", True, "https://upload.wikimedia.org/wikipedia/commons/thumb/8/81/Tellicherry_Black_Peppercorns.jpg/960px-Tellicherry_Black_Peppercorns.jpg"),
    ("spices-and-masalas", "Sambar Powder", "sambar-powder-200g", "Spice blend for flavorful sambar.", "95.00", "g", "200 g", True, "https://upload.wikimedia.org/wikipedia/commons/thumb/3/32/Sambar_powder.jpg/960px-Sambar_powder.jpg"),
    ("spices-and-masalas", "Rasam Powder", "rasam-powder-200g", "Aromatic spice mix for peppery rasam.", "90.00", "g", "200 g", True, "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ea/Rasam_powder_picture.JPG/960px-Rasam_powder_picture.JPG"),
    ("spices-and-masalas", "Garam Masala", "garam-masala-100g", "Warm spice blend for North and fusion dishes.", "85.00", "g", "100 g", True, "https://upload.wikimedia.org/wikipedia/commons/thumb/5/58/Garammasalaphoto.jpg/960px-Garammasalaphoto.jpg"),

    # Vegetables
    ("vegetables", "Tomatoes", "tomatoes-1kg", "Fresh tomatoes for curries, sambar, and salads.", "40.00", "kg", "1 kg", True, "https://upload.wikimedia.org/wikipedia/commons/thumb/8/88/Bright_red_tomato_and_cross_section02.jpg/960px-Bright_red_tomato_and_cross_section02.jpg"),
    ("vegetables", "Onions", "onions-1kg", "Everyday cooking onions for gravies and tempering.", "35.00", "kg", "1 kg", True, "https://images.unsplash.com/photo-1618512496248-a07fe83aa8cb?auto=format&fit=crop&w=800&q=80"),
    ("vegetables", "Potatoes", "potatoes-1kg", "Versatile potatoes for curries, poriyal, and snacks.", "32.00", "kg", "1 kg", True, "https://images.unsplash.com/photo-1518977676601-b53f82aba655?auto=format&fit=crop&w=800&q=80"),
    ("vegetables", "Green Chillies", "green-chillies-250g", "Fresh green chillies for heat and flavor.", "20.00", "g", "250 g", True, "https://upload.wikimedia.org/wikipedia/commons/0/08/Green_chillies_from_Indian_farms.jpg"),
    ("vegetables", "Carrots", "carrots-500g", "Crunchy carrots for poriyal, salads, and sambar.", "30.00", "g", "500 g", True, "https://images.unsplash.com/photo-1598170845058-32b9d6a5da37?auto=format&fit=crop&w=800&q=80"),
    ("vegetables", "Drumsticks", "drumsticks-250g", "Drumsticks commonly used in sambar and curries.", "28.00", "g", "250 g", True, "https://upload.wikimedia.org/wikipedia/commons/thumb/8/81/Moringa_oleifera_drumstick_pods.JPG/960px-Moringa_oleifera_drumstick_pods.JPG"),
    ("vegetables", "Brinjal (Eggplant)", "brinjal-500g", "Fresh brinjal for poriyal, curry, and kathirikai dishes.", "38.00", "g", "500 g", True, "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1a/Eggplant_%28Solanum_melongena%29.JPG/960px-Eggplant_%28Solanum_melongena%29.JPG"),
    ("vegetables", "Curry Leaves", "curry-leaves-50g", "Aromatic curry leaves for tempering and flavor.", "15.00", "g", "50 g", True, "https://upload.wikimedia.org/wikipedia/commons/thumb/9/96/Fresh_curry_leaves.jpg/960px-Fresh_curry_leaves.jpg"),

    # Fruits
    ("fruits", "Bananas", "bananas-1-dozen", "Ripe bananas for snacking and breakfast.", "60.00", "dozen", "1 dozen", True, "https://images.unsplash.com/photo-1571771894821-ce9b6c11b08e?auto=format&fit=crop&w=800&q=80"),
    ("fruits", "Apples", "apples-1kg", "Crisp apples suitable for snacking and salads.", "180.00", "kg", "1 kg", True, "https://images.unsplash.com/photo-1560806887-1e4cd0b6cbd6?auto=format&fit=crop&w=800&q=80"),
    ("fruits", "Oranges", "oranges-1kg", "Juicy oranges rich in citrus flavor.", "140.00", "kg", "1 kg", True, "https://images.unsplash.com/photo-1547514701-42782101795e?auto=format&fit=crop&w=800&q=80"),
    ("fruits", "Pomegranates", "pomegranates-500g", "Fresh pomegranates for snacking and toppings.", "120.00", "g", "500 g", True, "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fa/Pomegranate_fruit_-_whole_and_piece_with_arils.jpg/960px-Pomegranate_fruit_-_whole_and_piece_with_arils.jpg"),
    ("fruits", "Papaya", "papaya-1kg", "Ripe papaya for breakfast bowls and fruit plates.", "55.00", "kg", "1 kg", True, "https://images.unsplash.com/photo-1517282009859-f000ec3b26fe?auto=format&fit=crop&w=800&q=80"),

    # Dairy & Eggs
    ("dairy-and-eggs", "Toned Milk", "toned-milk-1l", "Toned milk for tea, coffee, and daily use.", "58.00", "L", "1 L", True, "https://images.unsplash.com/photo-1563636619-e9143da7973b?auto=format&fit=crop&w=800&q=80"),
    ("dairy-and-eggs", "Curd", "curd-400g", "Fresh curd for meals, raita, and curd rice.", "45.00", "g", "400 g", True, "https://images.unsplash.com/photo-1488477181946-6428a0291777?auto=format&fit=crop&w=800&q=80"),
    ("dairy-and-eggs", "Paneer", "paneer-200g", "Fresh paneer for curries and snacks.", "95.00", "g", "200 g", True, "https://images.unsplash.com/photo-1631452180519-c014fe946bc7?auto=format&fit=crop&w=800&q=80"),
    ("dairy-and-eggs", "Unsalted Butter", "unsalted-butter-100g", "Butter for cooking, baking, and spreads.", "62.00", "g", "100 g", True, "https://images.unsplash.com/photo-1589985270826-4b7bb135bc9d?auto=format&fit=crop&w=800&q=80"),
    ("dairy-and-eggs", "Eggs", "eggs-12-pack", "Farm eggs pack for everyday cooking and baking.", "78.00", "pack", "12 pcs", True, "https://images.unsplash.com/photo-1582722872445-44dc5f7e3c8f?auto=format&fit=crop&w=800&q=80"),

    # Cooking Essentials
    ("cooking-essentials", "Sunflower Oil", "sunflower-oil-1l", "Refined sunflower oil for everyday cooking.", "165.00", "L", "1 L", True, "https://upload.wikimedia.org/wikipedia/commons/thumb/3/33/Bottle_1_liter_Sunflower_refined_oil.jpg/960px-Bottle_1_liter_Sunflower_refined_oil.jpg"),
    ("cooking-essentials", "Groundnut Oil", "groundnut-oil-1l", "Groundnut oil commonly used in South Indian kitchens.", "210.00", "L", "1 L", True, "https://upload.wikimedia.org/wikipedia/commons/thumb/2/27/Groundnut_oil.jpg/960px-Groundnut_oil.jpg"),
    ("cooking-essentials", "Gingelly (Sesame) Oil", "gingelly-oil-500ml", "Sesame oil for traditional cooking and pickles.", "195.00", "ml", "500 ml", True, "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fb/Sesame-oil.jpg/960px-Sesame-oil.jpg"),
    ("cooking-essentials", "Iodized Salt", "iodized-salt-1kg", "Iodized table salt for everyday seasoning.", "28.00", "kg", "1 kg", True, "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d8/EdibleSalt.jpg/960px-EdibleSalt.jpg"),
    ("cooking-essentials", "Sugar", "sugar-1kg", "Refined sugar for beverages and cooking.", "48.00", "kg", "1 kg", True, "https://upload.wikimedia.org/wikipedia/commons/8/84/White-Sugar-Crystals_61460-480x360_%284905066920%29.jpg"),
    ("cooking-essentials", "Tea Powder", "tea-powder-250g", "Black tea powder for daily chai.", "135.00", "g", "250 g", True, "https://images.unsplash.com/photo-1597318181409-cf64d0b5d8a2?auto=format&fit=crop&w=800&q=80"),
    ("cooking-essentials", "Filter Coffee Powder", "filter-coffee-powder-200g", "South Indian filter coffee blend.", "160.00", "g", "200 g", True, "https://images.unsplash.com/photo-1559056199-641a0ac8b55e?auto=format&fit=crop&w=800&q=80"),
]


def main() -> int:
    if SessionLocal is None:
        print("ERROR: DATABASE_URL is not configured. Set backend/.env and retry.")
        return 1

    db = SessionLocal()
    cats_inserted = cats_existing = 0
    prods_inserted = prods_existing = 0
    try:
        # Seed categories by slug
        slug_to_category: dict[str, ProductCategory] = {}
        for c in CATEGORIES:
            existing = db.execute(
                select(ProductCategory).where(ProductCategory.slug == c["slug"])
            ).scalar_one_or_none()
            if existing:
                cats_existing += 1
                slug_to_category[c["slug"]] = existing
            else:
                obj = ProductCategory(name=c["name"], slug=c["slug"], description=c.get("description"))
                db.add(obj)
                db.flush()  # get id
                cats_inserted += 1
                slug_to_category[c["slug"]] = obj

        # Seed products by slug
        for p in PRODUCTS:
            cat_slug, name, slug, desc, price, unit, size, available, image_url = p
            existing = db.execute(select(Product).where(Product.slug == slug)).scalar_one_or_none()
            if existing:
                prods_existing += 1
                continue
            category = slug_to_category.get(cat_slug)
            if not category:
                # Should not happen; skip safely without fabricating
                print(f"WARNING: Missing category for product slug {slug} ({cat_slug}); skipping.")
                continue
            obj = Product(
                category_id=category.id,
                name=name,
                slug=slug,
                description=desc,
                price=Decimal(price),
                unit=unit,
                size=size,
                image_url=image_url,
                is_available=available,
            )
            db.add(obj)
            prods_inserted += 1

        db.commit()

        total_cats = db.execute(select(ProductCategory)).scalars().all()
        total_prods = db.execute(select(Product)).scalars().all()
        available_prods = [x for x in total_prods if x.is_available]
        print("SEED_SUMMARY")
        print(f"categories_inserted={cats_inserted}")
        print(f"categories_already_present={cats_existing}")
        print(f"products_inserted={prods_inserted}")
        print(f"products_already_present={prods_existing}")
        print(f"total_categories={len(total_cats)}")
        print(f"total_products={len(total_prods)}")
        print(f"total_available_products={len(available_prods)}")
        return 0
    except Exception as e:
        db.rollback()
        print(f"ERROR: {type(e).__name__}: {e}")
        return 1
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
