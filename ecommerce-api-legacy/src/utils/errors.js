// utils/errors.js — Custom error classes for structured error handling
class AppError extends Error {
    constructor(message, statusCode) {
        super(message);
        this.statusCode = statusCode;
        this.name = this.constructor.name;
    }
}

class NotFoundError extends AppError {
    constructor(message = 'Resource not found') {
        super(message, 404);
    }
}

class BadRequestError extends AppError {
    constructor(message = 'Bad Request') {
        super(message, 400);
    }
}

class UnauthorizedError extends AppError {
    constructor(message = 'Unauthorized') {
        super(message, 401);
    }
}

class PaymentDeniedError extends AppError {
    constructor(message = 'Pagamento recusado') {
        super(message, 400);
    }
}

module.exports = { AppError, NotFoundError, BadRequestError, UnauthorizedError, PaymentDeniedError };
