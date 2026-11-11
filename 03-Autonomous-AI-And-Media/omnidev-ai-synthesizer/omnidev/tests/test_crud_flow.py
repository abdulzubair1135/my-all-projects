import unittest
import time
import shutil
from pathlib import Path
import sys

OMNIDEV_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(OMNIDEV_DIR))

from builders.crud_builder import CRUDAppBuilder
from brains.base_brain import BaseBrain
import config

class MockCRUDAppBrain(BaseBrain):
    def ask(self, prompt: str, **kwargs) -> str:
        # Returns a complete working standalone FastAPI CRUD app with SQLite and HTML UI
        return '''FILE: main.py
```python
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Optional
import sqlite3
import os

app = FastAPI(title="Task Manager CRUD")

DB_PATH = "tasks.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            price REAL DEFAULT 0.0
        )
    """)
    conn.commit()
    conn.close()

init_db()

class ItemCreate(BaseModel):
    name: str
    description: Optional[str] = ""
    price: Optional[float] = 0.0

class ItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None

class Item(BaseModel):
    id: int
    name: str
    description: str
    price: float

@app.get("/", response_class=HTMLResponse)
def index():
    return "<html><head><title>Task Manager</title></head><body><h1>Task Manager App</h1></body></html>"

@app.get("/api/items")
def get_items():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, name, description, price FROM items")
    rows = c.fetchall()
    conn.close()
    return [{"id": r[0], "name": r[1], "description": r[2], "price": r[3]} for r in rows]

@app.post("/api/items")
def create_item(item: ItemCreate):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO items (name, description, price) VALUES (?, ?, ?)", (item.name, item.description, item.price))
    conn.commit()
    new_id = c.lastrowid
    conn.close()
    return {"id": new_id, "name": item.name, "description": item.description, "price": item.price}

@app.get("/api/items/{item_id}")
def get_item(item_id: int):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, name, description, price FROM items WHERE id = ?", (item_id,))
    row = c.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"id": row[0], "name": row[1], "description": row[2], "price": row[3]}

@app.put("/api/items/{item_id}")
def update_item(item_id: int, item: ItemUpdate):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE items SET name = coalesce(?, name), description = coalesce(?, description), price = coalesce(?, price) WHERE id = ?",
              (item.name, item.description, item.price, item_id))
    conn.commit()
    conn.close()
    return {"status": "updated", "id": item_id}

@app.delete("/api/items/{item_id}")
def delete_item(item_id: int):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM items WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()
    return {"status": "deleted", "id": item_id}
```'''

    def is_available(self) -> bool:
        return True

class TestCRUDLifecycle(unittest.TestCase):
    def setUp(self):
        self.brain = MockCRUDAppBrain()
        self.builder = CRUDAppBuilder(self.brain, OMNIDEV_DIR / "tests" / "test_workspace")

    def tearDown(self):
        self.builder.process_manager.stop_all()
        test_ws = OMNIDEV_DIR / "tests" / "test_workspace"
        if test_ws.exists():
            shutil.rmtree(test_ws, ignore_errors=True)

    def test_full_crud_build_launch_and_test(self):
        result = self.builder.build_and_launch("Test Todo CRUD", app_dir_name="sample_todo_app")
        self.assertTrue(result["success"])
        self.assertIn("http://127.0.0.1", result["app_url"])
        self.assertTrue(result["test_summary"]["all_passed"])

if __name__ == "__main__":
    unittest.main()
