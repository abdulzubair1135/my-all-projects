-- SQL Transaction: BEGIN and COMMIT Statements Practice

-- Setup sample table
CREATE TABLE IF NOT EXISTS bank_accounts (
    id INT PRIMARY KEY,
    name VARCHAR(50),
    balance DECIMAL(10,2)
);

-- Successful Transaction Block
START TRANSACTION; -- Or BEGIN

-- Step 1: Deduct 500 from Account 1
UPDATE bank_accounts 
SET balance = balance - 500 
WHERE id = 1;

-- Step 2: Add 500 to Account 2
UPDATE bank_accounts 
SET balance = balance + 500 
WHERE id = 2;

-- Commit changes permanently to database
COMMIT;
