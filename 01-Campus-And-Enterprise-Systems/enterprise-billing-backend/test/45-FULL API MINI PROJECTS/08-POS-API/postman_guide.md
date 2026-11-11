# Postman Guide - POS API

1. **Checkout Order (Transaction)**
   - `POST http://localhost:5000/api/pos/checkout`
   - Body:
     ```json
     {
       "customer_name": "Rohan Verma",
       "items": [
         { "item_name": "Coffee", "unit_price": 120, "quantity": 2 },
         { "item_name": "Sandwich", "unit_price": 180, "quantity": 1 }
       ]
     }
     ```

2. **List Orders**
   - `GET http://localhost:5000/api/pos/orders`

3. **Get Order Details with Items**
   - `GET http://localhost:5000/api/pos/orders/1`
