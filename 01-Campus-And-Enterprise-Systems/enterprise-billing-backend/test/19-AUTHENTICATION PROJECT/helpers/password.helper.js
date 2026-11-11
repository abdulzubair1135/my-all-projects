/**
 * Password Encryption & Comparison Helper using bcrypt
 */

import bcrypt from 'bcrypt';

// Salt rounds factor
const SALT_ROUNDS = 10;

// Plain text password ko hash karna
export const hashPassword = async (plainPassword) => {
  return await bcrypt.hash(plainPassword, SALT_ROUNDS);
};

// Plain text password aur hashed password compare karna
export const comparePassword = async (plainPassword, hashedPassword) => {
  return await bcrypt.compare(plainPassword, hashedPassword);
};
