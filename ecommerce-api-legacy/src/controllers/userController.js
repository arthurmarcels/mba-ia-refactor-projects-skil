// controllers/userController.js — User management logic
const UserModel = require('../models/userModel');
const { BadRequestError, NotFoundError } = require('../utils/errors');

class UserController {
    /**
     * Deletes a user and cascades to enrollments/payments.
     */
    static async deleteUser(userId) {
        if (!userId || isNaN(Number(userId))) {
            throw new BadRequestError('Invalid user ID');
        }

        const user = await UserModel.getById(Number(userId));
        if (!user) {
            throw new NotFoundError('Usuário não encontrado');
        }

        await UserModel.deleteById(Number(userId));

        return { msg: 'Usuário deletado com sucesso. Matrículas e pagamentos removidos.' };
    }
}

module.exports = UserController;
