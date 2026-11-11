# 09 - req.params Undefined Error

## ERROR
`req.params.id` returns `undefined` or route parameter is not captured.

---

## WHY IT HAPPENS
1. Route definition does not match parameter name (e.g. Route defined as `/products/:productId` but controller accesses `req.params.id`).
2. Parent router line in nested router missing `{ mergeParams: true }`.

---

## HOW TO FIND IT
- `console.log(req.params)` prints `{}` (empty object) or `{ productId: '1' }` instead of `{ id: '1' }`.

---

## HOW TO FIX IT
1. Match route parameter name in router file:
```javascript
// Route definition:
router.get('/:id', getProductById);

// Controller function:
export const getProductById = async (req, res) => {
    const { id } = req.params; // Matches :id exactly
};
```
2. For nested routes (e.g., `/api/categories/:categoryId/products`):
```javascript
const router = express.Router({ mergeParams: true });
```

---

## COMMON EXAM MISTAKE
Writing `router.get('/products/id')` (missing colon `:`) instead of `router.get('/products/:id')`.
