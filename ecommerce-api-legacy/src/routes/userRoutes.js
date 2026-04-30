// routes/userRoutes.js — User management endpoints (protected by auth)
const express = require('express');
const router = express.Router();
const UserController = require('../controllers/userController');
const authMiddleware = require('../middlewares/auth');

router.delete('/api/users/:id', authMiddleware, async (req, res, next) => {
    try {
        const result = await UserController.deleteUser(req.params.id);
        res.json(result);
    } catch (err) {
        next(err);
    }
});

module.exports = router;
