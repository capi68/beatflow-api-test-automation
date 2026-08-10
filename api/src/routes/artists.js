const express = require('express');
const bcrypt = require('bcryptjs');
const { query } = require('../utils/db');
const { requireAuth, generateToken } = require('../middleware/auth');

const router = express.Router();

/**
 * @swagger
 * /artists:
 *   get:
 *     summary: List all active artists
 *     tags: [Artists]
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: query
 *         name: genre_id
 *         schema:
 *           type: integer
 *         description: Filter by genre
 *     responses:
 *       200:
 *         description: List of active artists
 */
router.get('/', requireAuth, async (req, res) => {
  try {
    let sql = 'SELECT id, stage_name, first_name, last_name, email, genre_id, bio, country, total_earnings, is_active, created_at, updated_at FROM artists WHERE is_active = TRUE';
    const params = [];
    let paramIndex = 1;

    if (req.query.genre_id) {
      sql += ` AND genre_id = $${paramIndex}`;
      params.push(req.query.genre_id);
      paramIndex++;
    }
    sql += ' ORDER BY stage_name ASC';

    const result = await query(sql, params);
    const rows = result.rows.map(r => ({
      ...r,
      total_earnings: parseFloat(r.total_earnings),
    }));
    res.json(rows);
  } catch (err) {
    console.error('Error listing artists:', err);
    res.status(500).json({ message: 'Internal server error' });
  }
});

/**
 * @swagger
 * /artists:
 *   post:
 *     summary: Register a new artist
 *     tags: [Artists]
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required: [stage_name, first_name, last_name, email, password]
 *             properties:
 *               stage_name:
 *                 type: string
 *               first_name:
 *                 type: string
 *               last_name:
 *                 type: string
 *               email:
 *                 type: string
 *               password:
 *                 type: string
 *               genre_id:
 *                 type: integer
 *               bio:
 *                 type: string
 *               country:
 *                 type: string
 *     responses:
 *       201:
 *         description: Artist created
 *       400:
 *         description: Validation error
 *       409:
 *         description: Email already exists
 */
router.post('/', async (req, res) => {
  try {
    const data = req.body || {};

    // Required fields
    const required = ['stage_name', 'first_name', 'last_name', 'email', 'password'];
    const missing = required.filter(f => !data[f] && data[f] !== 0);
    if (missing.length > 0) {
      return res.status(400).json({ message: `Missing required fields: ${missing.join(', ')}` });
    }

    // Validate types (all required must be strings)
    for (const field of required) {
      if (typeof data[field] !== 'string') {
        return res.status(400).json({ message: `Field '${field}' must be a string` });
      }
    }

    // Validate non-empty after trim
    for (const field of required) {
      if (data[field].trim() === '') {
        return res.status(400).json({ message: `Field '${field}' cannot be empty` });
      }
    }

    // Validate email format
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(data.email)) {
      return res.status(400).json({ message: 'Invalid email format' });
    }

    // Validate password length
    if (data.password.length < 8) {
      return res.status(400).json({ message: 'Password must be at least 8 characters' });
    }

    // Validate stage_name length
    if (data.stage_name.length > 100) {
      return res.status(400).json({ message: 'stage_name must be at most 100 characters' });
    }

    // Validate bio length if provided
    if (data.bio && data.bio.length > 500) {
      return res.status(400).json({ message: 'bio must be at most 500 characters' });
    }

    // Validate genre_id if provided
    if (data.genre_id !== undefined && data.genre_id !== null) {
      if (!Number.isInteger(data.genre_id) || data.genre_id < 1) {
        return res.status(400).json({ message: 'genre_id must be a positive integer' });
      }
      const genre = await query('SELECT id FROM genres WHERE id = $1', [data.genre_id]);
      if (genre.rows.length === 0) {
        return res.status(404).json({ message: 'Genre not found' });
      }
    }

    // Check duplicate email
    const existing = await query('SELECT id FROM artists WHERE email = $1', [data.email]);
    if (existing.rows.length > 0) {
      return res.status(409).json({ message: 'Email already registered' });
    }

    // Hash password
    const passwordHash = await bcrypt.hash(data.password, 10);

    const result = await query(
      `INSERT INTO artists (stage_name, first_name, last_name, email, password_hash, genre_id, bio, country)
       VALUES ($1, $2, $3, $4, $5, $6, $7, $8) RETURNING *`,
      [data.stage_name, data.first_name, data.last_name, data.email, passwordHash, data.genre_id || null, data.bio || null, data.country || null]
    );

    const artist = result.rows[0];
    delete artist.password_hash;
    artist.total_earnings = parseFloat(artist.total_earnings);

    res.status(201).json(artist);
  } catch (err) {
    console.error('Error creating artist:', err);
    res.status(500).json({ message: 'Internal server error' });
  }
});

/**
 * @swagger
 * /artists/{id}:
 *   get:
 *     summary: Get artist by ID
 *     tags: [Artists]
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
 *         description: Artist found
 *       404:
 *         description: Artist not found
 */
router.get('/:id', requireAuth, async (req, res) => {
  try {
    const { id } = req.params;
    const result = await query(
      'SELECT id, stage_name, first_name, last_name, email, genre_id, bio, country, total_earnings, is_active, created_at, updated_at FROM artists WHERE id = $1',
      [id]
    );
    if (result.rows.length === 0) {
      return res.status(404).json({ message: 'Artist not found' });
    }
    const artist = result.rows[0];
    artist.total_earnings = parseFloat(artist.total_earnings);
    res.json(artist);
  } catch (err) {
    console.error('Error getting artist:', err);
    res.status(500).json({ message: 'Internal server error' });
  }
});

/**
 * @swagger
 * /artists/{id}:
 *   put:
 *     summary: Update artist fields
 *     tags: [Artists]
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
 *               stage_name:
 *                 type: string
 *               first_name:
 *                 type: string
 *               last_name:
 *                 type: string
 *               genre_id:
 *                 type: integer
 *               bio:
 *                 type: string
 *               country:
 *                 type: string
 *     responses:
 *       200:
 *         description: Artist updated
 *       404:
 *         description: Artist not found
 */
router.put('/:id', requireAuth, async (req, res) => {
  try {
    const { id } = req.params;
    const data = req.body || {};

    if (Object.keys(data).length === 0) {
      return res.status(400).json({ message: 'No data provided' });
    }

    // Check artist exists
    const current = await query('SELECT * FROM artists WHERE id = $1', [id]);
    if (current.rows.length === 0) {
      return res.status(404).json({ message: 'Artist not found' });
    }

    // Validate bio length
    if (data.bio !== undefined && data.bio.length > 500) {
      return res.status(400).json({ message: 'bio must be at most 500 characters' });
    }

    // Validate genre_id if provided
    if (data.genre_id !== undefined && data.genre_id !== null) {
      if (!Number.isInteger(data.genre_id) || data.genre_id < 1) {
        return res.status(400).json({ message: 'genre_id must be a positive integer' });
      }
      const genre = await query('SELECT id FROM genres WHERE id = $1', [data.genre_id]);
      if (genre.rows.length === 0) {
        return res.status(404).json({ message: 'Genre not found' });
      }
    }

    const allowedFields = ['stage_name', 'first_name', 'last_name', 'genre_id', 'bio', 'country'];
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
      `UPDATE artists SET ${setClauses.join(', ')} WHERE id = $${paramIndex} RETURNING id, stage_name, first_name, last_name, email, genre_id, bio, country, total_earnings, is_active, created_at, updated_at`,
      values
    );

    const artist = result.rows[0];
    artist.total_earnings = parseFloat(artist.total_earnings);
    res.json(artist);
  } catch (err) {
    console.error('Error updating artist:', err);
    res.status(500).json({ message: 'Internal server error' });
  }
});

/**
 * @swagger
 * /artists/{id}:
 *   delete:
 *     summary: Delete artist (fails if has published albums)
 *     tags: [Artists]
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
 *         description: Artist deleted
 *       404:
 *         description: Artist not found
 *       409:
 *         description: Artist has published albums
 */
router.delete('/:id', requireAuth, async (req, res) => {
  try {
    const { id } = req.params;

    const current = await query('SELECT * FROM artists WHERE id = $1', [id]);
    if (current.rows.length === 0) {
      return res.status(404).json({ message: 'Artist not found' });
    }

    // Check for published albums
    const albums = await query("SELECT COUNT(*) as count FROM albums WHERE artist_id = $1 AND status = 'published'", [id]);
    if (parseInt(albums.rows[0].count) > 0) {
      return res.status(409).json({ message: 'Cannot delete artist with published albums' });
    }

    // Check for pending royalties
    const royalties = await query("SELECT COUNT(*) as count FROM royalties WHERE artist_id = $1 AND status IN ('pending', 'processing')", [id]);
    if (parseInt(royalties.rows[0].count) > 0) {
      return res.status(409).json({ message: 'Cannot delete artist with pending royalties' });
    }

    // Cascade delete: draft/archived albums → tracks → playlist_tracks, streams, royalties, licenses
    const artistAlbums = await query('SELECT id FROM albums WHERE artist_id = $1', [id]);
    for (const album of artistAlbums.rows) {
      const tracks = await query('SELECT id FROM tracks WHERE album_id = $1', [album.id]);
      for (const track of tracks.rows) {
        await query('DELETE FROM playlist_tracks WHERE track_id = $1', [track.id]);
        await query('DELETE FROM streams WHERE track_id = $1', [track.id]);
        await query('DELETE FROM royalties WHERE track_id = $1', [track.id]);
        await query('DELETE FROM licenses WHERE track_id = $1', [track.id]);
      }
      await query('DELETE FROM tracks WHERE album_id = $1', [album.id]);
    }
    await query('DELETE FROM albums WHERE artist_id = $1', [id]);
    await query('DELETE FROM artists WHERE id = $1', [id]);

    res.json({ message: 'Artist deleted successfully' });
  } catch (err) {
    console.error('Error deleting artist:', err);
    res.status(500).json({ message: 'Internal server error' });
  }
});

/**
 * @swagger
 * /artists/login:
 *   post:
 *     summary: Authenticate artist and get JWT token
 *     tags: [Artists]
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

    const result = await query('SELECT * FROM artists WHERE email = $1 AND is_active = TRUE', [email]);
    if (result.rows.length === 0) {
      return res.status(401).json({ message: 'Invalid credentials' });
    }

    const artist = result.rows[0];
    const valid = await bcrypt.compare(password, artist.password_hash);
    if (!valid) {
      return res.status(401).json({ message: 'Invalid credentials' });
    }

    const token = generateToken({ id: artist.id, email: artist.email, role: 'artist' });

    res.json({ message: 'Login successful', token, artist_id: artist.id });
  } catch (err) {
    console.error('Error logging in artist:', err);
    res.status(500).json({ message: 'Internal server error' });
  }
});

module.exports = router;
