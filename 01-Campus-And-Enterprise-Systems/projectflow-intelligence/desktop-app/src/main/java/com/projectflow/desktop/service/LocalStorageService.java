package com.projectflow.desktop.service;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.File;
import java.sql.*;
import java.util.UUID;

/**
 * Local embedded SQLite database providing seamless offline capability and local caching
 * for the ProjectFlow Windows Desktop Application.
 */
public class LocalStorageService {
    private static final Logger log = LoggerFactory.getLogger(LocalStorageService.class);
    private static final String DB_FILE = "projectflow_desktop.db";
    private final String connectionUrl;

    public LocalStorageService() {
        this.connectionUrl = "jdbc:sqlite:" + DB_FILE;
        initSchema();
    }

    private void initSchema() {
        try (Connection conn = DriverManager.getConnection(connectionUrl);
             Statement stmt = conn.createStatement()) {
            
            // Workspaces cache
            stmt.execute("""
                CREATE TABLE IF NOT EXISTS local_workspaces (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    slug TEXT NOT NULL,
                    description TEXT,
                    created_at TEXT
                );
            """);

            // Projects cache
            stmt.execute("""
                CREATE TABLE IF NOT EXISTS local_projects (
                    id TEXT PRIMARY KEY,
                    workspace_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    code TEXT NOT NULL,
                    description TEXT,
                    status TEXT NOT NULL,
                    health TEXT NOT NULL,
                    target_date TEXT,
                    created_at TEXT
                );
            """);

            // Tasks cache
            stmt.execute("""
                CREATE TABLE IF NOT EXISTS local_tasks (
                    id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    priority TEXT NOT NULL,
                    status_category TEXT NOT NULL,
                    progress_percent INTEGER DEFAULT 0,
                    due_date TEXT,
                    created_at TEXT
                );
            """);

            // Pending offline sync queue
            stmt.execute("""
                CREATE TABLE IF NOT EXISTS pending_sync_queue (
                    id TEXT PRIMARY KEY,
                    operation_type TEXT NOT NULL,
                    entity_type TEXT NOT NULL,
                    entity_id TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
            """);

            // Key-value settings
            stmt.execute("""
                CREATE TABLE IF NOT EXISTS local_settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );
            """);

            log.info("Local SQLite schema initialized at {}", DB_FILE);
        } catch (SQLException e) {
            log.error("Failed to initialize SQLite local storage", e);
        }
    }

    public Connection getConnection() throws SQLException {
        return DriverManager.getConnection(connectionUrl);
    }

    public void setSetting(String key, String value) {
        String sql = "INSERT INTO local_settings(key, value) VALUES(?, ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value";
        try (Connection conn = getConnection();
             PreparedStatement ps = conn.prepareStatement(sql)) {
            ps.setString(1, key);
            ps.setString(2, value);
            ps.executeUpdate();
        } catch (SQLException e) {
            log.error("Error saving setting {}", key, e);
        }
    }

    public String getSetting(String key, String defaultValue) {
        String sql = "SELECT value FROM local_settings WHERE key = ?";
        try (Connection conn = getConnection();
             PreparedStatement ps = conn.prepareStatement(sql)) {
            ps.setString(1, key);
            try (ResultSet rs = ps.executeQuery()) {
                if (rs.next()) {
                    return rs.getString("value");
                }
            }
        } catch (SQLException e) {
            log.error("Error reading setting {}", key, e);
        }
        return defaultValue;
    }
}
