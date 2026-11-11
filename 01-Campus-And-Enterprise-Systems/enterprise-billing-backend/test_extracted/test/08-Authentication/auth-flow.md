REGISTER

↓

Password

↓

bcrypt.hash()

↓

Database

------------------------------------

LOGIN

↓

Email

↓

Database

↓

bcrypt.compare()

↓

jwt.sign()

↓

Token

↓

Client

------------------------------------

NEXT REQUEST

↓

Authorization

Bearer Token

↓

jwt.verify()

↓

Controller