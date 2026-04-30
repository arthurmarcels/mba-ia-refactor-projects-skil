// config/database.js — Database initialization with Promise wrappers (fixes H3: Callback Hell foundation)
const sqlite3 = require('sqlite3').verbose();
const settings = require('./settings');

let db;

/**
 * Wraps db.run in a Promise. Returns { lastID, changes }.
 */
function dbRun(sql, params = []) {
    return new Promise((resolve, reject) => {
        db.run(sql, params, function (err) {
            if (err) reject(err);
            else resolve({ lastID: this.lastID, changes: this.changes });
        });
    });
}

/**
 * Wraps db.get in a Promise. Returns a single row or undefined.
 */
function dbGet(sql, params = []) {
    return new Promise((resolve, reject) => {
        db.get(sql, params, (err, row) => {
            if (err) reject(err);
            else resolve(row);
        });
    });
}

/**
 * Wraps db.all in a Promise. Returns an array of rows.
 */
function dbAll(sql, params = []) {
    return new Promise((resolve, reject) => {
        db.all(sql, params, (err, rows) => {
            if (err) reject(err);
            else resolve(rows);
        });
    });
}

/**
 * Initializes the database, creates tables and seeds data.
 * Returns the promise-wrapped DB helpers.
 */
async function initDatabase() {
    return new Promise((resolve, reject) => {
        db = new sqlite3.Database(settings.dbPath, (err) => {
            if (err) return reject(err);

            db.serialize(() => {
                db.run("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, email TEXT, pass TEXT)");
                db.run("CREATE TABLE IF NOT EXISTS courses (id INTEGER PRIMARY KEY, title TEXT, price REAL, active INTEGER)");
                db.run("CREATE TABLE IF NOT EXISTS enrollments (id INTEGER PRIMARY KEY, user_id INTEGER, course_id INTEGER)");
                db.run("CREATE TABLE IF NOT EXISTS payments (id INTEGER PRIMARY KEY, enrollment_id INTEGER, amount REAL, status TEXT)");
                db.run("CREATE TABLE IF NOT EXISTS audit_logs (id INTEGER PRIMARY KEY, action TEXT, created_at DATETIME)");

                db.run("INSERT OR IGNORE INTO users (id, name, email, pass) VALUES (1, 'Leonan', 'leonan@fullcycle.com.br', '$2b$10$placeholder')");
                db.run("INSERT OR IGNORE INTO courses (id, title, price, active) VALUES (1, 'Clean Architecture', 997.00, 1), (2, 'Docker', 497.00, 1)", (err) => {
                    if (err) return reject(err);
                    resolve();
                });
            });
        });
    });
}

/**
 * Returns the raw db instance (for advanced use only).
 */
function getDb() {
    return db;
}

module.exports = { initDatabase, dbRun, dbGet, dbAll, getDb };
