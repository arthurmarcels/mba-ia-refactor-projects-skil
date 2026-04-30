// controllers/checkoutController.js — Checkout business logic (fixes H2, H3: extracted from God Class, async/await)
const CourseModel = require('../models/courseModel');
const UserModel = require('../models/userModel');
const EnrollmentModel = require('../models/enrollmentModel');
const PaymentModel = require('../models/paymentModel');
const AuditLogModel = require('../models/auditLogModel');
const { hashPassword } = require('../utils/password');
const { NotFoundError, BadRequestError, PaymentDeniedError } = require('../utils/errors');

const VISA_PREFIX = '4';

class CheckoutController {
    /**
     * Validates checkout input data.
     * @throws {BadRequestError} if required fields are missing
     */
    static validateInput(data) {
        const { username, email, courseId, cardNumber } = data;

        if (!username || !email || !courseId || !cardNumber) {
            throw new BadRequestError('Bad Request');
        }

        if (typeof email !== 'string' || !email.includes('@')) {
            throw new BadRequestError('Invalid email format');
        }

        if (typeof cardNumber !== 'string' || cardNumber.length < 13) {
            throw new BadRequestError('Invalid card number');
        }
    }

    /**
     * Processes a checkout: finds/creates user, processes payment, creates enrollment.
     */
    static async processCheckout(data) {
        const { username, email, password, courseId, cardNumber } = data;

        // 1. Validate the course exists and is active
        const course = await CourseModel.getActiveById(courseId);
        if (!course) {
            throw new NotFoundError('Curso não encontrado');
        }

        // 2. Find or create user
        let user = await UserModel.getByEmail(email);
        let userId;

        if (!user) {
            const passwordHash = await hashPassword(password || 'default-change-me');
            userId = await UserModel.create(username, email, passwordHash);
        } else {
            userId = user.id;
        }

        // 3. Process payment (simulate gateway)
        const paymentStatus = cardNumber.startsWith(VISA_PREFIX) ? 'PAID' : 'DENIED';

        if (paymentStatus === 'DENIED') {
            throw new PaymentDeniedError('Pagamento recusado');
        }

        // 4. Create enrollment
        const enrollmentId = await EnrollmentModel.create(userId, courseId);

        // 5. Record payment
        await PaymentModel.create(enrollmentId, course.price, paymentStatus);

        // 6. Audit log
        await AuditLogModel.create(`Checkout curso ${courseId} por ${userId}`);

        return { msg: 'Sucesso', enrollment_id: enrollmentId };
    }
}

module.exports = CheckoutController;
