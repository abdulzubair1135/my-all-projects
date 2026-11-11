# Architecture Overview

## System Architecture Diagram

```mermaid
graph TD
    subgraph Clients["Clients Layer"]
        AdminPanel["Admin Web Console<br/>(React 18 + Vite + TS)"]
        DesktopApp["Windows Desktop Manager<br/>(JavaFX 21 + SQLite)"]
        AndroidApp["Native Android Mobile<br/>(Java + Room + WorkManager)"]
    end

    subgraph Edge["Network & Gateway Layer"]
        HTTP["HTTP / JSON REST APIs<br/>(Stateless JWT + RBAC)"]
    end

    subgraph Backend["Application Server Layer"]
        SpringCore["Spring Boot 3.3.4 Application"]
        Controllers["REST Controllers (/api/v1/*)"]
        Services["Domain Services"]
        Security["JwtAuthenticationFilter & SecurityConfig"]
    end

    subgraph Core["Shared Core Module"]
        RiskEngine["DeterministicRiskEngine<br/>(6 Rules)"]
        SchedEngine["WhatIfSchedulingEngine<br/>(Topological Propagation)"]
        DepValidator["DependencyValidator<br/>(DAG Cycle Detection)"]
        DomainModels["Core Domain Models"]
    end

    subgraph Persistence["Persistence & Database Layer"]
        Flyway["Flyway Schema Migrations<br/>(V1__init_schema.sql)"]
        PostgreSQL["PostgreSQL 15+ / Supabase<br/>(With H2-PG Mode Local Fallback)"]
    end

    AdminPanel -->|Fetch /api/v1/*| Controllers
    DesktopApp -->|HTTP Client / Local SQLite| Controllers
    AndroidApp -->|Retrofit / Room SQLite| Controllers
    Controllers --> Security
    Security --> Services
    Services --> Core
    DesktopApp --> Core
    AndroidApp --> Core
    Services --> Persistence
```

---

## Architectural Principles

1. **Shared Domain Logic**: The deterministic engines (`DeterministicRiskEngine`, `WhatIfSchedulingEngine`, `DependencyValidator`) reside in `:shared-core`, shared directly between backend, desktop, and mobile targets without logic drift.
2. **Tenant Isolation**: All database tables enforce strict workspace partitioning with composite indices on `(workspace_id, ...)` and repository checks preventing cross-tenant leakage.
3. **Offline-First Persistence**: Both Android (Room) and Desktop (SQLite JDBC) cache domain records locally, queue write operations when disconnected, and synchronize via the `SyncService` when network connectivity is established.
4. **Stateless Security**: Spring Security enforces stateless JWT token authentication with role-based method security (`@PreAuthorize("hasAnyRole(...)")`).
5. **Database Independence**: The persistence layer uses standard ANSI SQL and PostgreSQL features supported by Supabase, with automatic fallback to H2 in PostgreSQL mode for zero-configuration local development and unit testing.
