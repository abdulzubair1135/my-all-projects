const express = require('express');
const router = express.Router();
const storeController = require('../controllers/storeController');
const authenticateToken = require('../middleware/auth');

// Public catalog APIs
router.get('/categories', storeController.getCategories);
router.get('/products', storeController.getProducts);
router.get('/products/:id', storeController.getProductById);

// Protected user wishlist & cart APIs
router.get('/wishlist', authenticateToken, storeController.getWishlist);
router.post('/wishlist', authenticateToken, storeController.addToWishlist);
router.delete('/wishlist/:id', authenticateToken, storeController.removeFromWishlist);
router.delete('/wishlist/product/:productId', authenticateToken, storeController.removeFromWishlist);

router.get('/cart', authenticateToken, storeController.getCart);
router.post('/cart/items', authenticateToken, storeController.addToCart);
router.put('/cart/items/:id', authenticateToken, storeController.updateCartItem);
router.delete('/cart/items/:id', authenticateToken, storeController.removeFromCart);

module.exports = router;
