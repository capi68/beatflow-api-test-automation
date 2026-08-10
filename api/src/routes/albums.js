const express = require('express');
const { query } = require('../utils/db');
const { requireAuth } = require('../middleware/auth');

const router = express.Router();

const VALID_STATUSES = ['draft', 'published', 'archived'];
const VALID_TRANSITIONS = {
  draft: ['published', 'archived'],
  published: ['archived'],
  archived: [],
};

/**
 * @swagger
 * /albums:
 *   get:
 *     summary: List albums (filterable by artist_id, status)
 *     tags: [Albums]
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: query
 *         name: artist_id
 *         schema:
 *           type: integer
 *       - in: query
 *         name: status
 *         schema:
 *           type: string
 *     responses:
 *       200:
 *         description: List of albums
 */
router.get('/', requireAuth, async (req, res) => {
  try {
    let sql = 'SELECT * FROM albums WHERE 1=1';
    const params = [];
    let paramIndex = 1;

    if (req.query.artist_id) {
      sql += ` AND artist_id = $${paramIndex}`;
      params.push(req.query.artist_id);
      paramIndex++;
    }
    if (req.query.status) {
      sql += ` AND status = $${paramIndex}`;
      params.push(req.query.status);
      paramIndex++;
    }
    sql += ' ORDER BY created_at DESC';

    const result = await query(sql, params);
    res.json(result.rows);
  } catch (err) {
    console.error('Error listing albums:', err);
    res.status(500).json({ message: 'Internal server error' });
  }
});

/**
 * @swagger
 * /albums:
 *   post:
 *     summary: Create a new album (starts in 'draft')
 *     tags: [Albums]
 *     security:
 *       - bearerAuth: []
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required: [artist_id, title]
 *             properties:
 *               artist_id:
 *                 type: integer
 *               title:
 *                 type: string
 *               description:
 *                 type: string
 *               release_year:
 *                 type: integer
 *               genre_id:
 *                 type: integer
 *               cover_url:
 *                 type: string
 *     responses:
 *       201:
 *         description: Album created
 *       400:
 *         description: Validation error
 *       404:
 *         description: Artist or genre not found
 */
router.post('/', requireAuth, async (req, res) => {
  try {
    const data = req.body || {};

    const required = ['artist_id', 'title'];
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

    // Validate artist exists and is active
    const artist = await query('SELECT id FROM artists WHERE id = $1 AND is_active = TRUE', [data.artist_id]);
    if (artist.rows.length === 0) {
      return res.status(404).json({ message: 'Artist not found or inactive' });
    }

    // Validate release_year if provided
    if (data.release_year !== undefined && data.release_year !== null) {
      if (!Number.isInteger(data.release_year) || data.release_year < 1900 || data.release_year > 2100) {
        return res.status(400).json({ message: 'release_year must be between 1900 and 2100' });
      }
    }

    // Validate genre_id if provided
    if (data.genre_id !== undefined && data.genre_id !== null) {
      const genre = await query('SELECT id FROM genres WHERE id = $1', [data.genre_id]);
      if (genre.rows.length === 0) {
        return res.status(404).json({ message: 'Genre not found' });
      }
    }

    // Validate description length
    if (data.description && data.description.length > 500) {
      return res.status(400).json({ message: 'description must be at most 500 characters' });
    }

    const result = await query(
      `INSERT INTO albums (artist_id, title, description, release_year, genre_id, cover_url)
       VALUES ($1, $2, $3, $4, $5, $6) RETURNING *`,
      [data.artist_id, data.title.trim(), data.description || null, data.release_year || null, data.genre_id || null, data.cover_url || null]
    );

    res.status(201).json(result.rows[0]);
  } catch (err) {
    console.error('Error creating album:', err);
    res.status(500).json({ message: 'Internal server error' });
  }
});

/**
 * @swagger
 * /albums/{id}:
 *   get:
 *     summary: Get album by ID
 *     tags: [Albums]
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
 *         description: Album found
 *       404:
 *         description: Album not found
 */
router.get('/:id', requireAuth, async (req, res) => {
  try {
    const { id } = req.params;
    const result = await query('SELECT * FROM albums WHERE id = $1', [id]);
    if (result.rows.length === 0) {
      return res.status(404).json({ message: 'Album not found' });
    }
    res.json(result.rows[0]);
  } catch (err) {
    console.error('Error getting album:', err);
    res.status(500).json({ message: 'Internal server error' });
  }
});

/**
 * @swagger
 * /albums/{id}:
 *   put:
 *     summary: Update album fields or status
 *     tags: [Albums]
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
 *               description:
 *                 type: string
 *               release_year:
 *                 type: integer
 *               genre_id:
 *                 type: integer
 *               cover_url:
 *                 type: string
 *               status:
 *                 type: string
 *                 enum: [draft, published, archived]
 *     responses:
 *       200:
 *         description: Album updated
 *       400:
 *         description: Invalid status transition or validation error
 *       404:
 *         description: Album not found
 */
router.put('/:id', requireAuth, async (req, res) => {
  try {
    const { id } = req.params;
    const data = req.body || {};

    if (Object.keys(data).length === 0) {
      return res.status(400).json({ message: 'No data provided' });
    }

    const current = await query('SELECT * FROM albums WHERE id = $1', [id]);
    if (current.rows.length === 0) {
      return res.status(404).json({ message: 'Album not found' });
    }
    const album = current.rows[0];

    // Validate status transition
    if (data.status) {
      if (!VALID_STATUSES.includes(data.status)) {
        return res.status(400).json({ message: `Invalid status. Must be one of: ${VALID_STATUSES.join(', ')}` });
      }
      const allowed = VALID_TRANSITIONS[album.status];
      if (!allowed.includes(data.status)) {
        return res.status(400).json({
          message: `Cannot transition from '${album.status}' to '${data.status}'. Allowed: ${allowed.join(', ') || 'none (terminal state)'}`,
        });
      }

      // Must have at least 1 track to publish
      if (data.status === 'published') {
        const trackCount = await query('SELECT COUNT(*) as count FROM tracks WHERE album_id = $1', [id]);
        if (parseInt(trackCount.rows[0].count) === 0) {
          return res.status(400).json({ message: 'Cannot publish album with no tracks' });
        }
      }
    }

    // Validate genre_id if provided
    if (data.genre_id !== undefined && data.genre_id !== null) {
      const genre = await query('SELECT id FROM genres WHERE id = $1', [data.genre_id]);
      if (genre.rows.length === 0) {
        return res.status(404).json({ message: 'Genre not found' });
      }
    }

    const allowedFields = ['title', 'description', 'release_year', 'genre_id', 'cover_url', 'status'];
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
      `UPDATE albums SET ${setClauses.join(', ')} WHERE id = $${paramIndex} RETURNING *`,
      values
    );

    res.json(result.rows[0]);
  } catch (err) {
    console.error('Error updating album:', err);
    res.status(500).json({ message: 'Internal server error' });
  }
});

/**
 * @swagger
 * /albums/{id}:
 *   delete:
 *     summary: Delete album (fails if published or tracks in active streams)
 *     tags: [Albums]
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
 *         description: Album deleted
 *       404:
 *         description: Album not found
 *       409:
 *         description: Cannot delete published album or album with licensed tracks
 */
router.delete('/:id', requireAuth, async (req, res) => {
  try {
    const { id } = req.params;

    const current = await query('SELECT * FROM albums WHERE id = $1', [id]);
    if (current.rows.length === 0) {
      return res.status(404).json({ message: 'Album not found' });
    }

    if (current.rows[0].status === 'published') {
      return res.status(409).json({ message: 'Cannot delete a published album. Archive it first.' });
    }

    // Check for active licenses on any track
    const licenses = await query(
      `SELECT COUNT(*) as count FROM licenses l
       JOIN tracks t ON l.track_id = t.id
       WHERE t.album_id = $1 AND l.status IN ('requested', 'approved', 'active')`,
      [id]
    );
    if (parseInt(licenses.rows[0].count) > 0) {
      return res.status(409).json({ message: 'Cannot delete album with tracks that have active licenses' });
    }

    // Cascade: tracks → playlist_tracks, streams, royalties, licenses
    const tracks = await query('SELECT id FROM tracks WHERE album_id = $1', [id]);
    for (const track of tracks.rows) {
      await query('DELETE FROM playlist_tracks WHERE track_id = $1', [track.id]);
      await query('DELETE FROM streams WHERE track_id = $1', [track.id]);
      await query('DELETE FROM royalties WHERE track_id = $1', [track.id]);
      await query('DELETE FROM licenses WHERE track_id = $1', [track.id]);
    }
    await query('DELETE FROM tracks WHERE album_id = $1', [id]);
    await query('DELETE FROM albums WHERE id = $1', [id]);

    res.json({ message: 'Album deleted successfully' });
  } catch (err) {
    console.error('Error deleting album:', err);
    res.status(500).json({ message: 'Internal server error' });
  }
});

module.exports = router;
