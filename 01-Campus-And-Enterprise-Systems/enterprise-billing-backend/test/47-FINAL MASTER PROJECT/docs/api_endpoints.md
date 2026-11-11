# API Endpoints Reference

| Method | Endpoint | Access | Description |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/auth/register` | Public | Register a new user |
| `POST` | `/api/auth/login` | Public | Authenticate user & get JWT token |
| `GET` | `/api/auth/profile` | Auth User | Get current user's profile details |
| `POST` | `/api/auth/avatar` | Auth User | Upload/update profile picture (Multer) |
| `GET` | `/api/categories` | Public | List all categories |
| `POST` | `/api/categories` | Admin | Create a new category |
| `PUT` | `/api/categories/:id` | Admin | Update existing category |
| `DELETE`| `/api/categories/:id` | Admin | Delete category |
| `GET` | `/api/products` | Public | Fetch products with Search & Pagination |
| `GET` | `/api/products/:id` | Public | Get single product details |
| `POST` | `/api/products` | Admin | Create product with optional image upload |
| `PUT` | `/api/products/:id` | Admin | Update product details |
| `DELETE`| `/api/products/:id` | Admin | Delete product |
| `POST` | `/api/orders/checkout` | Auth User | Checkout order with DB Transaction |
| `GET` | `/api/orders/my-orders` | Auth User | Get order history of logged-in user |
| `GET` | `/api/orders/:id` | Auth User/Admin | Get detailed breakdown of an order |
