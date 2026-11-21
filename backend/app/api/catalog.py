from math import ceil
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, joinedload

from app.database.session import get_db
from app.models.catalog import Product, ProductCategory
from app.schemas.catalog import CategoryOut, ProductListOut, ProductOut
from app.utils.search import ilike_contains

router = APIRouter(prefix="/catalog", tags=["catalog"])


@router.get("/categories", response_model=list[CategoryOut])
def list_categories(db: Session = Depends(get_db)):
    stmt = select(ProductCategory).order_by(ProductCategory.name.asc())
    return db.execute(stmt).scalars().all()


@router.get("/products", response_model=ProductListOut)
def list_products(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(12, ge=1, le=50),
    category: str | None = Query(None, description="Category slug"),
    category_id: UUID | None = Query(None),
    search: str | None = Query(None, description="Search by product name"),
    available_only: bool = Query(True),
):
    filters = []
    if available_only:
        filters.append(Product.is_available.is_(True))
    if search:
        name_filter = ilike_contains(Product.name, search)
        if name_filter is not None:
            filters.append(name_filter)
    if category_id:
        filters.append(Product.category_id == category_id)
    if category:
        filters.append(Product.category.has(ProductCategory.slug == category))

    base = select(Product).options(joinedload(Product.category)).where(*filters)
    count_stmt = select(func.count()).select_from(select(Product.id).where(*filters).subquery())
    total = db.execute(count_stmt).scalar_one()

    stmt = (
        base.order_by(Product.name.asc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    items = db.execute(stmt).scalars().unique().all()
    pages = ceil(total / page_size) if total else 0
    return ProductListOut(items=items, total=total, page=page, page_size=page_size, pages=pages)


@router.get("/products/{product_slug}", response_model=ProductOut)
def get_product(product_slug: str, db: Session = Depends(get_db)):
    stmt = (
        select(Product)
        .options(joinedload(Product.category))
        .where(Product.slug == product_slug)
    )
    product = db.execute(stmt).scalars().unique().first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product
