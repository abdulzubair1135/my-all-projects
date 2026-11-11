# AI Agent Protocol Specification (v1.0)

All communication between the LLM and the Autonomous Web-Agent IDE is structured as strict JSON blocks.

---

## 1. Top-Level Response Schema

```json
{
  "version": "1.0",
  "type": "agent_response",
  "summary": "Short explanation of the actions taken in this turn",
  "actions": [
    {
      "type": "write_file",
      "path": "server/index.js",
      "content": "const express = require('express');\n..."
    },
    {
      "type": "run_command",
      "command": "npm install express"
    }
  ],
  "next_task": "Implement database schema and models",
  "requires_user": false
}
```

---

## 2. Action Specifications

### `write_file`
Creates or overwrites a file inside the project workspace.
```json
{
  "type": "write_file",
  "path": "src/App.jsx",
  "content": "import React from 'react';\nexport default function App() {}"
}
```

### `edit_file`
Modifies an existing file with hash conflict validation.
```json
{
  "type": "edit_file",
  "path": "package.json",
  "expected_hash": "a1b2c3d4...",
  "content": "..."
}
```

### `delete_file`
Safely deletes a file or directory inside the workspace.
```json
{
  "type": "delete_file",
  "path": "src/old_component.jsx"
}
```

### `mkdir`
Creates a directory.
```json
{
  "type": "mkdir",
  "path": "server/routes"
}
```

### `run_command`
Executes an approved shell command with streaming logs and timeout control.
```json
{
  "type": "run_command",
  "command": "npm test",
  "timeout": 120
}
```

### `start_server`
Starts a long-running background development server.
```json
{
  "type": "start_server",
  "name": "backend-api",
  "command": "node server/index.js",
  "port": 4000
}
```

### `stop_server`
Stops a managed background process.
```json
{
  "type": "stop_server",
  "name": "backend-api"
}
```

### `git_checkpoint`
Creates a Git commit snapshot.
```json
{
  "type": "git_checkpoint",
  "message": "Implement authentication middleware"
}
```

### `finish`
Signals completion of the task plan after project verification.
```json
{
  "type": "finish",
  "summary": "Project successfully built and verified.",
  "verification_passed": true
}
```
