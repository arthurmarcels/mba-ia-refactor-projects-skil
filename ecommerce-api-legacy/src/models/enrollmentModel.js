// models/enrollmentModel.js — Enrollment data access layer
const { dbRun, dbAll } = require('../config/database');

class EnrollmentModel {
    static async create(userId, courseId) {
        const result = await dbRun(
            "INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)",
            [userId, courseId]
        );
        return result.lastID;
    }

    static async getByCourseId(courseId) {
        return dbAll(
            "SELECT id, user_id, course_id FROM enrollments WHERE course_id = ?",
            [courseId]
        );
    }
}

module.exports = EnrollmentModel;
