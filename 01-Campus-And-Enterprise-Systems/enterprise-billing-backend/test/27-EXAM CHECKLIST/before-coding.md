# Before Coding Checklist

## Setup & Environment Checklist

- [ ] **Node & NPM Installed**: Verify terminal responds to `node -v` and `npm -v`.
- [ ] **MySQL Service Running**: Start MySQL via XAMPP Control Panel or Windows Services.
- [ ] **Project Directory Created**: Navigate to designated project folder (`cd c:\backend\test\`).
- [ ] **Package.json Initialized**: Execute `npm init -y`.
- [ ] **ES Modules Enabled**: Verify `"type": "module"` is added in `package.json`.
- [ ] **Dependencies Installed**: Install `express mysql2 dotenv bcrypt jsonwebtoken express-validator cors`.
- [ ] **Environment File (.env) Configured**: Set `PORT`, `DB_HOST`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`, `JWT_SECRET`.
- [ ] **Database & Tables Created**: Run SQL script in MySQL CLI/phpMyAdmin to create tables with PK/FK constraints.
- [ ] **Sample Data Inserted**: Insert 2-3 dummy records for immediate endpoint testing.
