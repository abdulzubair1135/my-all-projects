const { z } = require('zod');

// Schema for device registration
const registerDeviceSchema = z.object({
  device_id: z.string().min(3).max(128).regex(/^[a-zA-Z0-9_-]+$/, 'Device ID must be alphanumeric with underscores or dashes'),
  device_name: z.string().min(1).max(100).default('Android Device'),
  admin_key: z.string().min(8)
});

// Schema for notifications in text sync
const notificationItemSchema = z.object({
  client_event_id: z.string().min(1).max(128).optional(),
  app_name: z.string().min(1).max(256),
  title: z.string().nullable().optional(),
  content: z.string().nullable().optional(),
  timestamp: z.number().int().positive()
});

// Schema for telecom logs
const telecomItemSchema = z.object({
  client_event_id: z.string().min(1).max(128).optional(),
  type: z.enum(['sms', 'call']),
  party: z.string().nullable().optional(),
  body: z.string().nullable().optional(),
  duration: z.number().int().nonnegative().nullable().optional(),
  timestamp: z.number().int().positive()
});

// Schema for sensor logs
const sensorItemSchema = z.object({
  client_event_id: z.string().min(1).max(128).optional(),
  type: z.string().min(1).max(64),
  payload_json: z.string().min(2),
  timestamp: z.number().int().positive()
});

// Full text batch schema
const syncTextBatchSchema = z.object({
  notifications: z.array(notificationItemSchema).default([]),
  telecom_logs: z.array(telecomItemSchema).default([]),
  sensor_logs: z.array(sensorItemSchema).default([])
});

// Date query schema (YYYY-MM-DD)
const dateQuerySchema = z.object({
  date: z.string().regex(/^\d{4}-\d{2}-\d{2}$/, 'Date must be formatted as YYYY-MM-DD')
});

// Date range query schema
const dateRangeQuerySchema = z.object({
  from: z.string().regex(/^\d{4}-\d{2}-\d{2}$/, 'From date must be formatted as YYYY-MM-DD'),
  to: z.string().regex(/^\d{4}-\d{2}-\d{2}$/, 'To date must be formatted as YYYY-MM-DD')
});

module.exports = {
  registerDeviceSchema,
  notificationItemSchema,
  telecomItemSchema,
  sensorItemSchema,
  syncTextBatchSchema,
  dateQuerySchema,
  dateRangeQuerySchema
};
