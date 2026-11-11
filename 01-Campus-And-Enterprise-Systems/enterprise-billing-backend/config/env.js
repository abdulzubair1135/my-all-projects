import dotenv from "dotenv";
dotenv.config();
export default {
    PORT: process.env.PORT,
    DB_HOST: process.env.HOST,
    DB_USER: process.env.USER,
    DB_PASSWORD: process.env.PASSWORD,
    DB_NAME: process.env.NAME,
    JWT_SECRET: process.env.JWT_SECRET
};