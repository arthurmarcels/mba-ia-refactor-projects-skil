// models/auditLogModel.js — Audit log data access layer
const { dbRun } = require('../config/database');

class AuditLogModel {
    static async create(action) {
        const result = await dbRun(
            "INSERT INTO audit_logs (action, created_at) VALUES (?, datetime('now'))",
            [action]
        );
        return result.lastID;
    }
}

module.exports = AuditLogModel;
