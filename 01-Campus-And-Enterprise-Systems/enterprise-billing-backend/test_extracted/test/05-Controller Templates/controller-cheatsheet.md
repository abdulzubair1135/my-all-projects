# CONTROLLER CHEAT SHEET

Controller = Brain

===================================

Controller Ka Kaam

✔ Request Lena

✔ Model Call Karna

✔ Response Dena

✔ Error Handle Karna

===================================

req

↓

Client Data

-----------------------------------

res

↓

Server Response

-----------------------------------

req.body

↓

POST / PUT Data

-----------------------------------

req.params

↓

URL Parameters

-----------------------------------

req.query

↓

Search Filters

Example

/users?page=1

/users?search=Abdul

-----------------------------------

Status Codes

200 = Success

201 = Created

400 = Bad Request

401 = Unauthorized

403 = Forbidden

404 = Not Found

500 = Server Error

-----------------------------------

Always

try{

...

}

catch{

...

}

-----------------------------------

Never Write SQL

Inside Controller

-----------------------------------

Always Call

Model

-----------------------------------

Always Return

JSON