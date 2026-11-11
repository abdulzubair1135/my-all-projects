START TRANSACTION;

UPDATE accounts

SET balance=balance-1000

WHERE id=1;

UPDATE accounts

SET balance=balance+1000

WHERE id=2;

COMMIT;