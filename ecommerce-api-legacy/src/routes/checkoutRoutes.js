// routes/checkoutRoutes.js — Checkout endpoint (thin route, delegates to controller)
const express = require('express');
const router = express.Router();
const CheckoutController = require('../controllers/checkoutController');

router.post('/api/checkout', async (req, res, next) => {
    try {
        // Map legacy field names to descriptive names (fixes L2: Poor Variable Naming)
        const data = {
            username: req.body.usr,
            email: req.body.eml,
            password: req.body.pwd,
            courseId: req.body.c_id,
            cardNumber: req.body.card
        };

        CheckoutController.validateInput(data);
        const result = await CheckoutController.processCheckout(data);
        res.status(200).json(result);
    } catch (err) {
        next(err);
    }
});

module.exports = router;
