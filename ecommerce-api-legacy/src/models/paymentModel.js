// models/paymentModel.js — Payment data access layer
const { dbRun, dbGet } = require('../config/database');

class PaymentModel {
    static async create(enrollmentId, amount, status) {
        const result = await dbRun(
            "INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)",
            [enrollmentId, amount, status]
        );
        return result.lastID;
    }

    static async getByEnrollmentId(enrollmentId) {
        return dbGet(
            "SELECT id, enrollment_id, amount, status FROM payments WHERE enrollment_id = ?",
            [enrollmentId]
        );
    }
}

module.exports = PaymentModel;
