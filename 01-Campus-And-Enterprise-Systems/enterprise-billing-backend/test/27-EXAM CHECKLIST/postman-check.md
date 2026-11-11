# Postman Verification Checklist

## API Endpoint Testing Checklist

- [ ] **Request Method**: Verify HTTP Method matches controller route definition (`GET`, `POST`, `PUT`, `DELETE`).
- [ ] **Header Content-Type**: Ensure `Content-Type: application/json` is specified for POST/PUT requests.
- [ ] **Valid JSON Body**: Check that body keys are wrapped in double quotes and there are no trailing commas.
- [ ] **Authorization Header**: For protected endpoints, verify `Authorization: Bearer <token>` is present.
- [ ] **Test Register (`POST /api/auth/register`)**: Expect status code 201 Created.
- [ ] **Test Login (`POST /api/auth/login`)**: Verify JWT token string is returned.
- [ ] **Test Read All (`GET /api/products`)**: Expect status code 200 OK with array data.
- [ ] **Test Read One (`GET /api/products/:id`)**: Expect status code 200 OK for valid ID, 404 for nonexistent ID.
- [ ] **Test Validation Error**: Send empty required fields, verify 400 Bad Request with error list.
- [ ] **Test Invalid Token**: Send corrupt JWT token, verify 401 Unauthorized response.
