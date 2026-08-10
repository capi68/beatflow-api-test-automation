const express = require('express');
const { query } = require('../utils/db');
const { requireAuth } = require('../middleware/auth');

const router = express.Router();

/**
 * @swagger
 * /playlists:
 *   get:
 *     summary: List playlists (filterable by listener_id, is_public)
 *     tags: [Playlists]
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: query
 *         name: listener_id
 *         schema:
 *           type: integer
 *       - in: query
 *         name: is_public
 *         schema:
 *           type: boolean
 *     responses:
 *       200:
 *         description: List of playlists
 */
router.get('/', requireAuth, async (req, res) => {
  try {
    let sql = 'SELECT * FROM playlists WHERE 1=1';
    const params = [];
    let paramIndex = 1;

    if (req.query.listener_id) {
      sql += ` AND listener_id = $${paramIndex}`;
      params.push(req.query.listener_id);
      paramIndex++;
    }
    if (req.query.is_public !== undefined) {
      sql += ` AND is_public = $${paramIndex}`;
      params.push(req.query.is_public === 'true');
      paramIndex++;
    }
    sql += ' ORDER BY created_at DESC';

    const result = await query(sql, params);
    res.json(result.rows);
  } catch (err) {
    console.error('Error listing playlists:', err);
    res.status(500).json({ message: 'Internal server error' });
  }
});

/**
 * @swagger
 * /playlists:
 *   post:
 *     summary: Create a new playlist
 *     tags: [Playlists]
 *     security:
 *       - bearerAuth: []
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required: [listener_id, name]
 *             properties:
 *               listener_id:
 *                 type: integer
 *               name:
 *                 type: string
 *               description:
 *                 type: string
 *               is_public:
 *                 type: boolean
 *     responses:
 *       201:
 *         description: Playlist created
 *       400:
 *         description: Validation error
 *       404:
 *         description: Listener not found
 */
router.post('/', requireAuth, async (req, res) => {
  try {
    const data = req.body || {};

    const required = ['listener_id', 'name'];
    const missing = required.filter(f => !data[f] && data[f] !== 0);
    if (missing.length > 0) {
      return res.status(400).json({ message: `Missing required fields: ${missing.join(', ')}` });
    }

    // Validate name
    if (typeof data.name !== 'string' || data.name.trim() === '') {
      return res.status(400).json({ message: 'name must be a non-empty string' });
    }
    if (data.name.length > 200) {
      return res.status(400).json({ message: 'name must be at most 200 characters' });
    }

    // Validate description
    if (data.description && data.description.length > 500) {
      return res.status(400).json({ message: 'description must be at most 500 characters' });
    }

    // Validate listener exists
    const listener = await query('SELECT id FROM listeners WHERE id = $1 AND is_active = TRUE', [data.listener_id]);
    if (listener.rows.length === 0) {
      return res.status(404).json({ message: 'Listener not found or inactive' });
    }

    // Max 50 playlists per listener
    const countResult = await query('SELECT COUNT(*) as count FROM playlists WHERE listener_id = $1', [data.listener_id]);
    if (parseInt(countResult.rows[0].count) >= 50) {
      return res.status(400).json({ message: 'Listener has reached the maximum of 50 playlists' });
    }

    const result = await query(
      `INSERT INTO playlists (listener_id, name, description, is_public)
       VALUES ($1, $2, $3, $4) RETURNING *`,
      [data.listener_id, data.name.trim(), data.description || null, data.is_public || false]
    );

    res.status(201).json(result.rows[0]);
  } catch (err) {
    console.error('Error creating playlist:', err);
    res.status(500).json({ message: 'Internal server error' });
  }
});

/**
 * @swagger
 * /playlists/{id}:
 *   get:
 *     summary: Get playlist by ID (includes tracks)
 *     tags: [Playlists]
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
 *         description: Playlist found
 *       404:
 *         description: Playlist not found
 */
router.get('/:id', requireAuth, async (req, res) => {
  try {
    const { id } = req.params;
    const result = await query('SELECT * FROM playlists WHERE id = $1', [id]);
    if (result.rows.length === 0) {
      return res.status(404).json({ message: 'Playlist not found' });
    }

    // Include tracks
    const tracks = await query(
      `SELECT pt.id, pt.track_id, pt.position, pt.added_at, t.title, t.duration_seconds, t.album_id
       FROM playlist_tracks pt
       JOIN tracks t ON pt.track_id = t.id
       WHERE pt.playlist_id = $1
       ORDER BY pt.position ASC`,
      [id]
    );

    res.json({ ...result.rows[0], tracks: tracks.rows });
  } catch (err) {
    console.error('Error getting playlist:', err);
    res.status(500).json({ message: 'Internal server error' });
  }
});

/**
 * @swagger
 * /playlists/{id}:
 *   put:
 *     summary: Update playlist fields
 *     tags: [Playlists]
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
 *               name:
 *                 type: string
 *               description:
 *                 type: string
 *               is_public:
 *                 type: boolean
 *     responses:
 *       200:
 *         description: Playlist updated
 *       404:
 *         description: Playlist not found
 */
router.put('/:id', requireAuth, async (req, res) => {
  try {
    const { id } = req.params;
    const data = req.body || {};

    if (Object.keys(data).length === 0) {
      return res.status(400).json({ message: 'No data provided' });
    }

    const current = await query('SELECT * FROM playlists WHERE id = $1', [id]);
    if (current.rows.length === 0) {
      return res.status(404).json({ message: 'Playlist not found' });
    }

    // Validate name length
    if (data.name !== undefined && data.name.length > 200) {
      return res.status(400).json({ message: 'name must be at most 200 characters' });
    }

    const allowedFields = ['name', 'description', 'is_public'];
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
      `UPDATE playlists SET ${setClauses.join(', ')} WHERE id = $${paramIndex} RETURNING *`,
      values
    );

    res.json(result.rows[0]);
  } catch (err) {
    console.error('Error updating playlist:', err);
    res.status(500).json({ message: 'Internal server error' });
  }
});

/**
 * @swagger
 * /playlists/{id}:
 *   delete:
 *     summary: Delete playlist
 *     tags: [Playlists]
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
 *         description: Playlist deleted
 *       404:
 *         description: Playlist not found
 */
router.delete('/:id', requireAuth, async (req, res) => {
  try {
    const { id } = req.params;

    const current = await query('SELECT * FROM playlists WHERE id = $1', [id]);
    if (current.rows.length === 0) {
      return res.status(404).json({ message: 'Playlist not found' });
    }

    // Cascade: playlist_tracks are ON DELETE CASCADE
    await query('DELETE FROM playlists WHERE id = $1', [id]);

    res.json({ message: 'Playlist deleted successfully' });
  } catch (err) {
    console.error('Error deleting playlist:', err);
    res.status(500).json({ message: 'Internal server error' });
  }
});

module.exports = router;
