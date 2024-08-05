from fastapi import APIRouter, HTTPException

from sqlmodel import Session, select

from models import engine

from models.item_models import CreatedItem, DBItem, Item, ItemList, UpdatedItem



router = APIRouter(prefix="/items", tags=["item"])


@router.post("/{merchant_id}")
async def create_item(item: CreatedItem, merchant_id: int) -> Item:
    data = item.dict()
    db_item = DBItem(**data)
    db_item.merchant_id = merchant_id
    with Session(engine) as session:
        session.add(db_item)
        session.commit()
        session.refresh(db_item)

    return Item.from_orm(db_item)


@router.get("")
async def get_items(page: int = 1, page_size: int = 10) -> ItemList:
    with Session(engine) as session:
        db_items = session.exec(
            select(DBItem).offset((page - 1) * page_size).limit(page_size)
        ).all()

    return ItemList(
        items=db_items, page=page, page_size=page_size, size_per_page=len(db_items)
    )


@router.get("/{item_id}")
async def get_item(item_id: int) -> Item:
    with Session(engine) as session:
        db_item = session.get(DBItem, item_id)
        if db_item is None:
            raise HTTPException(status_code=404, detail="Item not found")

        return Item.from_orm(db_item)


@router.put("/{item_id}")
async def update_item(item_id: int, item: UpdatedItem) -> Item:
    with Session(engine) as session:
        db_item = session.get(DBItem, item_id)
        if db_item is None:
            raise HTTPException(status_code=404, detail="Item not found")
        for key, value in item.dict().items():
            setattr(db_item, key, value)
            session.add(db_item)
            session.commit()
            session.refresh(db_item)

    return Item.from_orm(db_item)


@router.delete("/{item_id}")
async def delete_item(item_id: int) -> dict:
    with Session(engine) as session:
        db_item = session.get(DBItem, item_id)
        if db_item is None:
            raise HTTPException(status_code=404, detail="Item not found")
        session.delete(db_item)
        session.commit()

    return dict(message="Item deleted successfully")
