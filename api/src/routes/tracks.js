const express = require('express');
const { query } = require('../utils/db');
const { requireAuth } = require('../middleware/auth');

const router = express.Router();

/**
 * @swagger
 * /tracks:
 *   get:
 *     summary: List tracks (filterable by album_id, genre_id, is_available)
 *     tags: [Tracks]
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: query
 *         name: album_id
 *         schema:
 *           type: integer
 *       - in: query
 *         name: genre_id
 *         schema:
 *           type: integer
 *       - in: query
 *         name: is_available
 *         schema:
 *           type: boolean
 *     responses:
 *       200:
 *         description: List of tracks
 */
router.get('/', requireAuth, async (req, res) => {
  try {
    let sql = 'SELECT * FROM tracks WHERE 1=1';
    const params = [];
    let paramIndex = 1;

    if (req.query.album_id) {
      sql += ` AND album_id = $${paramIndex}`;
      params.push(req.query.album_id);
      paramIndex++;
    }
    if (req.query.genre_id) {
      sql += ` AND genre_id = $${paramIndex}`;
      params.push(req.query.genre_id);
      paramIndex++;
    }
    if (req.query.is_available !== undefined) {
      sql += ` AND is_available = $${paramIndex}`;
      params.push(req.query.is_available === 'true');
      paramIndex++;
    }
    sql += ' ORDER BY album_id, track_number ASC';

    const result = await query(sql, params);
    res.json(result.rows);
  } catch (err) {
    console.error('Error listing tracks:', err);
    res.status(500).json({ message: 'Internal server error' });
  }
});

/**
 * @swagger
 * /tracks:
 *   post:
 *     summary: Create a new track
 *     tags: [Tracks]
 *     security:
 *       - bearerAuth: []
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required: [album_id, title, duration_seconds, track_number]
 *             properties:
 *               album_id:
 *                 type: integer
 *               title:
 *                 type: string
 *               duration_seconds:
 *                 type: integer
 *                 example: 240
 *               track_number:
 *                 type: integer
 *                 example: 1
 *               genre_id:
 *                 type: integer
 *               is_explicit:
 *                 type: boolean
 *     responses:
 *       201:
 *         description: Track created
 *       400:
 *         description: Validation error
 *       404:
 *         description: Album or genre not found
 *       409:
 *         description: Track number already exists in album
 */
router.post('/', requireAuth, async (req, res) => {
  try {
    const data = req.body || {};

    const required = ['album_id', 'title', 'duration_seconds', 'track_number'];
    const missing = required.filter(f => !data[f] && data[f] !== 0);
    if (missing.length > 0) {
      return res.status(400).json({ message: `Missing required fields: ${missing.join(', ')}` });
    }

    // Validate title
    if (typeof data.title !== 'string' || data.title.trim() === '') {
      return res.status(400).json({ message: 'title must be a non-empty string' });
    }
    if (data.title.length > 200) {
      return res.status(400).json({ message: 'title must be at most 200 characters' });
    }

    // Validate duration_seconds (30 to 3600 — 30 sec min, 1 hour max)
    if (!Number.isInteger(data.duration_seconds) || data.duration_seconds < 30 || data.duration_seconds > 3600) {
      return res.status(400).json({ message: 'duration_seconds must be between 30 and 3600' });
    }

    // Validate track_number (1 to 50)
    if (!Number.isInteger(data.track_number) || data.track_number < 1 || data.track_number > 50) {
      return res.status(400).json({ message: 'track_number must be between 1 and 50' });
    }

    // Validate album exists
    const album = await query('SELECT * FROM albums WHERE id = $1', [data.album_id]);
    if (album.rows.length === 0) {
      return res.status(404).json({ message: 'Album not found' });
    }

    // Cannot add tracks to an archived album
    if (album.rows[0].status === 'archived') {
      return res.status(400).json({ message: 'Cannot add tracks to an archived album' });
    }

    // Validate genre_id if provided
    if (data.genre_id !== undefined && data.genre_id !== null) {
      const genre = await query('SELECT id FROM genres WHERE id = $1', [data.genre_id]);
      if (genre.rows.length === 0) {
        return res.status(404).json({ message: 'Genre not found' });
      }
    }

    // Check duplicate track_number in same album
    const existing = await query(
      'SELECT id FROM tracks WHERE album_id = $1 AND track_number = $2',
      [data.album_id, data.track_number]
    );
    if (existing.rows.length > 0) {
      return res.status(409).json({ message: `Track number ${data.track_number} already exists in this album` });
    }

    const result = await query(
      `INSERT INTO tracks (album_id, title, duration_seconds, track_number, genre_id, is_explicit)
       VALUES ($1, $2, $3, $4, $5, $6) RETURNING *`,
      [data.album_id, data.title.trim(), data.duration_seconds, data.track_number, data.genre_id || null, data.is_explicit || false]
    );

    res.status(201).json(result.rows[0]);
  } catch (err) {
    console.error('Error creating track:', err);
    res.status(500).json({ message: 'Internal server error' });
  }
});

/**
 * @swagger
 * /tracks/{id}:
 *   get:
 *     summary: Get track by ID
 *     tags: [Tracks]
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
 *         description: Track found
 *       404:
 *         description: Track not found
 */
router.get('/:id', requireAuth, async (req, res) => {
  try {
    const { id } = req.params;
    const result = await query('SELECT * FROM tracks WHERE id = $1', [id]);
    if (result.rows.length === 0) {
      return res.status(404).json({ message: 'Track not found' });
    }
    res.json(result.rows[0]);
  } catch (err) {
    console.error('Error getting track:', err);
    res.status(500).json({ message: 'Internal server error' });
  }
});

/**
 * @swagger
 * /tracks/{id}:
 *   put:
 *     summary: Update track fields
 *     tags: [Tracks]
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
 *               title:
 *                 type: string
 *               duration_seconds:
 *                 type: integer
 *               track_number:
 *                 type: integer
 *               genre_id:
 *                 type: integer
 *               is_available:
 *                 type: boolean
 *               is_explicit:
 *                 type: boolean
 *     responses:
 *       200:
 *         description: Track updated
 *       400:
 *         description: Validation error
 *       404:
 *         description: Track not found
 *       409:
 *         description: Track number conflict
 */
router.put('/:id', requireAuth, async (req, res) => {
  try {
    const { id } = req.params;
    const data = req.body || {};

    if (Object.keys(data).length === 0) {
      return res.status(400).json({ message: 'No data provided' });
    }

    const current = await query('SELECT * FROM tracks WHERE id = $1', [id]);
    if (current.rows.length === 0) {
      return res.status(404).json({ message: 'Track not found' });
    }
    const track = current.rows[0];

    // Validate duration_seconds
    if (data.duration_seconds !== undefined) {
      if (!Number.isInteger(data.duration_seconds) || data.duration_seconds < 30 || data.duration_seconds > 3600) {
        return res.status(400).json({ message: 'duration_seconds must be between 30 and 3600' });
      }
    }

    // Validate track_number
    if (data.track_number !== undefined) {
      if (!Number.isInteger(data.track_number) || data.track_number < 1 || data.track_number > 50) {
        return res.status(400).json({ message: 'track_number must be between 1 and 50' });
      }
      // Check conflict
      const conflict = await query(
        'SELECT id FROM tracks WHERE album_id = $1 AND track_number = $2 AND id != $3',
        [track.album_id, data.track_number, id]
      );
      if (conflict.rows.length > 0) {
        return res.status(409).json({ message: `Track number ${data.track_number} already exists in this album` });
      }
    }

    // Validate genre_id
    if (data.genre_id !== undefined && data.genre_id !== null) {
      const genre = await query('SELECT id FROM genres WHERE id = $1', [data.genre_id]);
      if (genre.rows.length === 0) {
        return res.status(404).json({ message: 'Genre not found' });
      }
    }

    // Cannot set is_available=true if track has a revoked license blocking it
    // (handled at license level, not here)

    const allowedFields = ['title', 'duration_seconds', 'track_number', 'genre_id', 'is_available', 'is_explicit'];
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
      `UPDATE tracks SET ${setClauses.join(', ')} WHERE id = $${paramIndex} RETURNING *`,
      values
    );

    res.json(result.rows[0]);
  } catch (err) {
    console.error('Error updating track:', err);
    res.status(500).json({ message: 'Internal server error' });
  }
});

/**
 * @swagger
 * /tracks/{id}:
 *   delete:
 *     summary: Delete track (fails if has active licenses or pending royalties)
 *     tags: [Tracks]
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
 *         description: Track deleted
 *       404:
 *         description: Track not found
 *       409:
 *         description: Cannot delete track with active constraints
 */
router.delete('/:id', requireAuth, async (req, res) => {
  try {
    const { id } = req.params;

    const current = await query('SELECT * FROM tracks WHERE id = $1', [id]);
    if (current.rows.length === 0) {
      return res.status(404).json({ message: 'Track not found' });
    }

    // Check active licenses
    const licenses = await query(
      "SELECT COUNT(*) as count FROM licenses WHERE track_id = $1 AND status IN ('requested', 'approved', 'active')",
      [id]
    );
    if (parseInt(licenses.rows[0].count) > 0) {
      return res.status(409).json({ message: 'Cannot delete track with active licenses' });
    }

    // Check pending royalties
    const royalties = await query(
      "SELECT COUNT(*) as count FROM royalties WHERE track_id = $1 AND status IN ('pending', 'processing')",
      [id]
    );
    if (parseInt(royalties.rows[0].count) > 0) {
      return res.status(409).json({ message: 'Cannot delete track with pending royalties' });
    }

    // Cascade delete
    await query('DELETE FROM playlist_tracks WHERE track_id = $1', [id]);
    await query('DELETE FROM streams WHERE track_id = $1', [id]);
    await query('DELETE FROM royalties WHERE track_id = $1', [id]);
    await query('DELETE FROM licenses WHERE track_id = $1', [id]);
    await query('DELETE FROM tracks WHERE id = $1', [id]);

    res.json({ message: 'Track deleted successfully' });
  } catch (err) {
    console.error('Error deleting track:', err);
    res.status(500).json({ message: 'Internal server error' });
  }
});

module.exports = router;
