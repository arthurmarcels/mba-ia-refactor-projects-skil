// routes/reportRoutes.js — Financial report endpoint (protected by auth)
const express = require('express');
const router = express.Router();
const ReportController = require('../controllers/reportController');
const authMiddleware = require('../middlewares/auth');

router.get('/api/admin/financial-report', authMiddleware, async (req, res, next) => {
    try {
        const report = await ReportController.getFinancialReport();
        res.json(report);
    } catch (err) {
        next(err);
    }
});

module.exports = router;
