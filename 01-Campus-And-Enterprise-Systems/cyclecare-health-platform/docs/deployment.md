# CycleCare Deployment Guide

## Overview
This guide provides deployment instructions for the Node.js API server on Render, the Supabase PostgreSQL database, and building the Android release APK.

## 1. Supabase Database Setup
1. Log in to [Supabase](https://supabase.com).
2. Create a new PostgreSQL project named `cyclecare-prod`.
3. Open the **SQL Editor** in Supabase.
4. Execute `database/migrations/001_initial_schema.sql`.
5. Execute `database/migrations/002_rls_policies_and_seed.sql`.
6. Copy the **DB Connection String**, **Project URL**, and **Anon Key** from Project Settings -> API.

## 2. Render Node.js Backend Deployment
1. Log in to [Render](https://render.com).
2. Click **New +** -> **Web Service**.
3. Connect your GitHub repository.
4. Set Build Command: `cd backend && npm install`
5. Set Start Command: `cd backend && npm start`
6. Add the following Environment Variables in Render:
   - `PORT`: `10000`
   - `NODE_ENV`: `production`
   - `JWT_SECRET`: `<secure_jwt_secret>`
   - `JWT_REFRESH_SECRET`: `<secure_jwt_refresh_secret>`
   - `SUPABASE_URL`: `https://your-supabase-project.supabase.co`
   - `SUPABASE_ANON_KEY`: `<your_supabase_anon_key>`
   - `SUPABASE_SERVICE_ROLE_KEY`: `<your_supabase_service_role_key>`
   - `RAZORPAY_KEY_ID`: `<your_razorpay_key_id>`
   - `RAZORPAY_KEY_SECRET`: `<your_razorpay_key_secret>`
   - `ADMIN_SECRET_KEY`: `<secure_admin_creation_key>`
7. Deploy the Web Service.

## 3. Android Release Build
1. Open the `android` folder in Android Studio.
2. In `android/app/build.gradle`, set `buildConfigField "String", "BASE_URL", "\"https://cyclecare-api.onrender.com/api/v1/\""`.
3. Select **Build** -> **Generate Signed Bundle / APK**.
4. Choose **APK**, select release keystore, and click **Finish**.
5. The release APK is generated in `android/app/release/app-release.apk`.
