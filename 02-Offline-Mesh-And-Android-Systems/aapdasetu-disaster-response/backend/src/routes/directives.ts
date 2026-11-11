import { Router } from 'express';
import { 
  getDirectives, 
  createDirective, 
  updateDirectiveStatus, 
  requestStockShortage, 
  replenishStock 
} from '../controllers/DirectiveController.js';

const router = Router();

router.get('/', getDirectives);
router.post('/', createDirective);
router.patch('/:id/status', updateDirectiveStatus);
router.post('/:id/request-stock', requestStockShortage);
router.patch('/:id/replenish', replenishStock);

export default router;
