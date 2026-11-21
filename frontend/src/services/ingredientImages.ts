/**
 * Curated ingredient image catalogue for pantry cards.
 *
 * Every ingredient returned by `/api/kitchen/ingredients` has an explicit,
 * normalized-name entry so cards never fall back to a generic placeholder.
 * Sources are authoritative Wikimedia Commons photographs of the exact
 * ingredient, or existing CookKart product photographs where the product is
 * the same ingredient. Keys are lowercase/trimmed to match the lookup used by
 * PantryManager.
 */
export const INGREDIENT_IMAGE_URLS: Readonly<Record<string, string>> = Object.freeze({
  'all-purpose flour': 'https://upload.wikimedia.org/wikipedia/commons/thumb/6/64/All-Purpose_Flour_%284107895947%29.jpg/960px-All-Purpose_Flour_%284107895947%29.jpg',
  'asafoetida': 'https://upload.wikimedia.org/wikipedia/commons/thumb/5/50/Asafoetida2.jpg/960px-Asafoetida2.jpg',
  'baguette': 'https://upload.wikimedia.org/wikipedia/commons/thumb/8/86/Baguettes%2C_Paris%2C_France_-_panoramio.jpg/960px-Baguettes%2C_Paris%2C_France_-_panoramio.jpg',
  'basmati rice': 'https://upload.wikimedia.org/wikipedia/commons/thumb/f/f8/Basmati_Rice_India%2C_raw.jpg/960px-Basmati_Rice_India%2C_raw.jpg',
  'black pepper': 'https://upload.wikimedia.org/wikipedia/commons/thumb/8/81/Tellicherry_Black_Peppercorns.jpg/960px-Tellicherry_Black_Peppercorns.jpg',
  'bread slices': 'https://upload.wikimedia.org/wikipedia/commons/thumb/7/79/Vegan_no-knead_whole_wheat_bread_loaf%2C_sliced%2C_September_2010.jpg/960px-Vegan_no-knead_whole_wheat_bread_loaf%2C_sliced%2C_September_2010.jpg',
  'butter': 'https://upload.wikimedia.org/wikipedia/commons/thumb/d/d3/%C5%A0v%C3%A9dsk%C3%BD_kol%C3%A1%C4%8D_naruby_904_%28cropped%29.JPG/960px-%C5%A0v%C3%A9dsk%C3%BD_kol%C3%A1%C4%8D_naruby_904_%28cropped%29.JPG',
  'button mushrooms': 'https://upload.wikimedia.org/wikipedia/commons/0/01/ChampignonMushroom.jpg',
  'cabbage': 'https://upload.wikimedia.org/wikipedia/commons/thumb/6/6f/Cabbage_and_cross_section_on_white.jpg/960px-Cabbage_and_cross_section_on_white.jpg',
  'capsicum': 'https://upload.wikimedia.org/wikipedia/commons/thumb/d/da/Red_capsicum_and_cross_section.jpg/960px-Red_capsicum_and_cross_section.jpg',
  'carrot': 'https://images.unsplash.com/photo-1598170845058-32b9d6a5da37?auto=format&fit=crop&w=800&q=80',
  'cashew nuts': 'https://upload.wikimedia.org/wikipedia/commons/thumb/f/f7/DFC_6137_Close-up_of_fresh_cashew_apples_yellow_fruits_and_shelled_cashew_kernels_at_a_local_market_in_Klet_Kaeo_Sattahip_Chon_Buri_Thailand.jpg/960px-DFC_6137_Close-up_of_fresh_cashew_apples_yellow_fruits_and_shelled_cashew_kernels_at_a_local_market_in_Klet_Kaeo_Sattahip_Chon_Buri_Thailand.jpg',
  'chaat masala': 'https://upload.wikimedia.org/wikipedia/commons/e/e5/Chaatmasala.jpg',
  'chickpeas': 'https://images.unsplash.com/photo-1515543904379-3d757afe72e4?auto=format&fit=crop&w=800&q=80',
  'chilli sauce': 'https://upload.wikimedia.org/wikipedia/commons/4/43/Swedish_chili_sauces.JPG',
  'coriander leaves': 'https://upload.wikimedia.org/wikipedia/commons/thumb/b/b7/Bunches_of_coriander_leaves.jpg/960px-Bunches_of_coriander_leaves.jpg',
  'coriander powder': 'https://upload.wikimedia.org/wikipedia/commons/thumb/6/64/Coriander_powder.JPG/960px-Coriander_powder.JPG',
  'cornflour': 'https://upload.wikimedia.org/wikipedia/commons/thumb/d/d5/Cornstarch_mixed_with_water.jpg/960px-Cornstarch_mixed_with_water.jpg',
  'cream': 'https://upload.wikimedia.org/wikipedia/commons/thumb/8/80/Cream_Drop.jpg/960px-Cream_Drop.jpg',
  'cucumber': 'https://upload.wikimedia.org/wikipedia/commons/thumb/9/96/ARS_cucumber.jpg/960px-ARS_cucumber.jpg',
  'cumin seeds': 'https://upload.wikimedia.org/wikipedia/commons/thumb/6/61/Whole_Cumin_Seeds.jpg/960px-Whole_Cumin_Seeds.jpg',
  'curd': 'https://images.unsplash.com/photo-1488477181946-6428a0291777?auto=format&fit=crop&w=800&q=80',
  'curry leaves': 'https://upload.wikimedia.org/wikipedia/commons/thumb/9/96/Fresh_curry_leaves.jpg/960px-Fresh_curry_leaves.jpg',
  'dosa rice': 'https://upload.wikimedia.org/wikipedia/commons/thumb/6/6e/Uncooked_ST25_rice_on_bamboo_surface.jpg/960px-Uncooked_ST25_rice_on_bamboo_surface.jpg',
  'dried basil': 'https://upload.wikimedia.org/wikipedia/commons/thumb/9/97/Ocimum_basilicum_8zz.jpg/960px-Ocimum_basilicum_8zz.jpg',
  'dried oregano': 'https://upload.wikimedia.org/wikipedia/commons/thumb/1/14/Origanum_vulgare_-_harilik_pune.jpg/960px-Origanum_vulgare_-_harilik_pune.jpg',
  'drumstick': 'https://upload.wikimedia.org/wikipedia/commons/thumb/8/81/Moringa_oleifera_drumstick_pods.JPG/960px-Moringa_oleifera_drumstick_pods.JPG',
  'eggs': 'https://images.unsplash.com/photo-1582722872445-44dc5f7e3c8f?auto=format&fit=crop&w=800&q=80',
  'fenugreek seeds': 'https://upload.wikimedia.org/wikipedia/commons/thumb/1/16/Fenugreek_Seeds_01.jpg/960px-Fenugreek_Seeds_01.jpg',
  'garam masala': 'https://upload.wikimedia.org/wikipedia/commons/thumb/5/58/Garammasalaphoto.jpg/960px-Garammasalaphoto.jpg',
  'garlic': 'https://upload.wikimedia.org/wikipedia/commons/thumb/9/9a/Garlic_bulbs_and_cloves.jpg/960px-Garlic_bulbs_and_cloves.jpg',
  'ginger': 'https://upload.wikimedia.org/wikipedia/commons/thumb/f/f2/Fresh_Ginger.JPG/960px-Fresh_Ginger.JPG',
  'gram flour': 'https://upload.wikimedia.org/wikipedia/commons/thumb/5/5e/Gram_flour_AvL.jpg/960px-Gram_flour_AvL.jpg',
  'green chillies': 'https://images.unsplash.com/photo-1583119022894-919a68a3d0e3?auto=format&fit=crop&w=800&q=80',
  'green peas': 'https://upload.wikimedia.org/wikipedia/commons/thumb/6/69/Pea-shelled.JPG/960px-Pea-shelled.JPG',
  'hakka noodles': 'https://upload.wikimedia.org/wikipedia/commons/9/9f/Hakka_Noodles%2C_Veg_Manchurian_PK009.jpg',
  'idli rice': 'https://upload.wikimedia.org/wikipedia/commons/thumb/2/2d/Rice_Grains_1.jpg/960px-Rice_Grains_1.jpg',
  'kasuri methi': 'https://upload.wikimedia.org/wikipedia/commons/thumb/6/68/Dried_leaves_of_Fenugreek-Kasuri_Methi.jpg/960px-Dried_leaves_of_Fenugreek-Kasuri_Methi.jpg',
  'lemon': 'https://upload.wikimedia.org/wikipedia/commons/thumb/e/e4/P1030323.JPG/960px-P1030323.JPG',
  'milk': 'https://images.unsplash.com/photo-1563636619-e9143da7973b?auto=format&fit=crop&w=800&q=80',
  'mozzarella cheese': 'https://upload.wikimedia.org/wikipedia/commons/thumb/5/57/Mozzarella_di_bufala3.jpg/960px-Mozzarella_di_bufala3.jpg',
  'mustard seeds': 'https://upload.wikimedia.org/wikipedia/commons/thumb/b/b4/Mustard_black.JPG/960px-Mustard_black.JPG',
  'olive oil': 'https://upload.wikimedia.org/wikipedia/commons/f/f1/Bottle_of_Extra_Virgin_Olive_Oil.jpg',
  'onions': 'https://images.unsplash.com/photo-1618512496248-a07fe83aa8cb?auto=format&fit=crop&w=800&q=80',
  'paneer': 'https://images.unsplash.com/photo-1631452180519-c014fe946bc7?auto=format&fit=crop&w=800&q=80',
  'peanuts': 'https://upload.wikimedia.org/wikipedia/commons/thumb/7/79/Peanut_Kernels.jpg/960px-Peanut_Kernels.jpg',
  'penne pasta': 'https://upload.wikimedia.org/wikipedia/commons/thumb/0/0b/Pennelisce_closeup.png/960px-Pennelisce_closeup.png',
  'pizza base': 'https://upload.wikimedia.org/wikipedia/commons/thumb/8/87/Masa_de_pizza_con_salsa_de_tomates_y_cebolla_junto_a_sus_ingredientes_listos_para_armar.jpg/960px-Masa_de_pizza_con_salsa_de_tomates_y_cebolla_junto_a_sus_ingredientes_listos_para_armar.jpg',
  'poha (flattened rice)': 'https://images.unsplash.com/photo-1604329760661-e71dc83f8f26?auto=format&fit=crop&w=800&q=80',
  'potatoes': 'https://images.unsplash.com/photo-1518977676601-b53f82aba655?auto=format&fit=crop&w=800&q=80',
  'red chilli powder': 'https://upload.wikimedia.org/wikipedia/commons/0/00/BolivianChilePowder2.JPG',
  'salt': 'https://upload.wikimedia.org/wikipedia/commons/thumb/d/d8/EdibleSalt.jpg/960px-EdibleSalt.jpg',
  'sambar powder': 'https://upload.wikimedia.org/wikipedia/commons/thumb/3/32/Sambar_powder.jpg/960px-Sambar_powder.jpg',
  'sesame oil': 'https://upload.wikimedia.org/wikipedia/commons/thumb/f/fb/Sesame-oil.jpg/960px-Sesame-oil.jpg',
  'sona masoori rice': 'https://upload.wikimedia.org/wikipedia/commons/thumb/2/29/Masoori_Rice_%285193854729%29.jpg/960px-Masoori_Rice_%285193854729%29.jpg',
  'soy sauce': 'https://upload.wikimedia.org/wikipedia/commons/thumb/6/63/Soy_sauce_2.jpg/960px-Soy_sauce_2.jpg',
  'spinach': 'https://upload.wikimedia.org/wikipedia/commons/thumb/5/56/Fresh_Spinach_leaves.jpg/960px-Fresh_Spinach_leaves.jpg',
  'spring onions': 'https://upload.wikimedia.org/wikipedia/commons/thumb/d/da/CSA-Red-Spring-Onions.jpg/960px-CSA-Red-Spring-Onions.jpg',
  'spring roll wrappers': 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/a8/Spring_roll_wrappers_in_Jincheng.jpg/960px-Spring_roll_wrappers_in_Jincheng.jpg',
  'sunflower oil': 'https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?auto=format&fit=crop&w=800&q=80',
  'sweet corn': 'https://upload.wikimedia.org/wikipedia/commons/7/79/VegCorn.jpg',
  'tamarind': 'https://upload.wikimedia.org/wikipedia/commons/thumb/c/c1/Tamarind2.jpg/960px-Tamarind2.jpg',
  'tomato puree': 'https://upload.wikimedia.org/wikipedia/commons/9/94/Tomato_passata.jpg',
  'tomatoes': 'https://upload.wikimedia.org/wikipedia/commons/thumb/8/88/Bright_red_tomato_and_cross_section02.jpg/960px-Bright_red_tomato_and_cross_section02.jpg',
  'toor dal': 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/a2/Tur_Dal.JPG/960px-Tur_Dal.JPG',
  'turmeric powder': 'https://upload.wikimedia.org/wikipedia/commons/thumb/9/90/Kunyit_Bubuk.jpg/960px-Kunyit_Bubuk.jpg',
  'urad dal': 'https://upload.wikimedia.org/wikipedia/commons/thumb/6/6f/Black_gram.jpg/960px-Black_gram.jpg',
  'whole wheat flour': 'https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?auto=format&fit=crop&w=800&q=80',
})

/** Returns the curated image URL for an ingredient, if one exists. */
export function getIngredientImageUrl(name: string | null | undefined): string | undefined {
  if (!name) return undefined
  return INGREDIENT_IMAGE_URLS[name.trim().toLowerCase()]
}
