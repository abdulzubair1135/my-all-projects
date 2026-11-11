# MIDDLEWARE

Middleware ek function hota hai.

Ye Request aur Controller ke beech me execute hota hai.

Flow

Client

↓

Middleware

↓

Controller

↓

Model

↓

Database

↓

Response

-----------------------------------

Middleware ke kaam

✔ Authentication

✔ Validation

✔ Logging

✔ Error Handling

✔ File Upload

✔ Role Checking

-----------------------------------

Middleware me

req

res

next()

hota hai.