// config/settings.js — Configuration from environment variables (fixes C1: Hardcoded Secrets)
module.exports = {
    dbPath: process.env.DB_PATH || ':memory:',
    paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY || '',
    smtpUser: process.env.SMTP_USER || '',
    secretKey: process.env.SECRET_KEY || 'dev-key-change-in-production',
    port: parseInt(process.env.PORT, 10) || 3000,
    nodeEnv: process.env.NODE_ENV || 'development'
};
