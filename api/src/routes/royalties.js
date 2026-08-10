const express = require('express');
const { query } = require('../utils/db');
const { requireAuth } = require('../middleware/auth');

const router = express.Router();

const VALID_STATUSES = ['pending', 'processing', 'paid', 'failed'];

const VALID_TRANSITIONS = {
  pending: ['processing', 'failed'],
  processing: ['paid', 'failed'],
  paid: [],
  failed: ['pending'],
};

/**
 * @swagger
 * /royalties:
 *   get:
 *     summary: List royalties (filterable by artist_id, track_id, status)
 *     tags: [Royalties]
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: query
 *         name: artist_id
 *         schema:
 *           type: integer
 *       - in: query
 *         name: track_id
 *         schema:
 *           type: integer
 *       - in: query
 *         name: status
 *         schema:
 *           type: string
 *     responses:
 *       200:
 *         description: List of royalties
 */
router.get('/', requireAuth, async (req, res) => {
  try {
    let sql = 'SELECT * FROM royalties WHERE 1=1';
    const params = [];
    let paramIndex = 1;

    if (req.query.artist_id) {
      sql += ` AND artist_id = $${paramIndex}`;
      params.push(req.query.artist_id);
      paramIndex++;
    }
    if (req.query.track_id) {
      sql += ` AND track_id = $${paramIndex}`;
      params.push(req.query.track_id);
      paramIndex++;
    }
    if (req.query.status) {
      sql += ` AND status = $${paramIndex}`;
      params.push(req.query.status);
      paramIndex++;
    }
    sql += ' ORDER BY created_at DESC';

    const result = await query(sql, params);
    const rows = result.rows.map(r => ({
      ...r,
      amount: parseFloat(r.amount),
    }));
    res.json(rows);
  } catch (err) {
    console.error('Error listing royalties:', err);
    res.status(500).json({ message: 'Internal server error' });
  }
});

/**
 * @swagger
 * /royalties:
 *   post:
 *     summary: Create a royalty payment record
 *     tags: [Royalties]
 *     security:
 *       - bearerAuth: []
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required: [artist_id, track_id, stream_count, amount, period_start, period_end]
 *             properties:
 *               artist_id:
 *                 type: integer
 *               track_id:
 *                 type: integer
 *               stream_count:
 *                 type: integer
 *                 example: 1500
 *               amount:
 *                 type: number
 *                 example: 4.50
 *               period_start:
 *                 type: string
 *                 format: date
 *                 example: "2026-01-01"
 *               period_end:
 *                 type: string
 *                 format: date
 *                 example: "2026-01-31"
 *     responses:
 *       201:
 *         description: Royalty record created
 *       400:
 *         description: Validation error
 *       404:
 *         description: Artist or track not found
 *       409:
 *         description: Duplicate royalty for same track and period
 */
router.post('/', requireAuth, async (req, res) => {
  try {
    const data = req.body || {};

    const required = ['artist_id', 'track_id', 'stream_count', 'amount', 'period_start', 'period_end'];
    const missing = required.filter(f => !data[f] && data[f] !== 0);
    if (missing.length > 0) {
      return res.status(400).json({ message: `Missing required fields: ${missing.join(', ')}` });
    }

    // Validate artist exists
    const artist = await query('SELECT id FROM artists WHERE id = $1', [data.artist_id]);
    if (artist.rows.length === 0) {
      return res.status(404).json({ message: 'Artist not found' });
    }

    // Validate track exists
    const track = await query('SELECT * FROM tracks WHERE id = $1', [data.track_id]);
    if (track.rows.length === 0) {
      return res.status(404).json({ message: 'Track not found' });
    }

    // Validate track belongs to artist (via album)
    const album = await query('SELECT artist_id FROM albums WHERE id = $1', [track.rows[0].album_id]);
    if (album.rows.length === 0 || album.rows[0].artist_id !== data.artist_id) {
      return res.status(400).json({ message: 'Track does not belong to this artist' });
    }

    // Validate stream_count
    if (!Number.isInteger(data.stream_count) || data.stream_count < 0) {
      return res.status(400).json({ message: 'stream_count must be a non-negative integer' });
    }

    // Validate amount
    if (typeof data.amount !== 'number' || data.amount < 0 || data.amount > 1000000) {
      return res.status(400).json({ message: 'amount must be between 0 and 1,000,000' });
    }

    // Validate dates
    const periodStart = new Date(data.period_start);
    const periodEnd = new Date(data.period_end);
    if (isNaN(periodStart.getTime()) || isNaN(periodEnd.getTime())) {
      return res.status(400).json({ message: 'Invalid date format. Use YYYY-MM-DD' });
    }
    if (periodEnd <= periodStart) {
      return res.status(400).json({ message: 'period_end must be after period_start' });
    }

    // Check for duplicate (same track + overlapping period)
    const duplicate = await query(
      `SELECT id FROM royalties WHERE track_id = $1 AND period_start = $2 AND period_end = $3`,
      [data.track_id, data.period_start, data.period_end]
    );
    if (duplicate.rows.length > 0) {
      return res.status(409).json({ message: 'Royalty record already exists for this track and period' });
    }

    const result = await query(
      `INSERT INTO royalties (artist_id, track_id, stream_count, amount, period_start, period_end)
       VALUES ($1, $2, $3, $4, $5, $6) RETURNING *`,
      [data.artist_id, data.track_id, data.stream_count, data.amount, data.period_start, data.period_end]
    );

    const royalty = result.rows[0];
    royalty.amount = parseFloat(royalty.amount);
    res.status(201).json(royalty);
  } catch (err) {
    console.error('Error creating royalty:', err);
    res.status(500).json({ message: 'Internal server error' });
  }
});

/**
 * @swagger
 * /royalties/{id}:
 *   get:
 *     summary: Get royalty by ID
 *     tags: [Royalties]
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
 *         description: Royalty found
 *       404:
 *         description: Royalty not found
 */
router.get('/:id', requireAuth, async (req, res) => {
  try {
    const { id } = req.params;
    const result = await query('SELECT * FROM royalties WHERE id = $1', [id]);
    if (result.rows.length === 0) {
      return res.status(404).json({ message: 'Royalty not found' });
    }
    const royalty = result.rows[0];
    royalty.amount = parseFloat(royalty.amount);
    res.json(royalty);
  } catch (err) {
    console.error('Error getting royalty:', err);
    res.status(500).json({ message: 'Internal server error' });
  }
});

/**
 * @swagger
 * /royalties/{id}:
 *   put:
 *     summary: Update royalty status (state machine)
 *     tags: [Royalties]
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
 *               status:
 *                 type: string
 *                 enum: [pending, processing, paid, failed]
 *               failure_reason:
 *                 type: string
 *     responses:
 *       200:
 *         description: Royalty updated
 *       400:
 *         description: Invalid status transition
 *       404:
 *         description: Royalty not found
 */
router.put('/:id', requireAuth, async (req, res) => {
  try {
    const { id } = req.params;
    const data = req.body || {};

    if (Object.keys(data).length === 0) {
      return res.status(400).json({ message: 'No data provided' });
    }

    const current = await query('SELECT * FROM royalties WHERE id = $1', [id]);
    if (current.rows.length === 0) {
      return res.status(404).json({ message: 'Royalty not found' });
    }
    const royalty = current.rows[0];

    if (!data.status) {
      return res.status(400).json({ message: 'status is required' });
    }

    // Validate status
    if (!VALID_STATUSES.includes(data.status)) {
      return res.status(400).json({ message: `Invalid status. Must be one of: ${VALID_STATUSES.join(', ')}` });
    }

    // Validate transition
    const allowed = VALID_TRANSITIONS[royalty.status];
    if (!allowed.includes(data.status)) {
      return res.status(400).json({
        message: `Cannot transition from '${royalty.status}' to '${data.status}'. Allowed: ${allowed.join(', ') || 'none (terminal state)'}`,
      });
    }

    // Validate failure_reason when transitioning to failed
    if (data.status === 'failed' && !data.failure_reason) {
      return res.status(400).json({ message: 'failure_reason is required when status is failed' });
    }
    if (data.failure_reason && data.failure_reason.length > 255) {
      return res.status(400).json({ message: 'failure_reason must be at most 255 characters' });
    }

    const setClauses = ['status = $1', 'updated_at = NOW()'];
    const values = [data.status];
    let paramIndex = 2;

    // Side effects based on new status
    if (data.status === 'processing') {
      setClauses.push('processed_at = NOW()');
    } else if (data.status === 'paid') {
      setClauses.push('paid_at = NOW()');
      // Side effect: update artist total_earnings
      await query(
        'UPDATE artists SET total_earnings = total_earnings + $1, updated_at = NOW() WHERE id = $2',
        [parseFloat(royalty.amount), royalty.artist_id]
      );
    } else if (data.status === 'failed') {
      setClauses.push(`failed_at = NOW()`);
      setClauses.push(`failure_reason = $${paramIndex}`);
      values.push(data.failure_reason);
      paramIndex++;
    } else if (data.status === 'pending' && royalty.status === 'failed') {
      // Retry: clear failure fields
      setClauses.push('failed_at = NULL');
      setClauses.push('failure_reason = NULL');
    }

    values.push(id);

    const result = await query(
      `UPDATE royalties SET ${setClauses.join(', ')} WHERE id = $${paramIndex} RETURNING *`,
      values
    );

    const updated = result.rows[0];
    updated.amount = parseFloat(updated.amount);
    res.json(updated);
  } catch (err) {
    console.error('Error updating royalty:', err);
    res.status(500).json({ message: 'Internal server error' });
  }
});

module.exports = router;
