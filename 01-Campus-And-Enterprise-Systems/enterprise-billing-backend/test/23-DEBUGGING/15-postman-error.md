# 15 - Postman Common Request Errors

## ERROR
`Could not get response`, `ECONNREFUSED`, or `400 Bad Request` in Postman client.

---

## WHY IT HAPPENS
1. Node server is not running on target machine.
2. Sent body in `x-www-form-urlencoded` or `Text` format instead of selecting `raw` -> `JSON`.
3. Malformed JSON body in Postman (missing quotes around keys or trailing commas).

---

## HOW TO FIND IT
- Postman status bar displays `Could not get any response` or red underline in body editor.

---

## HOW TO FIX IT
1. Ensure Node server is running on `http://localhost:5000`.
2. Select Body tab -> raw -> JSON.
3. Validate JSON format:
```json
{
  "name": "Sample Product",
  "price": 299.99
}
```
*(Notice double quotes around key names and string values!)*

---

## COMMON EXAM MISTAKE
Adding a trailing comma after the last property in Postman JSON body:
```json
{
  "name": "Sample Product",  <-- WRONG: Trailing comma causes JSON parse error!
}
```
