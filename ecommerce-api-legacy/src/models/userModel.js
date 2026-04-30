// models/userModel.js — User data access layer (fixes C3: God Class decomposition)
const { dbRun, dbGet, dbAll } = require('../config/database');

class UserModel {
    static async getById(userId) {
        return dbGet("SELECT id, name, email FROM users WHERE id = ?", [userId]);
    }

    static async getByEmail(email) {
        return dbGet("SELECT id, name, email, pass FROM users WHERE email = ?", [email]);
    }

    static async create(name, email, passwordHash) {
        const result = await dbRun(
            "INSERT INTO users (name, email, pass) VALUES (?, ?, ?)",
            [name, email, passwordHash]
        );
        return result.lastID;
    }

    static async deleteById(userId) {
        // Delete related enrollments and payments first to avoid orphaned data
        const enrollments = await dbAll(
            "SELECT id FROM enrollments WHERE user_id = ?", [userId]
        );

        for (const enrollment of enrollments) {
            await dbRun("DELETE FROM payments WHERE enrollment_id = ?", [enrollment.id]);
        }

        await dbRun("DELETE FROM enrollments WHERE user_id = ?", [userId]);
        const result = await dbRun("DELETE FROM users WHERE id = ?", [userId]);
        return result.changes;
    }
}

module.exports = UserModel;
