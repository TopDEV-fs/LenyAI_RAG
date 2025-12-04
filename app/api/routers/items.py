from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

class Item(BaseModel):
    id: int
    name: str
    description: Optional[str] = None

# In-memory store for demo purposes
_items_store = {
    1: {"id": 1, "name": "Widget", "description": "A useful widget"},
    2: {"id": 2, "name": "Gadget", "description": "A shiny gadget"},
}

@router.get("/", response_model=list[Item])
async def list_items():
    return list(_items_store.values())

@router.get("/{item_id}", response_model=Item)
async def get_item(item_id: int):
    item = _items_store.get(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@router.post("/", response_model=Item, status_code=201)
async def create_item(item: Item):
    if item.id in _items_store:
        raise HTTPException(status_code=400, detail="Item ID already exists")
    _items_store[item.id] = item.dict()
    return item

@router.put("/{item_id}", response_model=Item)
async def update_item(item_id: int, item: Item):
    if item_id != item.id:
        raise HTTPException(status_code=400, detail="Item ID mismatch")
    if item_id not in _items_store:
        raise HTTPException(status_code=404, detail="Item not found")
    _items_store[item_id] = item.dict()
    return item

@router.delete("/{item_id}")
async def delete_item(item_id: int):
    if item_id not in _items_store:
        raise HTTPException(status_code=404, detail="Item not found")
    del _items_store[item_id]
    return {"ok": True}
