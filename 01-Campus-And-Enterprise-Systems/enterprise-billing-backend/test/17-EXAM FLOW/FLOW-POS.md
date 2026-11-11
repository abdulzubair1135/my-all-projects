# Master Summary Flow: POS (Point of Sale) Project

Multi-entity workflow system handling Users, Franchises, Products, and Billing generation.

---

## 1. Relational Entities & Data Flow
1. **Users (Cashier/Admin):** Authenticates into system, attached to bill generation.
2. **Franchises (Branch/Store):** Stores franchise metadata (Name, Code, Location).
3. **Products (Items):** Belongs to a franchise, maintains stock and unit price.
4. **Bills (Transactions):** Linked to franchise and cashier user. Calculates tax, subtotal, grand total.

---

## 2. Execution Flow for Billing Endpoint (`POST /api/bills`)
```
Request Payload:
{
  "franchise_id": 1,
  "items": [
    { "product_id": 101, "quantity": 2 },
    { "product_id": 102, "quantity": 1 }
  ],
  "tax_rate": 0.18 // 18% GST
}

Step 1: Auth Middleware verifies token -> extracts req.user.id.
Step 2: Validation check for items array and valid IDs.
Step 3: Fetch product prices from Database using product_ids.
Step 4: Subtotal = SUM(price * qty), Tax = Subtotal * tax_rate, Grand Total = Subtotal + Tax.
Step 5: Insert record into `bills` table.
Step 6: Update product stocks in database.
Step 7: Return final Invoice JSON payload.
```
