# HTTP Headers Guide for Backend Developers

## 1. What are HTTP Headers?
HTTP Headers are key-value pairs sent in both requests and responses to convey metadata about the payload, client, authentication status, caching, and server configuration.

---

## 2. Important Request Headers

| Header Name | Description | Example Value |
|-------------|-------------|---------------|
| `Content-Type` | Media type of the body sent to server | `application/json` |
| `Authorization` | Credentials for authenticating the client | `Bearer eyJhbGci...` |
| `Accept` | Media types the client can handle | `application/json` |
| `User-Agent` | Information about the client browser/tool | `PostmanRuntime/7.29.0` |
| `Host` | Domain name of the target server | `localhost:5000` |

---

## 3. Important Response Headers

| Header Name | Description | Example Value |
|-------------|-------------|---------------|
| `Content-Type` | Format of returned data | `application/json; charset=utf-8` |
| `Access-Control-Allow-Origin` | CORS header specifying permitted origins | `*` or `http://localhost:3000` |
| `Set-Cookie` | Sends cookies to the browser | `token=xyz; HttpOnly; Path=/` |
| `Cache-Control` | Directives for caching mechanisms | `no-cache, no-store` |

---

## 4. Reading and Setting Headers in Express.js

### Reading Request Headers:
```js
app.get('/api/profile', (req, res) => {
  const authHeader = req.headers['authorization']; // Case-insensitive key
  const contentType = req.get('content-type');     // Express helper method

  console.log("Auth Header:", authHeader);
  console.log("Content-Type:", contentType);
});
```

### Setting Custom Response Headers:
```js
app.get('/api/data', (req, res) => {
  res.setHeader('X-Powered-By', 'BCA-Backend-App');
  res.setHeader('Cache-Control', 'no-cache');
  res.status(200).json({ success: true, message: "Headers updated" });
});
```

---

## 5. Exam Tip Questions
- **Q**: Which header is used to send JWT Bearer Tokens?
  - **A**: `Authorization: Bearer <token_string>`
- **Q**: Why is `Content-Type: application/json` required when sending JSON in POST body?
  - **A**: It informs Express's `express.json()` middleware to parse the raw body string as JSON into `req.body`.
