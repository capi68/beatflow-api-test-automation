const express = require('express');
const { query } = require('../utils/db');
const { requireAuth } = require('../middleware/auth');

const router = express.Router();

/**
 * @swagger
 * /playlist-tracks:
 *   get:
 *     summary: List playlist tracks (filterable by playlist_id)
 *     tags: [Playlist Tracks]
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: query
 *         name: playlist_id
 *         schema:
 *           type: integer
 *         required: true
 *     responses:
 *       200:
 *         description: List of playlist tracks
 *       400:
 *         description: playlist_id required
 */
router.get('/', requireAuth, async (req, res) => {
  try {
    if (!req.query.playlist_id) {
      return res.status(400).json({ message: 'playlist_id query parameter is required' });
    }

    const result = await query(
      `SELECT pt.*, t.title as track_title, t.duration_seconds, t.album_id
       FROM playlist_tracks pt
       JOIN tracks t ON pt.track_id = t.id
       WHERE pt.playlist_id = $1
       ORDER BY pt.position ASC`,
      [req.query.playlist_id]
    );

    res.json(result.rows);
  } catch (err) {
    console.error('Error listing playlist tracks:', err);
    res.status(500).json({ message: 'Internal server error' });
  }
});

/**
 * @swagger
 * /playlist-tracks:
 *   post:
 *     summary: Add a track to a playlist
 *     tags: [Playlist Tracks]
 *     security:
 *       - bearerAuth: []
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required: [playlist_id, track_id]
 *             properties:
 *               playlist_id:
 *                 type: integer
 *               track_id:
 *                 type: integer
 *               position:
 *                 type: integer
 *     responses:
 *       201:
 *         description: Track added to playlist
 *       400:
 *         description: Validation error
 *       404:
 *         description: Playlist or track not found
 *       409:
 *         description: Track already in playlist
 */
router.post('/', requireAuth, async (req, res) => {
  try {
    const data = req.body || {};

    const required = ['playlist_id', 'track_id'];
    const missing = required.filter(f => !data[f] && data[f] !== 0);
    if (missing.length > 0) {
      return res.status(400).json({ message: `Missing required fields: ${missing.join(', ')}` });
    }

    // Validate playlist exists
    const playlist = await query('SELECT * FROM playlists WHERE id = $1', [data.playlist_id]);
    if (playlist.rows.length === 0) {
      return res.status(404).json({ message: 'Playlist not found' });
    }

    // Validate track exists and is available
    const track = await query('SELECT * FROM tracks WHERE id = $1', [data.track_id]);
    if (track.rows.length === 0) {
      return res.status(404).json({ message: 'Track not found' });
    }
    if (!track.rows[0].is_available) {
      return res.status(400).json({ message: 'Track is not available' });
    }

    // Check track not already in playlist
    const existing = await query(
      'SELECT id FROM playlist_tracks WHERE playlist_id = $1 AND track_id = $2',
      [data.playlist_id, data.track_id]
    );
    if (existing.rows.length > 0) {
      return res.status(409).json({ message: 'Track already exists in this playlist' });
    }

    // Max 100 tracks per playlist
    const countResult = await query('SELECT COUNT(*) as count FROM playlist_tracks WHERE playlist_id = $1', [data.playlist_id]);
    if (parseInt(countResult.rows[0].count) >= 100) {
      return res.status(400).json({ message: 'Playlist has reached the maximum of 100 tracks' });
    }

    // Determine position (auto-increment if not provided)
    let position = data.position;
    if (!position || position < 1) {
      const maxPos = await query('SELECT COALESCE(MAX(position), 0) as max_pos FROM playlist_tracks WHERE playlist_id = $1', [data.playlist_id]);
      position = parseInt(maxPos.rows[0].max_pos) + 1;
    }

    const result = await query(
      `INSERT INTO playlist_tracks (playlist_id, track_id, position)
       VALUES ($1, $2, $3) RETURNING *`,
      [data.playlist_id, data.track_id, position]
    );

    // Update track_count on playlist
    await query(
      'UPDATE playlists SET track_count = (SELECT COUNT(*) FROM playlist_tracks WHERE playlist_id = $1), updated_at = NOW() WHERE id = $1',
      [data.playlist_id]
    );

    res.status(201).json(result.rows[0]);
  } catch (err) {
    console.error('Error adding track to playlist:', err);
    res.status(500).json({ message: 'Internal server error' });
  }
});

/**
 * @swagger
 * /playlist-tracks/{id}:
 *   get:
 *     summary: Get playlist track entry by ID
 *     tags: [Playlist Tracks]
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
 *         description: Playlist track entry found
 *       404:
 *         description: Entry not found
 */
router.get('/:id', requireAuth, async (req, res) => {
  try {
    const { id } = req.params;
    const result = await query(
      `SELECT pt.*, t.title as track_title, t.duration_seconds
       FROM playlist_tracks pt
       JOIN tracks t ON pt.track_id = t.id
       WHERE pt.id = $1`,
      [id]
    );
    if (result.rows.length === 0) {
      return res.status(404).json({ message: 'Playlist track entry not found' });
    }
    res.json(result.rows[0]);
  } catch (err) {
    console.error('Error getting playlist track:', err);
    res.status(500).json({ message: 'Internal server error' });
  }
});

/**
 * @swagger
 * /playlist-tracks/{id}:
 *   put:
 *     summary: Update track position in playlist
 *     tags: [Playlist Tracks]
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
 *               position:
 *                 type: integer
 *     responses:
 *       200:
 *         description: Position updated
 *       400:
 *         description: Validation error
 *       404:
 *         description: Entry not found
 */
router.put('/:id', requireAuth, async (req, res) => {
  try {
    const { id } = req.params;
    const data = req.body || {};

    if (data.position === undefined) {
      return res.status(400).json({ message: 'position is required' });
    }

    if (!Number.isInteger(data.position) || data.position < 1) {
      return res.status(400).json({ message: 'position must be a positive integer' });
    }

    const current = await query('SELECT * FROM playlist_tracks WHERE id = $1', [id]);
    if (current.rows.length === 0) {
      return res.status(404).json({ message: 'Playlist track entry not found' });
    }

    const result = await query(
      'UPDATE playlist_tracks SET position = $1 WHERE id = $2 RETURNING *',
      [data.position, id]
    );

    // Update playlist updated_at
    await query('UPDATE playlists SET updated_at = NOW() WHERE id = $1', [current.rows[0].playlist_id]);

    res.json(result.rows[0]);
  } catch (err) {
    console.error('Error updating playlist track:', err);
    res.status(500).json({ message: 'Internal server error' });
  }
});

/**
 * @swagger
 * /playlist-tracks/{id}:
 *   delete:
 *     summary: Remove track from playlist
 *     tags: [Playlist Tracks]
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
 *         description: Track removed from playlist
 *       404:
 *         description: Entry not found
 */
router.delete('/:id', requireAuth, async (req, res) => {
  try {
    const { id } = req.params;

    const current = await query('SELECT * FROM playlist_tracks WHERE id = $1', [id]);
    if (current.rows.length === 0) {
      return res.status(404).json({ message: 'Playlist track entry not found' });
    }

    const playlistId = current.rows[0].playlist_id;

    await query('DELETE FROM playlist_tracks WHERE id = $1', [id]);

    // Update track_count
    await query(
      'UPDATE playlists SET track_count = (SELECT COUNT(*) FROM playlist_tracks WHERE playlist_id = $1), updated_at = NOW() WHERE id = $1',
      [playlistId]
    );

    res.json({ message: 'Track removed from playlist' });
  } catch (err) {
    console.error('Error removing track from playlist:', err);
    res.status(500).json({ message: 'Internal server error' });
  }
});

module.exports = router;
