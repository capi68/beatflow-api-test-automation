const { Pool } = require('pg');

const pool = new Pool({
  host: process.env.DATABASE_HOST || 'localhost',
  port: parseInt(process.env.DATABASE_PORT || '5432'),
  user: process.env.DATABASE_USER || 'beatadmin',
  password: process.env.DATABASE_PASSWORD || 'beatpass123',
  database: process.env.DATABASE_NAME || 'beatflow',
});

const query = (text, params) => pool.query(text, params);

module.exports = { query, pool };
