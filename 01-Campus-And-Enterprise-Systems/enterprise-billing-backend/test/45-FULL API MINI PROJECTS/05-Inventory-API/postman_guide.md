# Postman Guide - Inventory API

1. `GET /api/inventory` - Get all inventory items
2. `GET /api/inventory/1` - Get single item
3. `POST /api/inventory` - Add inventory item
   Body: `{ "item_code": "INV-004", "item_name": "HDMI Cable 2m", "quantity": 100, "min_level": 15, "supplier": "CableWorld" }`
4. `PUT /api/inventory/1` - Update item
5. `DELETE /api/inventory/1` - Delete item
