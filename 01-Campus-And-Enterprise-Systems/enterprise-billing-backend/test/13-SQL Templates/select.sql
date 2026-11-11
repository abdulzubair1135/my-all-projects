-- ===========================================
-- SELECT ALL
-- ===========================================

SELECT *

FROM users;

------------------------------------------------

-- SELECT BY ID

SELECT *

FROM users

WHERE id = ?;

------------------------------------------------

-- SELECT SPECIFIC COLUMNS

SELECT

id,

name,

email

FROM users;