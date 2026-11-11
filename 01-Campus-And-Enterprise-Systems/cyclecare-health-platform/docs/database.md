# CycleCare Database Schema & Data Dictionary

## Overview
CycleCare utilizes Supabase PostgreSQL with strict relational integrity, foreign key constraints, indexes, and Row-Level Security (RLS) policies.

## Primary Entities

### 1. User & Authentication
- `users`: Core account identity (`id`, `email`, `password_hash`, `role`, `status`, `created_at`).
- `profiles`: User display details (`user_id`, `display_name`, `profile_image`).
- `cycle_settings`: User cycle baseline (`user_id`, `average_cycle_length`, `average_period_length`, `prediction_enabled`).
- `user_sessions`: Refresh token tracking (`user_id`, `refresh_token_hash`, `device_info`, `expires_at`).

### 2. Period & Symptom Tracking
- `period_logs`: Menstrual period entries (`user_id`, `start_date`, `end_date`, `flow`, `notes`).
- `symptoms`: Reference table of symptoms (`id`, `name`, `category`).
- `symptom_logs`: Daily symptom entries (`user_id`, `symptom_id`, `log_date`, `intensity`, `notes`).
- `moods`: Reference table of moods (`id`, `name`, `icon_name`).
- `mood_logs`: Daily mood entries (`user_id`, `mood_id`, `log_date`, `intensity`, `notes`).
- `reminders`: Configured alerts (`user_id`, `type`, `title`, `enabled`, `scheduled_time`, `days_before`).

### 3. Store & E-Commerce
- `categories`: Product categories (`id`, `name`, `description`, `is_active`).
- `products`: Catalog items (`id`, `category_id`, `name`, `description`, `price`, `discount_price`, `stock`, `sku`, `is_active`).
- `product_images`: Additional product imagery (`product_id`, `image_url`, `sort_order`).
- `cart` & `cart_items`: User shopping cart (`user_id`, `product_id`, `quantity`, `unit_price`).
- `wishlist`: Saved products (`user_id`, `product_id`).
- `coupons`: Admin promotional codes (`code`, `discount_type`, `discount_value`, `minimum_order`, `maximum_discount`, `starts_at`, `expires_at`).

### 4. Orders & Payments
- `addresses`: Shipping destinations (`user_id`, `name`, `phone`, `address_line`, `city`, `state`, `pincode`, `type`).
- `orders`: Order header (`id`, `user_id`, `address_id`, `subtotal`, `discount`, `delivery_fee`, `total_amount`, `status`).
- `order_items`: Order line items with price snapshots (`order_id`, `product_id`, `product_name_snapshot`, `unit_price`, `quantity`, `total`).
- `payments`: Server-verified transactions (`order_id`, `gateway`, `gateway_order_id`, `gateway_payment_id`, `amount`, `status`).
- `reviews`: Product reviews by verified buyers (`user_id`, `product_id`, `rating`, `review_text`, `status`).

### 5. Care Kits & Tracking
- `care_kits` & `care_kit_items`: Custom user care kits (`user_id`, `name`, `product_id`, `quantity`).
- `user_product_tracking`: Personal inventory restocking alerts (`user_id`, `product_id`, `quantity_remaining`, `restock_threshold`).

### 6. Event Planning & Wellness
- `user_events`: Overlap tracking for exams/trips (`user_id`, `title`, `event_date`, `type`).
- `wellness_categories` & `wellness_articles`: Educational articles (`title`, `content`, `image_url`, `status`).
- `ai_conversations` & `ai_messages`: Educational wellness chatbot history.
- `audit_logs`: Administrative system activity log (`actor_user_id`, `action`, `entity_type`, `entity_id`, `metadata`).
