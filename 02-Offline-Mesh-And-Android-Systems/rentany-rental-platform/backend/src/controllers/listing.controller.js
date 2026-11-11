import { listingRepository } from '../repositories/listing.repository.js';
import { searchService } from '../services/search.service.js';
import { AppError } from '../middleware/error.middleware.js';
import crypto from 'crypto';

export const listingController = {
  async getListings(req, res, next) {
    try {
      const results = await searchService.searchListings(req.query);
      res.status(200).json({
        success: true,
        data: results.listings,
        pagination: results.pagination
      });
    } catch (err) {
      next(err);
    }
  },

  async getListingDetails(req, res, next) {
    try {
      const id = Number(req.params.id);
      
      // Get authenticated user ID if present from token (optional auth endpoints)
      const authedUserId = req.user ? req.user.id : null;
      
      const listing = await listingRepository.findById(id, authedUserId);
      if (!listing) {
        throw new AppError('Rental listing not found.', 404);
      }

      // Increment view count asynchronously
      listingRepository.incrementViewCount(id).catch(err => console.error('Increment view failed:', err.message));

      res.status(200).json({
        success: true,
        data: listing
      });
    } catch (err) {
      next(err);
    }
  },

  async createListing(req, res, next) {
    try {
      const {
        category_id, title, description, price_per_day, price_per_hour, refundable_deposit,
        quantity, condition, location_address, city, state, country, postal_code,
        latitude, longitude, delivery_available, delivery_fee, pickup_available,
        instant_booking, minimum_rental_days, maximum_rental_days, attributes, images
      } = req.body;

      // Generate slug from title
      const slug = title.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '');

      const uuid = crypto.randomUUID();
      const listingData = {
        uuid,
        owner_id: req.user.id,
        category_id,
        title,
        slug,
        description,
        price_per_day,
        price_per_hour,
        refundable_deposit,
        quantity,
        condition,
        location_address,
        city,
        state,
        country,
        postal_code,
        latitude,
        longitude,
        delivery_available,
        delivery_fee,
        pickup_available,
        instant_booking,
        minimum_rental_days,
        maximum_rental_days,
        status: 'published' // Default to active for development ease
      };

      const listingId = await listingRepository.create(listingData);

      // Save custom attributes
      if (attributes && Array.isArray(attributes)) {
        await listingRepository.saveAttributes(listingId, attributes);
      }

      // Save images list
      if (images && Array.isArray(images)) {
        for (let i = 0; i < images.length; i++) {
          await listingRepository.addImage(listingId, images[i], i, i === 0 ? 1 : 0);
        }
      }

      const listing = await listingRepository.findById(listingId, req.user.id);

      res.status(201).json({
        success: true,
        message: 'Listing published successfully',
        data: listing
      });
    } catch (err) {
      next(err);
    }
  },

  async updateListing(req, res, next) {
    try {
      const id = Number(req.params.id);
      
      // 1. Check if listing exists and verify owner
      const listing = await listingRepository.findById(id);
      if (!listing) {
        throw new AppError('Listing not found.', 404);
      }

      // Authorize owner
      if (listing.owner_id !== req.user.id && req.user.role !== 'admin' && req.user.role !== 'super_admin') {
        throw new AppError('You are not authorized to update this listing.', 403);
      }

      // Generate slug if title is updated
      if (req.body.title) {
        req.body.slug = req.body.title.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '');
      }

      await listingRepository.update(id, req.body);

      // Update attributes
      if (req.body.attributes && Array.isArray(req.body.attributes)) {
        await listingRepository.saveAttributes(id, req.body.attributes);
      }

      const updated = await listingRepository.findById(id, req.user.id);

      res.status(200).json({
        success: true,
        message: 'Listing updated successfully',
        data: updated
      });
    } catch (err) {
      next(err);
    }
  },

  async deleteListing(req, res, next) {
    try {
      const id = Number(req.params.id);
      
      const listing = await listingRepository.findById(id);
      if (!listing) {
        throw new AppError('Listing not found.', 404);
      }

      // Authorize owner
      if (listing.owner_id !== req.user.id && req.user.role !== 'admin' && req.user.role !== 'super_admin') {
        throw new AppError('You are not authorized to delete this listing.', 403);
      }

      // Soft delete
      await listingRepository.softDelete(id);

      res.status(200).json({
        success: true,
        message: 'Listing archived/deleted successfully'
      });
    } catch (err) {
      next(err);
    }
  },

  async uploadListingImages(req, res, next) {
    try {
      const id = Number(req.params.id);

      const listing = await listingRepository.findById(id);
      if (!listing) {
        throw new AppError('Listing not found.', 404);
      }

      // Authorize owner
      if (listing.owner_id !== req.user.id) {
        throw new AppError('Unauthorized access.', 403);
      }

      if (!req.files || req.files.length === 0) {
        throw new AppError('Please select at least one image file to upload.', 400);
      }

      // Save each uploaded image to Cloudinary in parallel
      const { uploadToCloudinary } = await import('../middleware/upload.middleware.js');
      const startOrder = listing.images.length;
      
      const uploadPromises = req.files.map(async (file, index) => {
        const result = await uploadToCloudinary(file.buffer);
        const fileUrl = result.secure_url;
        const isPrimary = (startOrder + index === 0) ? 1 : 0;
        await listingRepository.addImage(id, fileUrl, startOrder + index, isPrimary);
      });
      
      await Promise.all(uploadPromises);

      const updated = await listingRepository.findById(id, req.user.id);

      res.status(200).json({
        success: true,
        message: 'Images uploaded successfully',
        data: updated.images
      });
    } catch (err) {
      next(err);
    }
  },

  async deleteListingImage(req, res, next) {
    try {
      const id = Number(req.params.id); // listingId
      const imageId = Number(req.params.imageId);

      const listing = await listingRepository.findById(id);
      if (!listing) {
        throw new AppError('Listing not found.', 404);
      }

      // Authorize owner
      if (listing.owner_id !== req.user.id) {
        throw new AppError('Unauthorized access.', 403);
      }

      const success = await listingRepository.deleteImage(id, imageId);
      if (!success) {
        throw new AppError('Image not found or already deleted.', 404);
      }

      res.status(200).json({
        success: true,
        message: 'Listing image deleted successfully'
      });
    } catch (err) {
      next(err);
    }
  },

  async updateListingStatus(req, res, next) {
    try {
      const id = Number(req.params.id);
      const { status } = req.body;

      const listing = await listingRepository.findById(id);
      if (!listing) {
        throw new AppError('Listing not found.', 404);
      }

      // Authorize owner
      if (listing.owner_id !== req.user.id && req.user.role !== 'admin' && req.user.role !== 'super_admin') {
        throw new AppError('Unauthorized access.', 403);
      }

      const allowedStatuses = ['draft', 'published', 'paused', 'archived'];
      if (!allowedStatuses.includes(status)) {
        throw new AppError('Invalid status value.', 400);
      }

      await listingRepository.update(id, { status });

      res.status(200).json({
        success: true,
        message: `Listing status updated to ${status}`
      });
    } catch (err) {
      next(err);
    }
  },

  async getNearby(req, res, next) {
    try {
      const { lat, lng, radius } = req.query;
      if (!lat || !lng) {
        throw new AppError('Latitude (lat) and longitude (lng) are required parameters.', 400);
      }

      const results = await searchService.searchListings({
        lat, lng, radius, sort: 'distance', limit: 50
      });

      // Privacy protection rule: never expose the exact physical addresses on public nearby lists
      const sanitized = results.listings.map(l => {
        const item = { ...l };
        delete item.location_address;
        delete item.postal_code;
        return item;
      });

      res.status(200).json({
        success: true,
        data: sanitized
      });
    } catch (err) {
      next(err);
    }
  }
};
