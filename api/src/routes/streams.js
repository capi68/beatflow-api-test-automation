const express = require('express');
const { query } = require('../utils/db');
const { requireAuth } = require('../middleware/auth');

const router = express.Router();

/**
 * @swagger
 * /streams:
 *   get:
 *     summary: List streams (filterable by listener_id, track_id)
 *     tags: [Streams]
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: query
 *         name: listener_id
 *         schema:
 *           type: integer
 *       - in: query
 *         name: track_id
 *         schema:
 *           type: integer
 *     responses:
 *       200:
 *         description: List of streams
 */
router.get('/', requireAuth, async (req, res) => {
  try {
    let sql = 'SELECT * FROM streams WHERE 1=1';
    const params = [];
    let paramIndex = 1;

    if (req.query.listener_id) {
      sql += ` AND listener_id = $${paramIndex}`;
      params.push(req.query.listener_id);
      paramIndex++;
    }
    if (req.query.track_id) {
      sql += ` AND track_id = $${paramIndex}`;
      params.push(req.query.track_id);
      paramIndex++;
    }
    sql += ' ORDER BY streamed_at DESC';

    const result = await query(sql, params);
    res.json(result.rows);
  } catch (err) {
    console.error('Error listing streams:', err);
    res.status(500).json({ message: 'Internal server error' });
  }
});

/**
 * @swagger
 * /streams:
 *   post:
 *     summary: Record a stream (play event)
 *     tags: [Streams]
 *     security:
 *       - bearerAuth: []
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required: [listener_id, track_id, duration_seconds]
 *             properties:
 *               listener_id:
 *                 type: integer
 *               track_id:
 *                 type: integer
 *               duration_seconds:
 *                 type: integer
 *                 description: How many seconds the listener played
 *                 example: 180
 *     responses:
 *       201:
 *         description: Stream recorded
 *       400:
 *         description: Validation error
 *       404:
 *         description: Listener or track not found
 *       403:
 *         description: No active subscription
 */
router.post('/', requireAuth, async (req, res) => {
  try {
    const data = req.body || {};

    const required = ['listener_id', 'track_id', 'duration_seconds'];
    const missing = required.filter(f => !data[f] && data[f] !== 0);
    if (missing.length > 0) {
      return res.status(400).json({ message: `Missing required fields: ${missing.join(', ')}` });
    }

    // Validate duration_seconds (minimum 10 seconds to count as a stream)
    if (!Number.isInteger(data.duration_seconds) || data.duration_seconds < 10) {
      return res.status(400).json({ message: 'duration_seconds must be at least 10' });
    }

    // Validate listener exists and is active
    const listener = await query('SELECT id FROM listeners WHERE id = $1 AND is_active = TRUE', [data.listener_id]);
    if (listener.rows.length === 0) {
      return res.status(404).json({ message: 'Listener not found or inactive' });
    }

    // Validate listener has an active subscription
    const subscription = await query(
      "SELECT id, plan FROM subscriptions WHERE listener_id = $1 AND status = 'active'",
      [data.listener_id]
    );
    if (subscription.rows.length === 0) {
      return res.status(403).json({ message: 'Listener does not have an active subscription. Cannot stream.' });
    }

    // Free plan: max 5 streams per day
    if (subscription.rows[0].plan === 'free') {
      const todayStreams = await query(
        "SELECT COUNT(*) as count FROM streams WHERE listener_id = $1 AND streamed_at >= CURRENT_DATE",
        [data.listener_id]
      );
      if (parseInt(todayStreams.rows[0].count) >= 5) {
        return res.status(403).json({ message: 'Free plan limit reached: maximum 5 streams per day' });
      }
    }

    // Basic plan: max 50 streams per day
    if (subscription.rows[0].plan === 'basic') {
      const todayStreams = await query(
        "SELECT COUNT(*) as count FROM streams WHERE listener_id = $1 AND streamed_at >= CURRENT_DATE",
        [data.listener_id]
      );
      if (parseInt(todayStreams.rows[0].count) >= 50) {
        return res.status(403).json({ message: 'Basic plan limit reached: maximum 50 streams per day' });
      }
    }

    // Validate track exists and is available
    const track = await query('SELECT * FROM tracks WHERE id = $1', [data.track_id]);
    if (track.rows.length === 0) {
      return res.status(404).json({ message: 'Track not found' });
    }
    if (!track.rows[0].is_available) {
      return res.status(400).json({ message: 'Track is not available for streaming' });
    }

    // Track must belong to a published album
    const album = await query("SELECT status FROM albums WHERE id = $1", [track.rows[0].album_id]);
    if (album.rows.length === 0 || album.rows[0].status !== 'published') {
      return res.status(400).json({ message: 'Track is not in a published album' });
    }

    // Determine if stream is "completed" (listened to >= 80% of track duration)
    const trackDuration = track.rows[0].duration_seconds;
    const completed = data.duration_seconds >= Math.floor(trackDuration * 0.8);

    // Cap duration_seconds at track duration
    const actualDuration = Math.min(data.duration_seconds, trackDuration);

    const result = await query(
      `INSERT INTO streams (listener_id, track_id, duration_seconds, completed)
       VALUES ($1, $2, $3, $4) RETURNING *`,
      [data.listener_id, data.track_id, actualDuration, completed]
    );

    // Side effect: increment play_count on track
    await query('UPDATE tracks SET play_count = play_count + 1, updated_at = NOW() WHERE id = $1', [data.track_id]);

    res.status(201).json(result.rows[0]);
  } catch (err) {
    console.error('Error creating stream:', err);
    res.status(500).json({ message: 'Internal server error' });
  }
});

/**
 * @swagger
 * /streams/{id}:
 *   get:
 *     summary: Get stream by ID
 *     tags: [Streams]
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
 *         description: Stream found
 *       404:
 *         description: Stream not found
 */
router.get('/:id', requireAuth, async (req, res) => {
  try {
    const { id } = req.params;
    const result = await query('SELECT * FROM streams WHERE id = $1', [id]);
    if (result.rows.length === 0) {
      return res.status(404).json({ message: 'Stream not found' });
    }
    res.json(result.rows[0]);
  } catch (err) {
    console.error('Error getting stream:', err);
    res.status(500).json({ message: 'Internal server error' });
  }
});

module.exports = router;
