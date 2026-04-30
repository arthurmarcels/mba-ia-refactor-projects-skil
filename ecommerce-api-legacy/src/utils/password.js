// utils/password.js — Secure password hashing (fixes H1: Insecure Password Storage)
const bcrypt = require('bcrypt');

const SALT_ROUNDS = 10;

async function hashPassword(password) {
    return bcrypt.hash(password, SALT_ROUNDS);
}

async function verifyPassword(password, hash) {
    return bcrypt.compare(password, hash);
}

module.exports = { hashPassword, verifyPassword };
