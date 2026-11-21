"""Idempotent seed script for the CookKart recipe catalogue (Phase 5).

Usage (from backend/):
  .\\.venv\\Scripts\\python.exe seed_recipe_catalogue.py

Inserts the approved 25-recipe catalogue if it is missing. Safe to run repeatedly:
existing collections, ingredients, recipes, recipe ingredients and product mappings
are counted as already present and are never overwritten or deleted.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from decimal import Decimal

from sqlalchemy import func, select

from app.database.session import SessionLocal
from app.models.catalog import Product
from app.models.mapping import ProductIngredientMapping
from app.models.recipe import Ingredient, Recipe, RecipeCollection, RecipeIngredient

COLLECTIONS = [
    {
        "name": "South Indian",
        "slug": "south-indian",
        "cuisine_label": "South Indian",
        "description": "Idlis, dosas, tempered rice and comforting lentil dishes from southern India.",
    },
    {
        "name": "North Indian",
        "slug": "north-indian",
        "cuisine_label": "North Indian",
        "description": "Hearty parathas, rich curries and crisp snacks from northern India.",
    },
    {
        "name": "Chinese",
        "slug": "chinese",
        "cuisine_label": "Indo-Chinese",
        "description": "Stir-fries, dumplings and crunchy snacks inspired by Chinese home cooking.",
    },
    {
        "name": "Italian",
        "slug": "italian",
        "cuisine_label": "Italian",
        "description": "Simple Italian favourites: frittatas, bruschetta, pasta, pizza and garlic bread.",
    },
    {
        "name": "Quick Meals",
        "slug": "quick-meals",
        "cuisine_label": "Everyday favourites",
        "description": "Everyday dishes that come together quickly with familiar pantry ingredients.",
    },
]

# Canonical ingredient name -> existing shop product slug. None means the ingredient
# is not sold in the current catalogue and must not be presented as purchasable.
INGREDIENT_PRODUCTS: dict[str, str | None] = {
    "Idli Rice": "idli-rice-5kg",
    "Dosa Rice": "dosa-rice-5kg",
    "Urad Dal": "urad-dal-whole-1kg",
    "Sona Masoori Rice": "sona-masoori-rice-5kg",
    "Basmati Rice": "basmati-rice-5kg",
    "Toor Dal": "toor-dal-1kg",
    "Poha (Flattened Rice)": "poha-medium-1kg",
    "Whole Wheat Flour": "whole-wheat-atta-5kg",
    "Tamarind": "tamarind-block-500g",
    "Sambar Powder": "sambar-powder-200g",
    "Turmeric Powder": "turmeric-powder-200g",
    "Red Chilli Powder": "red-chilli-powder-200g",
    "Coriander Powder": "coriander-powder-200g",
    "Cumin Seeds": "cumin-seeds-200g",
    "Mustard Seeds": "mustard-seeds-200g",
    "Curry Leaves": "curry-leaves-50g",
    "Garam Masala": "garam-masala-100g",
    "Black Pepper": "black-pepper-whole-100g",
    "Salt": "iodized-salt-1kg",
    "Sunflower Oil": "sunflower-oil-1l",
    "Sesame Oil": "gingelly-oil-500ml",
    "Butter": "unsalted-butter-100g",
    "Milk": "toned-milk-1l",
    "Curd": "curd-400g",
    "Paneer": "paneer-200g",
    "Eggs": "eggs-12-pack",
    "Chickpeas": "kabuli-chana-1kg",
    "Tomatoes": "tomatoes-1kg",
    "Onions": "onions-1kg",
    "Potatoes": "potatoes-1kg",
    "Carrot": "carrots-500g",
    "Drumstick": "drumsticks-250g",
    "Green Chillies": "green-chillies-250g",
    "Coriander Leaves": None,
    "Fenugreek Seeds": None,
    "Asafoetida": None,
    "Ginger": None,
    "Garlic": None,
    "Peanuts": None,
    "Cashew Nuts": None,
    "Cream": None,
    "Kasuri Methi": None,
    "Lemon": None,
    "Gram Flour": None,
    "All-Purpose Flour": None,
    "Spring Roll Wrappers": None,
    "Hakka Noodles": None,
    "Cabbage": None,
    "Capsicum": None,
    "Spring Onions": None,
    "Soy Sauce": None,
    "Chilli Sauce": None,
    "Cornflour": None,
    "Spinach": None,
    "Button Mushrooms": None,
    "Olive Oil": None,
    "Mozzarella Cheese": None,
    "Baguette": None,
    "Dried Basil": None,
    "Penne Pasta": None,
    "Tomato Puree": None,
    "Dried Oregano": None,
    "Pizza Base": None,
    "Bread Slices": None,
    "Cucumber": None,
    "Green Peas": None,
    "Chaat Masala": None,
    "Sweet Corn": None,
}


@dataclass(frozen=True)
class RecipeSpec:
    collection: str
    name: str
    slug: str
    description: str
    meal_type: str
    prep: int
    cook: int
    difficulty: str
    servings: int
    image_url: str
    video_id: str
    ingredients: tuple[tuple[str, str | None, str | None], ...]
    instructions: tuple[str, ...]


def _img(path: str) -> str:
    """Build an external Wikimedia Commons thumbnail URL."""
    return f"https://upload.wikimedia.org/wikipedia/commons/thumb/{path}/960px-{path.split('/')[-1]}"


RECIPES = [
    # ------------------------------- South Indian ------------------------------
    RecipeSpec(
        "south-indian", "Idli", "idli",
        "Soft, fermented rice and urad dumplings steamed until fluffy. A staple South Indian breakfast served with sambar and chutney.",
        "breakfast-tiffin", 25, 15, "Easy", 4,
        _img("8/89/Idli.jpg"), "Ayo80PIb-Qg",
        (
            ("Idli Rice", "2", "cups"),
            ("Urad Dal", "1", "cup"),
            ("Fenugreek Seeds", "0.5", "tsp"),
            ("Salt", None, "to taste"),
        ),
        (
            "Rinse the idli rice and urad dal separately until the water runs clear.",
            "Soak the rice, urad dal and fenugreek seeds together in plenty of water for 6 to 8 hours.",
            "Drain and grind to a smooth, slightly aerated batter, adding water a little at a time.",
            "Stir in salt, cover and ferment in a warm place for 8 to 12 hours until the batter rises.",
            "Grease an idli tray, pour in the batter and steam for 10 to 15 minutes.",
            "Serve warm with sambar and chutney.",
        ),
    ),
    RecipeSpec(
        "south-indian", "Masala Dosa", "masala-dosa",
        "A crisp fermented dosa filled with a spiced potato masala, cooked with mustard seeds and curry leaves.",
        "breakfast-tiffin", 30, 25, "Medium", 4,
        _img("4/43/Masala_dosa_01.jpg"), "PFG1aeYgi7c",
        (
            ("Dosa Rice", "2", "cups"),
            ("Urad Dal", "1", "cup"),
            ("Fenugreek Seeds", "0.5", "tsp"),
            ("Potatoes", "3", "pcs"),
            ("Onions", "1", "pcs"),
            ("Mustard Seeds", "1", "tsp"),
            ("Curry Leaves", "8", "leaves"),
            ("Turmeric Powder", "0.25", "tsp"),
            ("Green Chillies", "2", "pcs"),
            ("Sunflower Oil", "3", "tbsp"),
            ("Salt", None, "to taste"),
        ),
        (
            "Soak the dosa rice, urad dal and fenugreek seeds for 6 to 8 hours, then grind to a smooth batter.",
            "Add salt, cover and ferment for 8 to 12 hours until noticeably risen.",
            "Boil the potatoes, peel and lightly crush them.",
            "Heat oil, splutter mustard seeds, then add curry leaves, sliced onions and green chillies.",
            "Add turmeric and crushed potatoes, mix well and season with salt. Set the masala aside.",
            "Pour a thin layer of batter onto a hot greased tawa and spread into a round dosa.",
            "Spoon the potato masala into the centre, fold and serve hot with chutney and sambar.",
        ),
    ),
    RecipeSpec(
        "south-indian", "Sambar", "sambar",
        "A tangy lentil and vegetable stew flavoured with tamarind, sambar powder and a classic tempering.",
        "lunch-dinner", 20, 35, "Easy", 6,
        _img("3/34/Vegetable_ready_for_Sambar_in_Kerala_4888.JPG"), "zOJEc_3_Ng8",
        (
            ("Toor Dal", "1", "cup"),
            ("Tamarind", "50", "g"),
            ("Sambar Powder", "2", "tbsp"),
            ("Tomatoes", "2", "pcs"),
            ("Onions", "1", "pcs"),
            ("Carrot", "2", "pcs"),
            ("Drumstick", "200", "g"),
            ("Curry Leaves", "8", "leaves"),
            ("Mustard Seeds", "1", "tsp"),
            ("Asafoetida", "0.25", "tsp"),
            ("Turmeric Powder", "0.5", "tsp"),
            ("Sunflower Oil", "2", "tbsp"),
            ("Coriander Leaves", "2", "tbsp"),
            ("Salt", None, "to taste"),
        ),
        (
            "Cook the toor dal with turmeric and salt until soft, then mash lightly.",
            "Soak the tamarind in warm water and extract a thick pulp.",
            "Heat oil and temper mustard seeds, asafoetida and curry leaves.",
            "Add sliced onions, tomatoes, carrot and drumstick, and saute for a few minutes.",
            "Stir in sambar powder and the tamarind extract, then add water as needed.",
            "Simmer until the vegetables are tender, add the cooked dal and mix well.",
            "Adjust salt, garnish with coriander leaves and serve with rice or idli.",
        ),
    ),
    RecipeSpec(
        "south-indian", "Lemon Rice", "lemon-rice",
        "Tempered rice tossed with lemon juice, peanuts and curry leaves. A bright, quick lunch box favourite.",
        "lunch-dinner", 15, 20, "Easy", 4,
        _img("b/bb/Lemon_Rice_in_Kerala.jpg"), "dTBg3O_s9LM",
        (
            ("Sona Masoori Rice", "2", "cups"),
            ("Lemon", "2", "pcs"),
            ("Peanuts", "50", "g"),
            ("Mustard Seeds", "1", "tsp"),
            ("Curry Leaves", "8", "leaves"),
            ("Turmeric Powder", "0.5", "tsp"),
            ("Green Chillies", "2", "pcs"),
            ("Sunflower Oil", "2", "tbsp"),
            ("Salt", None, "to taste"),
        ),
        (
            "Cook the rice until the grains are separate and let it cool slightly.",
            "Heat oil in a pan and fry the peanuts until golden. Remove and set aside.",
            "In the same oil, splutter mustard seeds and add curry leaves and sliced green chillies.",
            "Stir in turmeric and the juice of the lemons.",
            "Add the rice, peanuts and salt, then toss gently until evenly coated.",
            "Serve warm or at room temperature.",
        ),
    ),
    RecipeSpec(
        "south-indian", "Medu Vada", "medu-vada",
        "Crisp, savoury urad dal fritters with a soft centre, flavoured with ginger, green chilli and curry leaves.",
        "snack", 20, 25, "Medium", 4,
        _img("d/db/Uzhunnu_vada.jpg"), "b4c-QzvSMx8",
        (
            ("Urad Dal", "1.5", "cups"),
            ("Green Chillies", "2", "pcs"),
            ("Ginger", "20", "g"),
            ("Curry Leaves", "8", "leaves"),
            ("Sunflower Oil", "500", "ml"),
            ("Salt", None, "to taste"),
        ),
        (
            "Soak the urad dal for 4 to 6 hours, then drain well.",
            "Grind the dal to a thick, fluffy batter using very little water.",
            "Add finely chopped green chillies, ginger, curry leaves and salt.",
            "Beat the batter briefly to incorporate air.",
            "Heat oil in a deep pan. Shape the batter into rings on a greased surface and slide into the oil.",
            "Fry until deep golden and crisp, then drain and serve with chutney or sambar.",
        ),
    ),

    # -------------------------------- North Indian ----------------------------
    RecipeSpec(
        "north-indian", "Aloo Paratha", "aloo-paratha",
        "Whole wheat flatbreads stuffed with a spiced potato filling and cooked with a little butter.",
        "breakfast-tiffin", 20, 25, "Medium", 4,
        _img("9/92/Aloo_Paratha_with_Sabzi.jpg"), "jLmYDZ2zjSg",
        (
            ("Whole Wheat Flour", "2", "cups"),
            ("Potatoes", "3", "pcs"),
            ("Green Chillies", "2", "pcs"),
            ("Coriander Leaves", "2", "tbsp"),
            ("Cumin Seeds", "1", "tsp"),
            ("Butter", "20", "g"),
            ("Salt", None, "to taste"),
        ),
        (
            "Knead the whole wheat flour with water and a pinch of salt into a soft dough. Rest for 15 minutes.",
            "Boil, peel and mash the potatoes.",
            "Mix the potatoes with chopped green chillies, coriander leaves, cumin seeds and salt.",
            "Divide the dough and filling into equal portions.",
            "Stuff each dough ball with the potato mixture, seal and roll gently into a paratha.",
            "Cook on a hot tawa, flipping until both sides are golden, then brush with butter.",
            "Serve hot with curd or a vegetable side dish.",
        ),
    ),
    RecipeSpec(
        "north-indian", "Vegetable Poha", "vegetable-poha",
        "Light flattened rice cooked with onions, peanuts and turmeric. A quick, wholesome Indian breakfast.",
        "breakfast-tiffin", 10, 12, "Easy", 3,
        _img("f/f4/Poha%2C_a_snack_made_of_flattened_rice.jpg"), "yWkF-2aBDZE",
        (
            ("Poha (Flattened Rice)", "2", "cups"),
            ("Onions", "1", "pcs"),
            ("Peanuts", "50", "g"),
            ("Mustard Seeds", "1", "tsp"),
            ("Curry Leaves", "8", "leaves"),
            ("Turmeric Powder", "0.5", "tsp"),
            ("Green Chillies", "2", "pcs"),
            ("Lemon", "1", "pcs"),
            ("Sunflower Oil", "2", "tbsp"),
            ("Salt", None, "to taste"),
        ),
        (
            "Rinse the poha gently in a sieve and let it drain for a few minutes.",
            "Heat oil and fry the peanuts until crisp. Remove and set aside.",
            "Splutter mustard seeds in the same pan, then add curry leaves, onions and green chillies.",
            "Saute until soft and stir in the turmeric.",
            "Add the drained poha and salt, mixing gently so the grains stay separate.",
            "Cover and cook for 3 to 4 minutes, then finish with lemon juice and peanuts.",
        ),
    ),
    RecipeSpec(
        "north-indian", "Paneer Butter Masala", "paneer-butter-masala",
        "Soft paneer cubes in a silky tomato and cashew gravy enriched with butter, cream and warm spices.",
        "lunch-dinner", 20, 30, "Medium", 4,
        _img("1/19/Paneer_butter_masala_2.jpg"), "U1LVDFwi8qI",
        (
            ("Paneer", "400", "g"),
            ("Butter", "50", "g"),
            ("Tomatoes", "4", "pcs"),
            ("Onions", "1", "pcs"),
            ("Cashew Nuts", "30", "g"),
            ("Cream", "100", "ml"),
            ("Ginger", "20", "g"),
            ("Garlic", "4", "cloves"),
            ("Garam Masala", "1", "tsp"),
            ("Red Chilli Powder", "1", "tsp"),
            ("Turmeric Powder", "0.25", "tsp"),
            ("Kasuri Methi", "1", "tsp"),
            ("Coriander Powder", "1", "tsp"),
            ("Sunflower Oil", "1", "tbsp"),
            ("Coriander Leaves", "2", "tbsp"),
            ("Salt", None, "to taste"),
        ),
        (
            "Soak the cashew nuts in warm water for 10 minutes.",
            "Cook chopped tomatoes, onion, ginger and garlic in a little oil until soft.",
            "Cool, blend with the cashews and strain for a smooth gravy base.",
            "Return the gravy to the pan and add turmeric, coriander powder and red chilli powder.",
            "Simmer with butter and salt until the sauce thickens and releases oil at the edges.",
            "Add the paneer cubes and cream, then cook gently for 5 minutes.",
            "Finish with garam masala and crushed kasuri methi. Garnish with coriander leaves.",
        ),
    ),
    RecipeSpec(
        "north-indian", "Chole", "chole",
        "Punjabi-style chickpeas simmered with onions, tomatoes and a robust blend of ground spices.",
        "lunch-dinner", 25, 45, "Medium", 5,
        _img("6/6a/Bikaner_chole_bhature.jpg"), "RXZsDHKlVGw",
        (
            ("Chickpeas", "2", "cups"),
            ("Onions", "2", "pcs"),
            ("Tomatoes", "3", "pcs"),
            ("Ginger", "20", "g"),
            ("Garlic", "4", "cloves"),
            ("Garam Masala", "1.5", "tsp"),
            ("Coriander Powder", "2", "tsp"),
            ("Cumin Seeds", "1", "tsp"),
            ("Red Chilli Powder", "1", "tsp"),
            ("Turmeric Powder", "0.5", "tsp"),
            ("Sunflower Oil", "3", "tbsp"),
            ("Coriander Leaves", "2", "tbsp"),
            ("Salt", None, "to taste"),
        ),
        (
            "Soak the chickpeas overnight, then pressure cook until tender.",
            "Heat oil and add cumin seeds, then finely chopped onions.",
            "Cook the onions until golden and add ginger, garlic and chopped tomatoes.",
            "Stir in turmeric, coriander powder and red chilli powder; cook until the oil separates.",
            "Add the chickpeas with a little of their cooking liquid and simmer for 15 minutes.",
            "Season with salt and garam masala, and mash a few chickpeas to thicken the gravy.",
            "Garnish with coriander leaves and serve with rice or flatbread.",
        ),
    ),
    RecipeSpec(
        "north-indian", "Onion Pakora", "onion-pakora",
        "Crisp onion fritters bound with gram flour and spiced with chilli and curry leaves.",
        "snack", 15, 20, "Easy", 4,
        _img("0/06/Onion_pakora.jpg"), "qfZ3axZV48A",
        (
            ("Gram Flour", "1.5", "cups"),
            ("Onions", "3", "pcs"),
            ("Green Chillies", "2", "pcs"),
            ("Curry Leaves", "8", "leaves"),
            ("Red Chilli Powder", "1", "tsp"),
            ("Sunflower Oil", "500", "ml"),
            ("Salt", None, "to taste"),
        ),
        (
            "Thinly slice the onions and chop the green chillies and curry leaves.",
            "Mix the onions with gram flour, red chilli powder and salt.",
            "Add water a spoonful at a time to form a thick, sticky mixture.",
            "Heat oil in a deep pan until hot but not smoking.",
            "Drop small clusters of the mixture into the oil and fry until golden and crisp.",
            "Drain well and serve hot with chutney or a cup of tea.",
        ),
    ),

    # --------------------------------- Chinese --------------------------------
    RecipeSpec(
        "chinese", "Vegetable Momos", "vegetable-momos",
        "Steamed dumplings with a finely chopped vegetable filling and a light soy seasoning.",
        "breakfast-tiffin", 30, 20, "Medium", 4,
        _img("a/a1/Vegetable_Momo_-_Howrah_2013-10-10_3255.JPG"), "kfvXn1RMRpY",
        (
            ("All-Purpose Flour", "2", "cups"),
            ("Cabbage", "200", "g"),
            ("Carrot", "1", "pcs"),
            ("Spring Onions", "4", "pcs"),
            ("Ginger", "20", "g"),
            ("Garlic", "3", "cloves"),
            ("Soy Sauce", "2", "tbsp"),
            ("Sunflower Oil", "1", "tbsp"),
            ("Salt", None, "to taste"),
        ),
        (
            "Knead the flour with warm water and a pinch of salt into a firm dough. Cover and rest for 20 minutes.",
            "Finely chop the cabbage, carrot, spring onions, ginger and garlic.",
            "Heat oil and stir-fry the vegetables for 2 to 3 minutes.",
            "Add soy sauce and salt, then cook until the moisture evaporates. Cool the filling.",
            "Divide the dough into small balls and roll each into a thin round wrapper.",
            "Place a spoonful of filling in the centre, pleat the edges and seal into a dumpling.",
            "Steam for 10 to 12 minutes and serve with chutney or chilli sauce.",
        ),
    ),
    RecipeSpec(
        "chinese", "Scallion Pancakes", "scallion-pancakes",
        "Flaky pan-fried flatbreads layered with spring onions and sesame oil.",
        "breakfast-tiffin", 25, 20, "Medium", 4,
        _img("1/1d/Scallion_pancake_%284354349219%29.jpg"), "qsRD4QWDtOU",
        (
            ("All-Purpose Flour", "2", "cups"),
            ("Spring Onions", "6", "pcs"),
            ("Sesame Oil", "2", "tbsp"),
            ("Sunflower Oil", "3", "tbsp"),
            ("Salt", None, "to taste"),
        ),
        (
            "Mix the flour with warm water and salt to make a smooth dough. Rest for 20 minutes.",
            "Roll the dough into a thin sheet and brush lightly with sesame oil.",
            "Sprinkle generously with chopped spring onions.",
            "Roll the sheet into a log, then coil the log into a spiral and flatten gently.",
            "Roll the spiral into a round pancake.",
            "Pan-fry in a little sunflower oil until both sides are crisp and golden.",
            "Slice into wedges and serve hot.",
        ),
    ),
    RecipeSpec(
        "chinese", "Vegetable Hakka Noodles", "vegetable-hakka-noodles",
        "Wok-tossed noodles with crunchy vegetables, garlic, ginger and soy sauce.",
        "lunch-dinner", 15, 15, "Easy", 4,
        _img("1/13/Hakka_Noodles.JPG"), "bdNuZfnDLRs",
        (
            ("Hakka Noodles", "200", "g"),
            ("Cabbage", "200", "g"),
            ("Carrot", "1", "pcs"),
            ("Capsicum", "1", "pcs"),
            ("Spring Onions", "4", "pcs"),
            ("Garlic", "3", "cloves"),
            ("Ginger", "20", "g"),
            ("Soy Sauce", "3", "tbsp"),
            ("Chilli Sauce", "1", "tbsp"),
            ("Sunflower Oil", "3", "tbsp"),
            ("Salt", None, "to taste"),
        ),
        (
            "Boil the noodles until just tender, drain and toss with a little oil.",
            "Shred the cabbage and slice the carrot and capsicum into thin strips.",
            "Heat oil in a hot pan or wok and stir-fry garlic and ginger for a few seconds.",
            "Add the vegetables and toss on high heat until they stay crisp.",
            "Add the noodles, soy sauce, chilli sauce and salt.",
            "Toss quickly until evenly coated, then finish with chopped spring onions.",
        ),
    ),
    RecipeSpec(
        "chinese", "Chilli Paneer", "chilli-paneer",
        "Paneer tossed in a glossy, spicy Indo-Chinese sauce with peppers and spring onions.",
        "lunch-dinner", 20, 20, "Medium", 4,
        _img("9/96/A_full_plate_chilli_paneer_in_Kolkata%2C_West_Bengal.jpg"), "fPyHXiHbLg4",
        (
            ("Paneer", "400", "g"),
            ("Capsicum", "2", "pcs"),
            ("Onions", "1", "pcs"),
            ("Garlic", "4", "cloves"),
            ("Ginger", "20", "g"),
            ("Soy Sauce", "3", "tbsp"),
            ("Chilli Sauce", "2", "tbsp"),
            ("Cornflour", "2", "tbsp"),
            ("Red Chilli Powder", "1", "tsp"),
            ("Sunflower Oil", "3", "tbsp"),
            ("Salt", None, "to taste"),
        ),
        (
            "Cut the paneer into cubes and coat lightly with cornflour.",
            "Shallow fry the paneer until the edges are golden, then set aside.",
            "Heat oil in a wok and stir-fry chopped garlic and ginger briefly.",
            "Add sliced onions and capsicum and toss on high heat for 2 minutes.",
            "Mix soy sauce, chilli sauce, red chilli powder and a splash of water.",
            "Pour the sauce into the wok and cook until it thickens slightly.",
            "Return the paneer, toss to coat and season with salt. Serve hot.",
        ),
    ),
    RecipeSpec(
        "chinese", "Vegetable Spring Rolls", "vegetable-spring-rolls",
        "Crisp rolls filled with seasoned cabbage, carrot and spring onions.",
        "snack", 25, 20, "Medium", 4,
        _img("c/c1/Spring_roll_001.jpg"), "wNB05Zc4TqA",
        (
            ("Spring Roll Wrappers", "8", "pcs"),
            ("Cabbage", "200", "g"),
            ("Carrot", "1", "pcs"),
            ("Spring Onions", "4", "pcs"),
            ("Garlic", "3", "cloves"),
            ("Soy Sauce", "2", "tbsp"),
            ("Cornflour", "2", "tbsp"),
            ("Sunflower Oil", "500", "ml"),
            ("Salt", None, "to taste"),
        ),
        (
            "Finely shred the cabbage and carrot and slice the spring onions.",
            "Stir-fry the garlic and vegetables over high heat until just softened.",
            "Add soy sauce and salt, then cook until the filling is dry. Let it cool.",
            "Mix cornflour with a little water to make a thin paste.",
            "Place filling on each wrapper, fold in the sides and roll tightly, sealing with the paste.",
            "Deep-fry in hot oil until golden and crisp.",
            "Drain well and serve with chilli sauce.",
        ),
    ),

    # --------------------------------- Italian --------------------------------
    RecipeSpec(
        "italian", "Spinach & Mushroom Frittata", "spinach-mushroom-frittata",
        "A baked egg frittata with spinach, mushrooms and melted cheese.",
        "breakfast-tiffin", 15, 25, "Easy", 4,
        _img("7/77/Frittata02.jpg"), "CsDhqWSyPYg",
        (
            ("Eggs", "6", "pcs"),
            ("Spinach", "150", "g"),
            ("Button Mushrooms", "150", "g"),
            ("Onions", "1", "pcs"),
            ("Milk", "100", "ml"),
            ("Mozzarella Cheese", "80", "g"),
            ("Olive Oil", "2", "tbsp"),
            ("Black Pepper", "1", "tsp"),
            ("Salt", None, "to taste"),
        ),
        (
            "Whisk the eggs with milk, salt and black pepper.",
            "Heat olive oil in an oven-safe pan and soften the sliced onion.",
            "Add sliced mushrooms and cook until they release their moisture.",
            "Stir in the spinach and cook until just wilted.",
            "Pour in the egg mixture and sprinkle with grated mozzarella.",
            "Cook on low until the base is set, then finish under a hot grill until golden.",
            "Rest for a few minutes before slicing.",
        ),
    ),
    RecipeSpec(
        "italian", "Tomato Basil Bruschetta", "tomato-basil-bruschetta",
        "Toasted bread topped with ripe tomatoes, garlic, basil and olive oil.",
        "breakfast-tiffin", 15, 5, "Easy", 4,
        _img("8/8d/Bruschetta.jpg"), "URNuYVx0Cmo",
        (
            ("Baguette", "1", "pcs"),
            ("Tomatoes", "3", "pcs"),
            ("Garlic", "3", "cloves"),
            ("Olive Oil", "2", "tbsp"),
            ("Dried Basil", "1", "tsp"),
            ("Black Pepper", "0.5", "tsp"),
            ("Salt", None, "to taste"),
        ),
        (
            "Chop the tomatoes and mix with salt, dried basil and black pepper.",
            "Slice the baguette and toast the pieces until lightly golden.",
            "Rub each slice with a cut garlic clove.",
            "Spoon the tomato mixture over the toast.",
            "Drizzle with olive oil and serve immediately.",
        ),
    ),
    RecipeSpec(
        "italian", "Creamy Tomato Pasta", "creamy-tomato-pasta",
        "Penne in a smooth tomato and cream sauce with garlic, oregano and cheese.",
        "lunch-dinner", 10, 20, "Easy", 4,
        _img("0/03/Homemade_Tomato_sauce_pasta_2.jpg"), "12ieDk-uTkw",
        (
            ("Penne Pasta", "250", "g"),
            ("Tomato Puree", "300", "g"),
            ("Cream", "150", "ml"),
            ("Garlic", "4", "cloves"),
            ("Onions", "1", "pcs"),
            ("Olive Oil", "2", "tbsp"),
            ("Dried Oregano", "1", "tsp"),
            ("Mozzarella Cheese", "50", "g"),
            ("Black Pepper", "0.5", "tsp"),
            ("Salt", None, "to taste"),
        ),
        (
            "Cook the penne in salted water until al dente. Reserve a little pasta water.",
            "Heat olive oil and soften the chopped onion and garlic.",
            "Add tomato puree, oregano and salt, then simmer for 10 minutes.",
            "Stir in the cream and cook gently until the sauce is smooth.",
            "Add the pasta and toss, loosening with reserved pasta water if needed.",
            "Finish with grated mozzarella and black pepper, then serve hot.",
        ),
    ),
    RecipeSpec(
        "italian", "Margherita Pizza", "margherita-pizza",
        "A classic pizza with tomato sauce, mozzarella, basil and olive oil.",
        "lunch-dinner", 15, 20, "Easy", 2,
        _img("d/de/Margherita_pizza_on_plate.jpg"), "xKDnD8sJsuY",
        (
            ("Pizza Base", "2", "pcs"),
            ("Tomato Puree", "200", "g"),
            ("Mozzarella Cheese", "200", "g"),
            ("Dried Oregano", "1", "tsp"),
            ("Dried Basil", "1", "tsp"),
            ("Olive Oil", "2", "tbsp"),
            ("Salt", None, "to taste"),
        ),
        (
            "Heat the oven to its highest setting with a tray inside.",
            "Season the tomato puree with a little salt and spread it over each pizza base.",
            "Top evenly with grated mozzarella.",
            "Sprinkle with dried oregano and dried basil, then drizzle with olive oil.",
            "Bake on the hot tray until the crust is golden and the cheese is bubbling.",
            "Slice and serve hot.",
        ),
    ),
    RecipeSpec(
        "italian", "Garlic Bread", "garlic-bread",
        "Warm bread brushed with garlic butter and oregano, toasted until golden.",
        "snack", 10, 10, "Easy", 4,
        _img("e/ee/Garlic_bread_-_on_plate%2C_ready_to_eat.jpg"), "H8MOTK9ztEc",
        (
            ("Baguette", "1", "pcs"),
            ("Butter", "50", "g"),
            ("Garlic", "4", "cloves"),
            ("Dried Oregano", "1", "tsp"),
            ("Salt", None, "to taste"),
        ),
        (
            "Soften the butter and mix it with finely chopped garlic, oregano and salt.",
            "Slice the baguette without cutting all the way through the base.",
            "Spread the garlic butter generously between the slices.",
            "Wrap in foil and warm in a hot oven for 8 minutes.",
            "Unwrap and toast briefly until the edges are crisp. Serve warm.",
        ),
    ),

    # ------------------------------- Quick Meals ------------------------------
    RecipeSpec(
        "quick-meals", "Masala Omelette", "masala-omelette",
        "A fluffy egg omelette packed with onions, tomatoes, green chilli and herbs.",
        "breakfast-tiffin", 10, 10, "Easy", 2,
        _img("6/62/Masala_Egg_Omelette.jpeg"), "Mle9Vks2u84",
        (
            ("Eggs", "4", "pcs"),
            ("Onions", "1", "pcs"),
            ("Tomatoes", "1", "pcs"),
            ("Green Chillies", "2", "pcs"),
            ("Coriander Leaves", "2", "tbsp"),
            ("Turmeric Powder", "0.25", "tsp"),
            ("Black Pepper", "0.5", "tsp"),
            ("Sunflower Oil", "2", "tbsp"),
            ("Salt", None, "to taste"),
        ),
        (
            "Finely chop the onion, tomato, green chillies and coriander leaves.",
            "Whisk the eggs with turmeric, black pepper and salt.",
            "Stir the chopped vegetables into the egg mixture.",
            "Heat oil in a non-stick pan and pour in the mixture.",
            "Cook until the base is set, then flip and cook the other side.",
            "Serve hot with toast or rice.",
        ),
    ),
    RecipeSpec(
        "quick-meals", "Vegetable Sandwich", "vegetable-sandwich",
        "A layered sandwich with fresh cucumber, tomato, onion and a light pepper seasoning.",
        "breakfast-tiffin", 10, 5, "Easy", 2,
        _img("c/c9/Bombay_Sandwich.jpg"), "ju5nFKNkkBU",
        (
            ("Bread Slices", "8", "pcs"),
            ("Cucumber", "1", "pcs"),
            ("Tomatoes", "2", "pcs"),
            ("Onions", "1", "pcs"),
            ("Butter", "30", "g"),
            ("Black Pepper", "0.5", "tsp"),
            ("Salt", None, "to taste"),
        ),
        (
            "Thinly slice the cucumber, tomatoes and onions.",
            "Sprinkle the vegetables with salt and black pepper.",
            "Butter the bread slices lightly.",
            "Layer the vegetables between the slices and press gently.",
            "Toast in a sandwich maker or pan until golden, then cut and serve.",
        ),
    ),
    RecipeSpec(
        "quick-meals", "Curd Rice", "curd-rice",
        "Cooling rice mixed with curd and finished with a mustard seed and curry leaf tempering.",
        "lunch-dinner", 10, 20, "Easy", 4,
        _img("5/58/Curd_Rice.jpg"), "VFpzansM-XM",
        (
            ("Sona Masoori Rice", "1.5", "cups"),
            ("Curd", "400", "g"),
            ("Mustard Seeds", "1", "tsp"),
            ("Curry Leaves", "8", "leaves"),
            ("Ginger", "20", "g"),
            ("Green Chillies", "2", "pcs"),
            ("Sunflower Oil", "1", "tbsp"),
            ("Salt", None, "to taste"),
        ),
        (
            "Cook the rice until soft and let it cool to room temperature.",
            "Whisk the curd with salt until smooth.",
            "Heat oil and splutter mustard seeds, then add curry leaves, ginger and green chillies.",
            "Mix the tempered mixture and curd into the rice.",
            "Serve cool, garnished with a little extra curry leaf if desired.",
        ),
    ),
    RecipeSpec(
        "quick-meals", "Egg Fried Rice", "egg-fried-rice",
        "Fluffy rice stir-fried with eggs, vegetables and soy sauce.",
        "lunch-dinner", 15, 15, "Easy", 4,
        _img("c/c9/Egg_Fried_Rice.jpg"), "iv1frVobFeQ",
        (
            ("Basmati Rice", "2", "cups"),
            ("Eggs", "3", "pcs"),
            ("Spring Onions", "4", "pcs"),
            ("Carrot", "1", "pcs"),
            ("Green Peas", "100", "g"),
            ("Garlic", "3", "cloves"),
            ("Soy Sauce", "2", "tbsp"),
            ("Sunflower Oil", "2", "tbsp"),
            ("Salt", None, "to taste"),
        ),
        (
            "Cook the rice in advance and cool it so the grains stay separate.",
            "Beat the eggs with a pinch of salt and scramble them in a little oil. Set aside.",
            "Stir-fry chopped garlic, carrot and green peas in the remaining oil.",
            "Add the rice and toss well over medium-high heat.",
            "Pour in soy sauce and add the scrambled eggs.",
            "Finish with chopped spring onions and serve hot.",
        ),
    ),
    RecipeSpec(
        "quick-meals", "Masala Corn Chaat", "masala-corn-chaat",
        "A quick street-style snack of warm sweet corn tossed with chaat masala, lemon and herbs.",
        "snack", 10, 10, "Easy", 2,
        _img("1/12/Roasted_Sweet_Corn.jpg"), "AMPDjSZJARc",
        (
            ("Sweet Corn", "300", "g"),
            ("Onions", "1", "pcs"),
            ("Tomatoes", "1", "pcs"),
            ("Chaat Masala", "1", "tsp"),
            ("Lemon", "1", "pcs"),
            ("Coriander Leaves", "2", "tbsp"),
            ("Butter", "20", "g"),
            ("Salt", None, "to taste"),
        ),
        (
            "Boil or roast the sweet corn until tender, then drain well.",
            "Finely chop the onion, tomato and coriander leaves.",
            "Melt the butter in a pan and add the corn.",
            "Sprinkle with chaat masala and salt, then toss for 2 minutes.",
            "Add the chopped vegetables and a squeeze of lemon juice.",
            "Toss once more, garnish with coriander leaves and serve warm.",
        ),
    ),
]


def main() -> int:
    if SessionLocal is None:
        print("ERROR: DATABASE_URL is not configured. Set backend/.env and retry.")
        return 1

    db = SessionLocal()
    counts = {
        "collections_inserted": 0,
        "collections_existing": 0,
        "ingredients_inserted": 0,
        "ingredients_existing": 0,
        "recipes_inserted": 0,
        "recipes_existing": 0,
        "recipe_ingredients_inserted": 0,
        "recipe_ingredients_existing": 0,
        "mappings_inserted": 0,
        "mappings_existing": 0,
    }

    try:
        used_ingredients = {name for spec in RECIPES for name, _, _ in spec.ingredients}
        if used_ingredients != set(INGREDIENT_PRODUCTS):
            missing = sorted(used_ingredients - set(INGREDIENT_PRODUCTS))
            unused = sorted(set(INGREDIENT_PRODUCTS) - used_ingredients)
            raise ValueError(f"Ingredient catalogue mismatch. Missing: {missing}. Unused: {unused}")
        if not 60 <= len(used_ingredients) <= 70:
            raise ValueError(f"Expected 60-70 unique ingredients, found {len(used_ingredients)}")

        # Collections
        collection_by_slug: dict[str, RecipeCollection] = {}
        for item in COLLECTIONS:
            existing = db.execute(
                select(RecipeCollection).where(RecipeCollection.slug == item["slug"])
            ).scalar_one_or_none()
            if existing:
                counts["collections_existing"] += 1
                collection_by_slug[item["slug"]] = existing
                continue
            obj = RecipeCollection(
                name=item["name"],
                slug=item["slug"],
                cuisine_label=item["cuisine_label"],
                description=item["description"],
            )
            db.add(obj)
            db.flush()
            counts["collections_inserted"] += 1
            collection_by_slug[item["slug"]] = obj

        # Ingredients
        ingredient_by_name: dict[str, Ingredient] = {}
        for name in sorted(used_ingredients):
            normalized = name.strip().lower()
            existing = db.execute(
                select(Ingredient).where(Ingredient.normalized_name == normalized)
            ).scalar_one_or_none()
            if existing:
                counts["ingredients_existing"] += 1
                ingredient_by_name[name] = existing
                continue
            obj = Ingredient(name=name, normalized_name=normalized)
            db.add(obj)
            db.flush()
            counts["ingredients_inserted"] += 1
            ingredient_by_name[name] = obj

        # Product-ingredient mappings (existing products only)
        product_slugs = set(db.execute(select(Product.slug)).scalars().all())
        for name, product_slug in INGREDIENT_PRODUCTS.items():
            if not product_slug:
                continue
            if product_slug not in product_slugs:
                raise ValueError(f"Mapped product does not exist: {product_slug} for {name}")
            product = db.execute(select(Product).where(Product.slug == product_slug)).scalar_one()
            ingredient = ingredient_by_name[name]
            mapping = db.execute(
                select(ProductIngredientMapping).where(
                    ProductIngredientMapping.product_id == product.id,
                    ProductIngredientMapping.ingredient_id == ingredient.id,
                )
            ).scalar_one_or_none()
            if mapping:
                counts["mappings_existing"] += 1
                continue
            db.add(
                ProductIngredientMapping(
                    product_id=product.id,
                    ingredient_id=ingredient.id,
                    match_priority=100,
                )
            )
            counts["mappings_inserted"] += 1

        # Recipes and their ordered ingredients
        for spec in RECIPES:
            existing = db.execute(select(Recipe).where(Recipe.slug == spec.slug)).scalar_one_or_none()
            if existing:
                counts["recipes_existing"] += 1
                counts["recipe_ingredients_existing"] += db.execute(
                    select(func.count())
                    .select_from(RecipeIngredient)
                    .where(RecipeIngredient.recipe_id == existing.id)
                ).scalar_one()
                continue

            recipe = Recipe(
                collection_id=collection_by_slug[spec.collection].id,
                name=spec.name,
                slug=spec.slug,
                description=spec.description,
                meal_type=spec.meal_type,
                prep_time_minutes=spec.prep,
                cook_time_minutes=spec.cook,
                difficulty=spec.difficulty,
                serving_size=spec.servings,
                image_url=spec.image_url,
                youtube_video_id=spec.video_id,
                youtube_url=f"https://www.youtube.com/watch?v={spec.video_id}",
                instructions=json.dumps(list(spec.instructions)),
            )
            db.add(recipe)
            db.flush()
            counts["recipes_inserted"] += 1

            for order, (name, quantity, unit) in enumerate(spec.ingredients):
                ingredient = ingredient_by_name[name]
                link = db.execute(
                    select(RecipeIngredient).where(
                        RecipeIngredient.recipe_id == recipe.id,
                        RecipeIngredient.ingredient_id == ingredient.id,
                        RecipeIngredient.display_order == order,
                    )
                ).scalar_one_or_none()
                if link:
                    counts["recipe_ingredients_existing"] += 1
                    continue
                db.add(
                    RecipeIngredient(
                        recipe_id=recipe.id,
                        ingredient_id=ingredient.id,
                        quantity=Decimal(quantity) if quantity is not None else None,
                        unit=unit,
                        preparation_note=None,
                        display_order=order,
                    )
                )
                counts["recipe_ingredients_inserted"] += 1

        db.commit()

        print("RECIPE_SEED_SUMMARY")
        for key, value in counts.items():
            print(f"{key}={value}")
        for table, model in (
            ("total_collections", RecipeCollection),
            ("total_recipes", Recipe),
            ("total_ingredients", Ingredient),
            ("total_recipe_ingredients", RecipeIngredient),
            ("total_mappings", ProductIngredientMapping),
        ):
            print(f"{table}={db.execute(select(func.count()).select_from(model)).scalar_one()}")
        return 0
    except Exception as exc:
        db.rollback()
        print(f"ERROR: {type(exc).__name__}: {exc}")
        return 1
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
