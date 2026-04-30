// middlewares/errorHandler.js — Centralized error handling (fixes H4: Duplicated Code, M4: Bare Exceptions)
function errorHandler(err, req, res, _next) {
    const timestamp = new Date().toISOString();
    const statusCode = err.statusCode || 500;
    const message = statusCode === 500 ? 'Internal server error' : err.message;

    // Log the error with context (but never log sensitive data)
    console.error(`[${timestamp}] ${err.name || 'Error'}: ${err.message}`);
    if (statusCode === 500) {
        console.error(err.stack);
    }

    res.status(statusCode).json({ error: message });
}

module.exports = errorHandler;
