"""Catalogue-wide product image correction.

Replaces duplicate, incorrect and unrelated product photographs with
product-specific images. Only products.image_url is updated, by slug with
old/new URL guards; names, descriptions, prices, quantities, categories and
availability are untouched.

Revision ID: 0005_audit_product_images
Revises: 0004_repair_product_images
Create Date: 2026-11-17
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0005_audit_product_images"
down_revision = "0004_repair_product_images"
branch_labels = None
depends_on = None

# (slug, product name, previous image_url, corrected image_url)
CHANGES = [
    ("brinjal-500g", "Brinjal (Eggplant)", "https://images.unsplash.com/photo-1615484477778-ca3b77940c25?auto=format&fit=crop&w=800&q=80", "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1a/Eggplant_%28Solanum_melongena%29.JPG/960px-Eggplant_%28Solanum_melongena%29.JPG"),
    ("brown-rice-1kg", "Brown Rice", "https://images.unsplash.com/photo-1586201375761-83865001e31c?auto=format&fit=crop&w=800&q=80", "https://upload.wikimedia.org/wikipedia/commons/d/d1/Reis_-_Sorte_C_voll.jpg"),
    ("chana-dal-1kg", "Chana Dal", "https://images.unsplash.com/photo-1596040033229-a9821ebd058d?auto=format&fit=crop&w=800&q=80", "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a5/Chana_Dal_%28split_Bengal_gram%29.JPG/960px-Chana_Dal_%28split_Bengal_gram%29.JPG"),
    ("coriander-powder-200g", "Coriander Powder", "https://images.unsplash.com/photo-1596040033229-a9821ebd058d?auto=format&fit=crop&w=800&q=80", "https://upload.wikimedia.org/wikipedia/commons/thumb/6/64/Coriander_powder.JPG/960px-Coriander_powder.JPG"),
    ("curry-leaves-50g", "Curry Leaves", "https://images.unsplash.com/photo-1597362925123-77861d3fbac7?auto=format&fit=crop&w=800&q=80", "https://upload.wikimedia.org/wikipedia/commons/thumb/9/96/Fresh_curry_leaves.jpg/960px-Fresh_curry_leaves.jpg"),
    ("dosa-rice-5kg", "Dosa Rice", "https://images.unsplash.com/photo-1586201375761-83865001e31c?auto=format&fit=crop&w=800&q=80", "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6e/Uncooked_ST25_rice_on_bamboo_surface.jpg/960px-Uncooked_ST25_rice_on_bamboo_surface.jpg"),
    ("drumsticks-250g", "Drumsticks", "https://images.unsplash.com/photo-1597362925123-77861d3fbac7?auto=format&fit=crop&w=800&q=80", "https://upload.wikimedia.org/wikipedia/commons/thumb/8/81/Moringa_oleifera_drumstick_pods.JPG/960px-Moringa_oleifera_drumstick_pods.JPG"),
    ("foxtail-millet-1kg", "Foxtail Millet", "https://images.unsplash.com/photo-1627485937980-221c88ac04f9?auto=format&fit=crop&w=800&q=80", "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f1/Food_grain_foxtail_millet.jpg/960px-Food_grain_foxtail_millet.jpg"),
    ("garam-masala-100g", "Garam Masala", "https://images.unsplash.com/photo-1596040033229-a9821ebd058d?auto=format&fit=crop&w=800&q=80", "https://upload.wikimedia.org/wikipedia/commons/thumb/5/58/Garammasalaphoto.jpg/960px-Garammasalaphoto.jpg"),
    ("gingelly-oil-500ml", "Gingelly (Sesame) Oil", "https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?auto=format&fit=crop&w=800&q=80", "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fb/Sesame-oil.jpg/960px-Sesame-oil.jpg"),
    ("green-chillies-250g", "Green Chillies", "https://images.unsplash.com/photo-1583119022894-919a68a3d0e3?auto=format&fit=crop&w=800&q=80", "https://upload.wikimedia.org/wikipedia/commons/0/08/Green_chillies_from_Indian_farms.jpg"),
    ("green-gram-whole-1kg", "Green Gram Whole", "https://images.unsplash.com/photo-1596040033229-a9821ebd058d?auto=format&fit=crop&w=800&q=80", "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a1/Vigna.radiata.seeds.jpg/960px-Vigna.radiata.seeds.jpg"),
    ("groundnut-oil-1l", "Groundnut Oil", "https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?auto=format&fit=crop&w=800&q=80", "https://upload.wikimedia.org/wikipedia/commons/thumb/2/27/Groundnut_oil.jpg/960px-Groundnut_oil.jpg"),
    ("idli-rice-5kg", "Idli Rice", "https://images.unsplash.com/photo-1586201375761-83865001e31c?auto=format&fit=crop&w=800&q=80", "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2d/Rice_Grains_1.jpg/960px-Rice_Grains_1.jpg"),
    ("jaggery-powder-1kg", "Jaggery Powder", "https://images.unsplash.com/photo-1621939514649-280e2ee25f60?auto=format&fit=crop&w=800&q=80", "https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/An_image_of_jaggery_powder.JPG/960px-An_image_of_jaggery_powder.JPG"),
    ("little-millet-1kg", "Little Millet", "https://images.unsplash.com/photo-1627485937980-221c88ac04f9?auto=format&fit=crop&w=800&q=80", "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f8/A_closeup_fo_Samai_millet_with_husk.JPG/960px-A_closeup_fo_Samai_millet_with_husk.JPG"),
    ("masoor-dal-1kg", "Masoor Dal", "https://images.unsplash.com/photo-1596040033229-a9821ebd058d?auto=format&fit=crop&w=800&q=80", "https://upload.wikimedia.org/wikipedia/commons/3/38/Masoor_dal.JPG"),
    ("moong-dal-1kg", "Moong Dal", "https://images.unsplash.com/photo-1596040033229-a9821ebd058d?auto=format&fit=crop&w=800&q=80", "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2a/Moong_Dal.jpg/960px-Moong_Dal.jpg"),
    ("pomegranates-500g", "Pomegranates", "https://images.unsplash.com/photo-1615485500704-8e990f9900f7?auto=format&fit=crop&w=800&q=80", "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fa/Pomegranate_fruit_-_whole_and_piece_with_arils.jpg/960px-Pomegranate_fruit_-_whole_and_piece_with_arils.jpg"),
    ("rasam-powder-200g", "Rasam Powder", "https://images.unsplash.com/photo-1596040033229-a9821ebd058d?auto=format&fit=crop&w=800&q=80", "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ea/Rasam_powder_picture.JPG/960px-Rasam_powder_picture.JPG"),
    ("red-chilli-powder-200g", "Red Chilli Powder", "https://images.unsplash.com/photo-1596040033229-a9821ebd058d?auto=format&fit=crop&w=800&q=80", "https://upload.wikimedia.org/wikipedia/commons/0/00/BolivianChilePowder2.JPG"),
    ("rice-flour-1kg", "Rice Flour", "https://images.unsplash.com/photo-1604908176997-125f25cc6f3d?auto=format&fit=crop&w=800&q=80", "https://upload.wikimedia.org/wikipedia/commons/1/19/Two_kinds_of_rice_flour.jpg"),
    ("roasted-rava-1kg", "Roasted Rava (Sooji)", "https://images.unsplash.com/photo-1627485937980-221c88ac04f9?auto=format&fit=crop&w=800&q=80", "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c6/Sa_semolina_far.jpg/960px-Sa_semolina_far.jpg"),
    ("sambar-powder-200g", "Sambar Powder", "https://images.unsplash.com/photo-1596040033229-a9821ebd058d?auto=format&fit=crop&w=800&q=80", "https://upload.wikimedia.org/wikipedia/commons/thumb/3/32/Sambar_powder.jpg/960px-Sambar_powder.jpg"),
    ("sona-masoori-rice-5kg", "Sona Masoori Rice", "https://images.unsplash.com/photo-1586201375761-83865001e31c?auto=format&fit=crop&w=800&q=80", "https://upload.wikimedia.org/wikipedia/commons/thumb/2/29/Masoori_Rice_%285193854729%29.jpg/960px-Masoori_Rice_%285193854729%29.jpg"),
    ("sugar-1kg", "Sugar", "https://images.unsplash.com/photo-1621939514649-280e2ee25f60?auto=format&fit=crop&w=800&q=80", "https://upload.wikimedia.org/wikipedia/commons/8/84/White-Sugar-Crystals_61460-480x360_%284905066920%29.jpg"),
    ("sunflower-oil-1l", "Sunflower Oil", "https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?auto=format&fit=crop&w=800&q=80", "https://upload.wikimedia.org/wikipedia/commons/thumb/3/33/Bottle_1_liter_Sunflower_refined_oil.jpg/960px-Bottle_1_liter_Sunflower_refined_oil.jpg"),
    ("toor-dal-1kg", "Toor Dal", "https://images.unsplash.com/photo-1596040033229-a9821ebd058d?auto=format&fit=crop&w=800&q=80", "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a2/Tur_Dal.JPG/960px-Tur_Dal.JPG"),
    ("turmeric-powder-200g", "Turmeric Powder", "https://images.unsplash.com/photo-1615485500704-8e990f9900f7?auto=format&fit=crop&w=800&q=80", "https://upload.wikimedia.org/wikipedia/commons/thumb/9/90/Kunyit_Bubuk.jpg/960px-Kunyit_Bubuk.jpg"),
    ("urad-dal-split-1kg", "Urad Dal Split", "https://images.unsplash.com/photo-1596040033229-a9821ebd058d?auto=format&fit=crop&w=800&q=80", "https://upload.wikimedia.org/wikipedia/commons/thumb/0/09/%E0%AE%89%E0%AE%B4%E0%AF%81%E0%AE%A8%E0%AF%8D%E0%AE%A4%E0%AF%81_3.JPG/960px-%E0%AE%89%E0%AE%B4%E0%AF%81%E0%AE%A8%E0%AF%8D%E0%AE%A4%E0%AF%81_3.JPG"),
    ("urad-dal-whole-1kg", "Urad Dal Whole", "https://images.unsplash.com/photo-1596040033229-a9821ebd058d?auto=format&fit=crop&w=800&q=80", "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6f/Black_gram.jpg/960px-Black_gram.jpg"),
    ("whole-wheat-atta-5kg", "Whole Wheat Atta", "https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?auto=format&fit=crop&w=800&q=80", "https://upload.wikimedia.org/wikipedia/commons/1/11/Wheat-flour.jpg"),
]


def upgrade() -> None:
    for slug, _name, old, new in CHANGES:
        op.execute(
            sa.text(
                "UPDATE products SET image_url = :new "
                "WHERE slug = :slug AND image_url = :old"
            ).bindparams(new=new, slug=slug, old=old)
        )


def downgrade() -> None:
    for slug, _name, old, new in CHANGES:
        op.execute(
            sa.text(
                "UPDATE products SET image_url = :old "
                "WHERE slug = :slug AND image_url = :new"
            ).bindparams(old=old, slug=slug, new=new)
        )
