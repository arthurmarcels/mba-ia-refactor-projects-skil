// middlewares/auth.js — JWT authentication middleware (fixes C4: Missing Authentication)
const jwt = require('jsonwebtoken');
const settings = require('../config/settings');

function authMiddleware(req, res, next) {
    const authHeader = req.headers.authorization;
    const token = authHeader && authHeader.startsWith('Bearer ')
        ? authHeader.slice(7)
        : null;

    if (!token) {
        return res.status(401).json({ error: 'Token is missing' });
    }

    try {
        const decoded = jwt.verify(token, settings.secretKey);
        req.userId = decoded.userId;
        next();
    } catch (err) {
        return res.status(401).json({ error: 'Invalid or expired token' });
    }
}

module.exports = authMiddleware;
