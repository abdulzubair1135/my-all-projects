-- SQL Transaction: ROLLBACK Practice

-- Failed Transaction Scenario
START TRANSACTION;

-- Step 1: Deduct 500 from Account 1
UPDATE bank_accounts 
SET balance = balance - 500 
WHERE id = 1;

-- Error occurs (e.g. Account 2 does not exist or negative balance violation)

-- Revert all changes made during this transaction back to initial state
ROLLBACK;
