// controllers/reportController.js — Financial report logic (fixes M1: N+1 Queries with JOIN)
const { dbAll } = require('../config/database');

class ReportController {
    /**
     * Generates financial report using a single JOIN query instead of N+1 nested loops.
     * Fixes M1: N+1 Query Pattern.
     */
    static async getFinancialReport() {
        // Single JOIN query replaces the nested forEach + individual queries pattern
        const rows = await dbAll(`
            SELECT 
                c.id AS course_id,
                c.title AS course_title,
                u.name AS student_name,
                p.amount AS paid_amount,
                p.status AS payment_status
            FROM courses c
            LEFT JOIN enrollments e ON e.course_id = c.id
            LEFT JOIN users u ON u.id = e.user_id
            LEFT JOIN payments p ON p.enrollment_id = e.id
            ORDER BY c.id
        `);

        // Aggregate results by course
        const courseMap = new Map();

        for (const row of rows) {
            if (!courseMap.has(row.course_id)) {
                courseMap.set(row.course_id, {
                    course: row.course_title,
                    revenue: 0,
                    students: []
                });
            }

            const courseData = courseMap.get(row.course_id);

            // Only add student data if there is an enrollment (LEFT JOIN may produce nulls)
            if (row.student_name) {
                if (row.payment_status === 'PAID') {
                    courseData.revenue += row.paid_amount || 0;
                }

                courseData.students.push({
                    student: row.student_name,
                    paid: row.paid_amount || 0
                });
            }
        }

        return Array.from(courseMap.values());
    }
}

module.exports = ReportController;
