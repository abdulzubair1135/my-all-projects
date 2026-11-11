import pool from '../config/database.js';

export const searchService = {
  async searchListings(filters) {
    const {
      search,
      category,
      minPrice,
      maxPrice,
      city,
      rating,
      sort = 'newest',
      page = 1,
      limit = 20,
      lat,
      lng,
      radius = 10 // km
    } = filters;

    const offset = (Number(page) - 1) * Number(limit);
    const params = [];
    
    // We only select active/published listings that are not soft-deleted
    let query = `
      SELECT l.*, c.name as category_name, li.image_url as listing_primary_image
    `;
    
    // If geo search coordinates are provided, calculate distance
    if (lat && lng) {
      query += `, 
        (6371 * acos(
          cos(radians(?)) * cos(radians(l.latitude)) * cos(radians(l.longitude) - radians(?)) + 
          sin(radians(?)) * sin(radians(l.latitude))
        )) AS distance_km
      `;
      params.push(Number(lat), Number(lng), Number(lat));
    }

    query += `
      FROM listings l
      JOIN categories c ON l.category_id = c.id
      LEFT JOIN listing_images li ON l.id = li.listing_id AND li.is_primary = 1
      WHERE l.status = 'published' AND l.deleted_at IS NULL
    `;

    // Apply Filters
    if (search) {
      query += ' AND (l.title LIKE ? OR l.description LIKE ? OR l.city LIKE ?)';
      const keyword = `%${search}%`;
      params.push(keyword, keyword, keyword);
    }

    if (category) {
      // Allow category ID or category slug
      if (isNaN(category)) {
        query += ' AND c.slug = ?';
      } else {
        query += ' AND l.category_id = ?';
      }
      params.push(category);
    }

    if (minPrice) {
      query += ' AND l.price_per_day >= ?';
      params.push(Number(minPrice));
    }

    if (maxPrice) {
      query += ' AND l.price_per_day <= ?';
      params.push(Number(maxPrice));
    }

    if (city) {
      query += ' AND l.city = ?';
      params.push(city);
    }

    if (rating) {
      query += ' AND l.rating_average >= ?';
      params.push(Number(rating));
    }

    // Geolocation radius constraint
    if (lat && lng && radius) {
      query += `
        HAVING distance_km <= ?
      `;
      params.push(Number(radius));
    }

    // Sorting
    if (sort === 'price_asc') {
      query += ' ORDER BY l.price_per_day ASC';
    } else if (sort === 'price_desc') {
      query += ' ORDER BY l.price_per_day DESC';
    } else if (sort === 'rating') {
      query += ' ORDER BY l.rating_average DESC, l.rating_count DESC';
    } else if (sort === 'popularity') {
      query += ' ORDER BY l.booking_count DESC, l.view_count DESC';
    } else if (sort === 'distance' && lat && lng) {
      query += ' ORDER BY distance_km ASC';
    } else {
      // Default: newest
      query += ' ORDER BY l.id DESC';
    }

    // Pagination
    query += ' LIMIT ? OFFSET ?';
    params.push(Number(limit), Number(offset));

    const [rows] = await pool.query(query, params);

    // Get total count for pagination calculations
    // MySQL count queries with HAVING require a subquery
    let countQuery = '';
    const countParams = [];

    if (lat && lng && radius) {
      // Need same distance calculation for HAVING subquery
      countQuery = `
        SELECT COUNT(*) as total FROM (
          SELECT l.id,
            (6371 * acos(
              cos(radians(?)) * cos(radians(l.latitude)) * cos(radians(l.longitude) - radians(?)) + 
              sin(radians(?)) * sin(radians(l.latitude))
            )) AS distance_km
          FROM listings l
          JOIN categories c ON l.category_id = c.id
          WHERE l.status = 'published' AND l.deleted_at IS NULL
      `;
      countParams.push(Number(lat), Number(lng), Number(lat));

      if (search) {
        countQuery += ' AND (l.title LIKE ? OR l.description LIKE ? OR l.city LIKE ?)';
        const keyword = `%${search}%`;
        countParams.push(keyword, keyword, keyword);
      }
      if (category) {
        if (isNaN(category)) countQuery += ' AND c.slug = ?';
        else countQuery += ' AND l.category_id = ?';
        countParams.push(category);
      }
      if (minPrice) {
        countQuery += ' AND l.price_per_day >= ?';
        countParams.push(Number(minPrice));
      }
      if (maxPrice) {
        countQuery += ' AND l.price_per_day <= ?';
        countParams.push(Number(maxPrice));
      }
      if (city) {
        countQuery += ' AND l.city = ?';
        countParams.push(city);
      }
      if (rating) {
        countQuery += ' AND l.rating_average >= ?';
        countParams.push(Number(rating));
      }
      countQuery += ' HAVING distance_km <= ? ) AS sub';
      countParams.push(Number(radius));
    } else {
      countQuery = `
        SELECT COUNT(*) as total 
        FROM listings l
        JOIN categories c ON l.category_id = c.id
        WHERE l.status = 'published' AND l.deleted_at IS NULL
      `;
      if (search) {
        countQuery += ' AND (l.title LIKE ? OR l.description LIKE ? OR l.city LIKE ?)';
        const keyword = `%${search}%`;
        countParams.push(keyword, keyword, keyword);
      }
      if (category) {
        if (isNaN(category)) countQuery += ' AND c.slug = ?';
        else countQuery += ' AND l.category_id = ?';
        countParams.push(category);
      }
      if (minPrice) {
        countQuery += ' AND l.price_per_day >= ?';
        countParams.push(Number(minPrice));
      }
      if (maxPrice) {
        countQuery += ' AND l.price_per_day <= ?';
        countParams.push(Number(maxPrice));
      }
      if (city) {
        countQuery += ' AND l.city = ?';
        countParams.push(city);
      }
      if (rating) {
        countQuery += ' AND l.rating_average >= ?';
        countParams.push(Number(rating));
      }
    }

    const [[{ total }]] = await pool.query(countQuery, countParams);

    return {
      listings: rows,
      pagination: {
        page: Number(page),
        limit: Number(limit),
        total,
        totalPages: Math.ceil(total / Number(limit))
      }
    };
  }
};
