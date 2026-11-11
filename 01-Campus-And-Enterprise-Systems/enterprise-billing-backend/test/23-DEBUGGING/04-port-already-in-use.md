# 04 - Port Already in Use

## ERROR
`Error: listen EADDRINUSE: address already in use :::5000`

---

## WHY IT HAPPENS
Another instance of Node.js server or another application is already running on port 5000.

---

## HOW TO FIND IT
- Check error code: `EADDRINUSE`.
- The port number listed in message (e.g. `5000`) is occupied.

---

## HOW TO FIX IT
1. **Option A**: Change port in `.env` file to `5001` or `8000`:
```env
PORT=5001
```
2. **Option B**: Kill running process using PowerShell:
```powershell
Get-Process -Id (Get-NetTCPConnection -LocalPort 5000).OwningProcess | Stop-Process -Force
```

---

## COMMON EXAM MISTAKE
Opening a second terminal window and starting `node server.js` without closing the previous background running server process.
