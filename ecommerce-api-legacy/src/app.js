// app.js — Entry point / Composition root (fixes C3: God Class decomposition)
const express = require('express');
const settings = require('./config/settings');
const { initDatabase } = require('./config/database');
const checkoutRoutes = require('./routes/checkoutRoutes');
const reportRoutes = require('./routes/reportRoutes');
const userRoutes = require('./routes/userRoutes');
const errorHandler = require('./middlewares/errorHandler');

const app = express();

// Middleware
app.use(express.json());

// Routes
app.use(checkoutRoutes);
app.use(reportRoutes);
app.use(userRoutes);

// Centralized error handler (must be registered AFTER routes)
app.use(errorHandler);

// Initialize database and start server
initDatabase()
    .then(() => {
        app.listen(settings.port, () => {
            console.log(`Frankenstein LMS rodando na porta ${settings.port}...`);
        });
    })
    .catch((err) => {
        console.error('Failed to initialize database:', err);
        process.exit(1);
    });

module.exports = app;
