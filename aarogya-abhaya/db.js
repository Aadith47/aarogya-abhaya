require("dotenv").config({ path: require("path").join(__dirname, ".env") });
const { Pool } = require("pg");

const pool = new Pool({
    user: process.env.DB_USER || "postgres",
    host: process.env.DB_HOST || "localhost",
    database: process.env.DB_NAME || "aarogya_abhaya",
    password: process.env.DB_PASSWORD,
    port: parseInt(process.env.DB_PORT) || 5432
});

module.exports = pool;
