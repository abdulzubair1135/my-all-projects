import { Response } from 'express';

export interface ApiResponse<T = any> {
  success: boolean;
  message?: string;
  data?: T;
  errors?: any;
  meta?: any;
}

export class ResponseUtil {
  static success<T>(res: Response, data: T, message?: string, statusCode = 200, meta?: any): Response {
    const payload: ApiResponse<T> = {
      success: true,
      message,
      data,
      meta
    };
    return res.status(statusCode).json(payload);
  }

  static error(res: Response, message: string, statusCode = 400, errors?: any): Response {
    const payload: ApiResponse = {
      success: false,
      message,
      errors
    };
    return res.status(statusCode).json(payload);
  }
}
