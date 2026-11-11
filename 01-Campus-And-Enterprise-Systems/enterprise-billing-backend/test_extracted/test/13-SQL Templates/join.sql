-- ===========================================
-- LEFT JOIN
-- ===========================================

SELECT

users.id,

users.name,

roles.name AS role

FROM users

LEFT JOIN roles

ON users.role_id=roles.id;