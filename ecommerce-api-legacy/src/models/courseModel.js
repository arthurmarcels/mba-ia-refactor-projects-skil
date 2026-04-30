// models/courseModel.js — Course data access layer
const { dbGet, dbAll } = require('../config/database');

class CourseModel {
    static async getActiveById(courseId) {
        return dbGet(
            "SELECT id, title, price, active FROM courses WHERE id = ? AND active = 1",
            [courseId]
        );
    }

    static async getAll() {
        return dbAll("SELECT id, title, price, active FROM courses");
    }
}

module.exports = CourseModel;
