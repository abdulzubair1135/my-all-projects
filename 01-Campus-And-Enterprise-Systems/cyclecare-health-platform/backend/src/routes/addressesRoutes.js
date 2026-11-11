const express = require('express');
const router = express.Router();
const addressesController = require('../controllers/addressesController');
const authenticateToken = require('../middleware/auth');

router.use(authenticateToken);

router.get('/', addressesController.getAddresses);
router.post('/', addressesController.addAddress);
router.get('/:id', addressesController.getAddressById);
router.put('/:id', addressesController.updateAddress);
router.delete('/:id', addressesController.deleteAddress);
router.post('/:id/default', addressesController.setDefaultAddress);

module.exports = router;
