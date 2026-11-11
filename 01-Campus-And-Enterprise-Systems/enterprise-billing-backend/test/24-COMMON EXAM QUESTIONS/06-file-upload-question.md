# 06 - File Upload with Multer Exam Question

## QUESTION
Implement an Image/File Upload endpoint using `multer` middleware for uploading product images, saving filename to database, and serving static uploaded images.

---

## REQUIREMENTS
- Limit upload file size (e.g. 2MB max).
- Restrict file extension types to images (`.jpg`, `.jpeg`, `.png`).
- Serve static uploaded directory via `express.static('uploads')`.

---

## TABLES
```sql
CREATE TABLE products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    image_url VARCHAR(255) DEFAULT NULL
);
```

---

## FILES REQUIRED
1. `middleware/uploadMiddleware.js`
2. `controllers/productController.js`
3. `routes/productRoutes.js`
4. `server.js`

---

## CODING ORDER
1. Install multer `npm install multer`.
2. Configure storage engine in `middleware/uploadMiddleware.js`.
3. Add static file hosting in `server.js`: `app.use('/uploads', express.static('uploads'))`.
4. Attach `upload.single('image')` to upload route.

---

## API FLOW
`POST /api/products/upload` (form-data: `image` file) -> Multer saves file to `./uploads/` -> Controller inserts filename `req.file.filename` to DB -> Returns file path.

---

## POSTMAN TEST
- Select `POST /api/products/upload`.
- Select Body -> `form-data`. Key: `image` (Type: File), Value: select local `.png` image.

---

## COMMON MISTAKES
- Selecting `raw` JSON in Postman instead of `form-data`.
- Forgetting to create `uploads/` folder manually or auto-creating it in code.
