const express = require('express');
const { query } = require('../utils/db');
const { requireAuth } = require('../middleware/auth');

const router = express.Router();

const VALID_LICENSE_TYPES = ['sync', 'mechanical', 'performance', 'master'];
const VALID_STATUSES = ['requested', 'approved', 'active', 'expired', 'revoked'];

const VALID_TRANSITIONS = {
  requested: ['approved', 'revoked'],
  approved: ['active', 'revoked'],
  active: ['expired', 'revoked'],
  expired: [],
  revoked: [],
};

/**
 * @swagger
 * /licenses:
 *   get:
 *     summary: List licenses (filterable by track_id, status, license_type)
 *     tags: [Licenses]
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: query
 *         name: track_id
 *         schema:
 *           type: integer
 *       - in: query
 *         name: status
 *         schema:
 *           type: string
 *       - in: query
 *         name: license_type
 *         schema:
 *           type: string
 *     responses:
 *       200:
 *         description: List of licenses
 */
router.get('/', requireAuth, async (req, res) => {
  try {
    let sql = 'SELECT * FROM licenses WHERE 1=1';
    const params = [];
    let paramIndex = 1;

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
    if (req.query.license_type) {
      sql += ` AND license_type = $${paramIndex}`;
      params.push(req.query.license_type);
      paramIndex++;
    }
    sql += ' ORDER BY created_at DESC';

    const result = await query(sql, params);
    const rows = result.rows.map(r => ({
      ...r,
      fee: parseFloat(r.fee),
    }));
    res.json(rows);
  } catch (err) {
    console.error('Error listing licenses:', err);
    res.status(500).json({ message: 'Internal server error' });
  }
});

/**
 * @swagger
 * /licenses:
 *   post:
 *     summary: Request a license for a track
 *     tags: [Licenses]
 *     security:
 *       - bearerAuth: []
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required: [track_id, licensee_name, licensee_email, license_type, fee]
 *             properties:
 *               track_id:
 *                 type: integer
 *               licensee_name:
 *                 type: string
 *               licensee_email:
 *                 type: string
 *               license_type:
 *                 type: string
 *                 enum: [sync, mechanical, performance, master]
 *               fee:
 *                 type: number
 *                 example: 500.00
 *               territory:
 *                 type: string
 *                 example: "worldwide"
 *               starts_at:
 *                 type: string
 *                 format: date
 *               expires_at:
 *                 type: string
 *                 format: date
 *     responses:
 *       201:
 *         description: License requested
 *       400:
 *         description: Validation error
 *       404:
 *         description: Track not found
 *       409:
 *         description: Active license of same type already exists for this track
 */
router.post('/', requireAuth, async (req, res) => {
  try {
    const data = req.body || {};

    const required = ['track_id', 'licensee_name', 'licensee_email', 'license_type', 'fee'];
    const missing = required.filter(f => !data[f] && data[f] !== 0);
    if (missing.length > 0) {
      return res.status(400).json({ message: `Missing required fields: ${missing.join(', ')}` });
    }

    // Validate string fields
    if (typeof data.licensee_name !== 'string' || data.licensee_name.trim() === '') {
      return res.status(400).json({ message: 'licensee_name must be a non-empty string' });
    }
    if (data.licensee_name.length > 200) {
      return res.status(400).json({ message: 'licensee_name must be at most 200 characters' });
    }

    // Validate email
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(data.licensee_email)) {
      return res.status(400).json({ message: 'Invalid licensee_email format' });
    }

    // Validate license_type
    if (!VALID_LICENSE_TYPES.includes(data.license_type)) {
      return res.status(400).json({ message: `Invalid license_type. Must be one of: ${VALID_LICENSE_TYPES.join(', ')}` });
    }

    // Validate fee (100 to 1,000,000)
    if (typeof data.fee !== 'number' || data.fee < 100 || data.fee > 1000000) {
      return res.status(400).json({ message: 'fee must be between 100 and 1,000,000' });
    }

    // Validate track exists and is available
    const track = await query('SELECT * FROM tracks WHERE id = $1', [data.track_id]);
    if (track.rows.length === 0) {
      return res.status(404).json({ message: 'Track not found' });
    }
    if (!track.rows[0].is_available) {
      return res.status(400).json({ message: 'Track is not available for licensing' });
    }

    // Check no active/approved/requested license of same type exists for this track
    const existing = await query(
      "SELECT id FROM licenses WHERE track_id = $1 AND license_type = $2 AND status IN ('requested', 'approved', 'active')",
      [data.track_id, data.license_type]
    );
    if (existing.rows.length > 0) {
      return res.status(409).json({ message: `A ${data.license_type} license already exists for this track (status: requested, approved, or active)` });
    }

    // Validate dates if provided
    if (data.starts_at) {
      const startsAt = new Date(data.starts_at);
      if (isNaN(startsAt.getTime())) {
        return res.status(400).json({ message: 'Invalid starts_at date format. Use YYYY-MM-DD' });
      }
    }
    if (data.expires_at) {
      const expiresAt = new Date(data.expires_at);
      if (isNaN(expiresAt.getTime())) {
        return res.status(400).json({ message: 'Invalid expires_at date format. Use YYYY-MM-DD' });
      }
      if (data.starts_at && new Date(data.expires_at) <= new Date(data.starts_at)) {
        return res.status(400).json({ message: 'expires_at must be after starts_at' });
      }
    }

    // Validate territory length
    if (data.territory && data.territory.length > 100) {
      return res.status(400).json({ message: 'territory must be at most 100 characters' });
    }

    const result = await query(
      `INSERT INTO licenses (track_id, licensee_name, licensee_email, license_type, fee, territory, starts_at, expires_at)
       VALUES ($1, $2, $3, $4, $5, $6, $7, $8) RETURNING *`,
      [data.track_id, data.licensee_name.trim(), data.licensee_email, data.license_type, data.fee, data.territory || 'worldwide', data.starts_at || null, data.expires_at || null]
    );

    const license = result.rows[0];
    license.fee = parseFloat(license.fee);
    res.status(201).json(license);
  } catch (err) {
    console.error('Error creating license:', err);
    res.status(500).json({ message: 'Internal server error' });
  }
});

/**
 * @swagger
 * /licenses/{id}:
 *   get:
 *     summary: Get license by ID
 *     tags: [Licenses]
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
 *         description: License found
 *       404:
 *         description: License not found
 */
router.get('/:id', requireAuth, async (req, res) => {
  try {
    const { id } = req.params;
    const result = await query('SELECT * FROM licenses WHERE id = $1', [id]);
    if (result.rows.length === 0) {
      return res.status(404).json({ message: 'License not found' });
    }
    const license = result.rows[0];
    license.fee = parseFloat(license.fee);
    res.json(license);
  } catch (err) {
    console.error('Error getting license:', err);
    res.status(500).json({ message: 'Internal server error' });
  }
});

/**
 * @swagger
 * /licenses/{id}:
 *   put:
 *     summary: Update license status (state machine)
 *     tags: [Licenses]
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
 *                 enum: [requested, approved, active, expired, revoked]
 *               revocation_reason:
 *                 type: string
 *     responses:
 *       200:
 *         description: License updated
 *       400:
 *         description: Invalid transition or validation error
 *       404:
 *         description: License not found
 */
router.put('/:id', requireAuth, async (req, res) => {
  try {
    const { id } = req.params;
    const data = req.body || {};

    if (Object.keys(data).length === 0) {
      return res.status(400).json({ message: 'No data provided' });
    }

    const current = await query('SELECT * FROM licenses WHERE id = $1', [id]);
    if (current.rows.length === 0) {
      return res.status(404).json({ message: 'License not found' });
    }
    const license = current.rows[0];

    if (!data.status) {
      return res.status(400).json({ message: 'status is required' });
    }

    // Validate status
    if (!VALID_STATUSES.includes(data.status)) {
      return res.status(400).json({ message: `Invalid status. Must be one of: ${VALID_STATUSES.join(', ')}` });
    }

    // Validate transition
    const allowed = VALID_TRANSITIONS[license.status];
    if (!allowed.includes(data.status)) {
      return res.status(400).json({
        message: `Cannot transition from '${license.status}' to '${data.status}'. Allowed: ${allowed.join(', ') || 'none (terminal state)'}`,
      });
    }

    // Validate revocation_reason when revoking
    if (data.status === 'revoked' && !data.revocation_reason) {
      return res.status(400).json({ message: 'revocation_reason is required when revoking a license' });
    }
    if (data.revocation_reason && data.revocation_reason.length > 255) {
      return res.status(400).json({ message: 'revocation_reason must be at most 255 characters' });
    }

    const setClauses = ['status = $1', 'updated_at = NOW()'];
    const values = [data.status];
    let paramIndex = 2;

    // Side effects
    if (data.status === 'approved') {
      setClauses.push('approved_at = NOW()');
    } else if (data.status === 'revoked') {
      setClauses.push('revoked_at = NOW()');
      setClauses.push(`revocation_reason = $${paramIndex}`);
      values.push(data.revocation_reason);
      paramIndex++;

      // Side effect: set track is_available = false
      await query('UPDATE tracks SET is_available = FALSE, updated_at = NOW() WHERE id = $1', [license.track_id]);
    } else if (data.status === 'active') {
      // If starts_at not set, set it to now
      if (!license.starts_at) {
        setClauses.push('starts_at = CURRENT_DATE');
      }
    }

    values.push(id);

    const result = await query(
      `UPDATE licenses SET ${setClauses.join(', ')} WHERE id = $${paramIndex} RETURNING *`,
      values
    );

    const updated = result.rows[0];
    updated.fee = parseFloat(updated.fee);
    res.json(updated);
  } catch (err) {
    console.error('Error updating license:', err);
    res.status(500).json({ message: 'Internal server error' });
  }
});

module.exports = router;
