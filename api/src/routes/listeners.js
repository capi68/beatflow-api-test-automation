const express = require('express');
const bcrypt = require('bcryptjs');
const { query } = require('../utils/db');
const { requireAuth, generateToken } = require('../middleware/auth');

const router = express.Router();

/**
 * @swagger
 * /listeners:
 *   get:
 *     summary: List all active listeners
 *     tags: [Listeners]
 *     security:
 *       - bearerAuth: []
 *     responses:
 *       200:
 *         description: List of active listeners
 */
router.get('/', requireAuth, async (req, res) => {
  try {
    const result = await query(
      'SELECT id, username, email, first_name, last_name, date_of_birth, country, is_active, created_at, updated_at FROM listeners WHERE is_active = TRUE ORDER BY username ASC'
    );
    res.json(result.rows);
  } catch (err) {
    console.error('Error listing listeners:', err);
    res.status(500).json({ message: 'Internal server error' });
  }
});

/**
 * @swagger
 * /listeners:
 *   post:
 *     summary: Register a new listener
 *     tags: [Listeners]
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required: [username, email, password, first_name, last_name]
 *             properties:
 *               username:
 *                 type: string
 *               email:
 *                 type: string
 *               password:
 *                 type: string
 *               first_name:
 *                 type: string
 *               last_name:
 *                 type: string
 *               date_of_birth:
 *                 type: string
 *                 format: date
 *               country:
 *                 type: string
 *     responses:
 *       201:
 *         description: Listener created
 *       400:
 *         description: Validation error
 *       409:
 *         description: Email or username already exists
 */
router.post('/', async (req, res) => {
  try {
    const data = req.body || {};

    const required = ['username', 'email', 'password', 'first_name', 'last_name'];
    const missing = required.filter(f => !data[f] && data[f] !== 0);
    if (missing.length > 0) {
      return res.status(400).json({ message: `Missing required fields: ${missing.join(', ')}` });
    }

    // Validate types
    for (const field of required) {
      if (typeof data[field] !== 'string') {
        return res.status(400).json({ message: `Field '${field}' must be a string` });
      }
    }

    // Validate non-empty
    for (const field of required) {
      if (data[field].trim() === '') {
        return res.status(400).json({ message: `Field '${field}' cannot be empty` });
      }
    }

    // Validate username format (alphanumeric + underscore, 3-50 chars)
    if (!/^[a-zA-Z0-9_]{3,50}$/.test(data.username)) {
      return res.status(400).json({ message: 'Username must be 3-50 characters, alphanumeric and underscores only' });
    }

    // Validate email format
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(data.email)) {
      return res.status(400).json({ message: 'Invalid email format' });
    }

    // Validate password
    if (data.password.length < 8) {
      return res.status(400).json({ message: 'Password must be at least 8 characters' });
    }

    // Validate date_of_birth if provided
    if (data.date_of_birth) {
      const dob = new Date(data.date_of_birth);
      if (isNaN(dob.getTime())) {
        return res.status(400).json({ message: 'Invalid date_of_birth format. Use YYYY-MM-DD' });
      }
      // Must be at least 13 years old
      const today = new Date();
      const age = today.getFullYear() - dob.getFullYear();
      if (age < 13) {
        return res.status(400).json({ message: 'Listener must be at least 13 years old' });
      }
    }

    // Check duplicate email
    const existingEmail = await query('SELECT id FROM listeners WHERE email = $1', [data.email]);
    if (existingEmail.rows.length > 0) {
      return res.status(409).json({ message: 'Email already registered' });
    }

    // Check duplicate username
    const existingUsername = await query('SELECT id FROM listeners WHERE username = $1', [data.username]);
    if (existingUsername.rows.length > 0) {
      return res.status(409).json({ message: 'Username already taken' });
    }

    const passwordHash = await bcrypt.hash(data.password, 10);

    const result = await query(
      `INSERT INTO listeners (username, email, password_hash, first_name, last_name, date_of_birth, country)
       VALUES ($1, $2, $3, $4, $5, $6, $7) RETURNING id, username, email, first_name, last_name, date_of_birth, country, is_active, created_at, updated_at`,
      [data.username, data.email, passwordHash, data.first_name, data.last_name, data.date_of_birth || null, data.country || null]
    );

    res.status(201).json(result.rows[0]);
  } catch (err) {
    console.error('Error creating listener:', err);
    res.status(500).json({ message: 'Internal server error' });
  }
});

/**
 * @swagger
 * /listeners/{id}:
 *   get:
 *     summary: Get listener by ID
 *     tags: [Listeners]
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: path
 *         name: id
 *         required: true
 *         schema:
 *           type: integer
 *     responses:
 *       200:
 *         description: Listener found
 *       404:
 *         description: Listener not found
 */
router.get('/:id', requireAuth, async (req, res) => {
  try {
    const { id } = req.params;
    const result = await query(
      'SELECT id, username, email, first_name, last_name, date_of_birth, country, is_active, created_at, updated_at FROM listeners WHERE id = $1',
      [id]
    );
    if (result.rows.length === 0) {
      return res.status(404).json({ message: 'Listener not found' });
    }
    res.json(result.rows[0]);
  } catch (err) {
    console.error('Error getting listener:', err);
    res.status(500).json({ message: 'Internal server error' });
  }
});

/**
 * @swagger
 * /listeners/{id}:
 *   put:
 *     summary: Update listener fields
 *     tags: [Listeners]
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: path
 *         name: id
 *         required: true
 *         schema:
 *           type: integer
 *     requestBody:
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             properties:
 *               first_name:
 *                 type: string
 *               last_name:
 *                 type: string
 *               country:
 *                 type: string
 *     responses:
 *       200:
 *         description: Listener updated
 *       404:
 *         description: Listener not found
 */
router.put('/:id', requireAuth, async (req, res) => {
  try {
    const { id } = req.params;
    const data = req.body || {};

    if (Object.keys(data).length === 0) {
      return res.status(400).json({ message: 'No data provided' });
    }

    const current = await query('SELECT * FROM listeners WHERE id = $1', [id]);
    if (current.rows.length === 0) {
      return res.status(404).json({ message: 'Listener not found' });
    }

    const allowedFields = ['first_name', 'last_name', 'country'];
    const setClauses = [];
    const values = [];
    let paramIndex = 1;

    for (const key of allowedFields) {
      if (data[key] !== undefined) {
        setClauses.push(`${key} = $${paramIndex}`);
        values.push(data[key]);
        paramIndex++;
      }
    }

    if (setClauses.length === 0) {
      return res.status(400).json({ message: 'No valid fields to update' });
    }

    setClauses.push('updated_at = NOW()');
    values.push(id);

    const result = await query(
      `UPDATE listeners SET ${setClauses.join(', ')} WHERE id = $${paramIndex} RETURNING id, username, email, first_name, last_name, date_of_birth, country, is_active, created_at, updated_at`,
      values
    );

    res.json(result.rows[0]);
  } catch (err) {
    console.error('Error updating listener:', err);
    res.status(500).json({ message: 'Internal server error' });
  }
});

/**
 * @swagger
 * /listeners/{id}:
 *   delete:
 *     summary: Delete listener (fails if has active subscription)
 *     tags: [Listeners]
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: path
 *         name: id
 *         required: true
 *         schema:
 *           type: integer
 *     responses:
 *       200:
 *         description: Listener deleted
 *       404:
 *         description: Listener not found
 *       409:
 *         description: Listener has active subscription
 */
router.delete('/:id', requireAuth, async (req, res) => {
  try {
    const { id } = req.params;

    const current = await query('SELECT * FROM listeners WHERE id = $1', [id]);
    if (current.rows.length === 0) {
      return res.status(404).json({ message: 'Listener not found' });
    }

    // Check for active subscription
    const subs = await query(
      "SELECT COUNT(*) as count FROM subscriptions WHERE listener_id = $1 AND status IN ('active', 'paused')",
      [id]
    );
    if (parseInt(subs.rows[0].count) > 0) {
      return res.status(409).json({ message: 'Cannot delete listener with active or paused subscription' });
    }

    // Cascade delete: playlists → playlist_tracks, streams, subscriptions
    const playlists = await query('SELECT id FROM playlists WHERE listener_id = $1', [id]);
    for (const pl of playlists.rows) {
      await query('DELETE FROM playlist_tracks WHERE playlist_id = $1', [pl.id]);
    }
    await query('DELETE FROM playlists WHERE listener_id = $1', [id]);
    await query('DELETE FROM streams WHERE listener_id = $1', [id]);
    await query('DELETE FROM subscriptions WHERE listener_id = $1', [id]);
    await query('DELETE FROM listeners WHERE id = $1', [id]);

    res.json({ message: 'Listener deleted successfully' });
  } catch (err) {
    console.error('Error deleting listener:', err);
    res.status(500).json({ message: 'Internal server error' });
  }
});

/**
 * @swagger
 * /listeners/login:
 *   post:
 *     summary: Authenticate listener and get JWT token
 *     tags: [Listeners]
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required: [email, password]
 *             properties:
 *               email:
 *                 type: string
 *               password:
 *                 type: string
 *     responses:
 *       200:
 *         description: Login successful
 *       400:
 *         description: Missing fields
 *       401:
 *         description: Invalid credentials
 */
router.post('/login', async (req, res) => {
  try {
    const { email, password } = req.body || {};

    if (!email || !password) {
      return res.status(400).json({ message: 'Email and password are required' });
    }

    const result = await query('SELECT * FROM listeners WHERE email = $1 AND is_active = TRUE', [email]);
    if (result.rows.length === 0) {
      return res.status(401).json({ message: 'Invalid credentials' });
    }

    const listener = result.rows[0];
    const valid = await bcrypt.compare(password, listener.password_hash);
    if (!valid) {
      return res.status(401).json({ message: 'Invalid credentials' });
    }

    const token = generateToken({ id: listener.id, email: listener.email, role: 'listener' });

    res.json({ message: 'Login successful', token, listener_id: listener.id });
  } catch (err) {
    console.error('Error logging in listener:', err);
    res.status(500).json({ message: 'Internal server error' });
  }
});

module.exports = router;
