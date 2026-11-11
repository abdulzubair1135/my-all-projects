# ES Modules (`import`/`export`) One-Page Quick Revision Sheet

## Enabling ES Modules in Node.js
Add `"type": "module"` in `package.json`:
```json
{
  "name": "backend-exam",
  "version": "1.0.0",
  "type": "module",
  "main": "server.js"
}
```

---

## Syntax Comparison

| Action | CommonJS (`require`) | ES Modules (`import`/`export`) |
| :--- | :--- | :--- |
| **Package Import** | `const express = require('express');` | `import express from 'express';` |
| **Local File Import** | `const db = require('./config/db');` | `import db from './config/db.js';` *(Must include .js)* |
| **Named Export** | `module.exports = { func };` | `export const func = () => {};` |
| **Default Export** | `module.exports = func;` | `export default func;` |

---

## Key Exam Rule
In ES Modules, **all relative imports MUST explicitly specify the `.js` extension** (e.g. `import db from './config/db.js'`). Missing `.js` causes runtime `ERR_MODULE_NOT_FOUND`!
