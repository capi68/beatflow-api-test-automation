const express = require('express');
const { query } = require('../utils/db');
const { requireAuth } = require('../middleware/auth');

const router = express.Router();

const VALID_PLANS = ['free', 'basic', 'premium'];
const VALID_STATUSES = ['active', 'paused', 'cancelled', 'expired'];

const VALID_TRANSITIONS = {
  active: ['paused', 'cancelled'],
  paused: ['active', 'cancelled'],
  cancelled: [],
  expired: [],
};

/**
 * @swagger
 * /subscriptions:
 *   get:
 *     summary: List subscriptions (filterable by listener_id, status)
 *     tags: [Subscriptions]
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: query
 *         name: listener_id
 *         schema:
 *           type: integer
 *       - in: query
 *         name: status
 *         schema:
 *           type: string
 *     responses:
 *       200:
 *         description: List of subscriptions
 */
router.get('/', requireAuth, async (req, res) => {
  try {
    let sql = 'SELECT * FROM subscriptions WHERE 1=1';
    const params = [];
    let paramIndex = 1;

    if (req.query.listener_id) {
      sql += ` AND listener_id = $${paramIndex}`;
      params.push(req.query.listener_id);
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
    console.error('Error listing subscriptions:', err);
    res.status(500).json({ message: 'Internal server error' });
  }
});

/**
 * @swagger
 * /subscriptions:
 *   post:
 *     summary: Create a new subscription for a listener
 *     tags: [Subscriptions]
 *     security:
 *       - bearerAuth: []
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required: [listener_id, plan]
 *             properties:
 *               listener_id:
 *                 type: integer
 *               plan:
 *                 type: string
 *                 enum: [free, basic, premium]
 *     responses:
 *       201:
 *         description: Subscription created
 *       400:
 *         description: Validation error
 *       404:
 *         description: Listener not found
 *       409:
 *         description: Listener already has active subscription
 */
router.post('/', requireAuth, async (req, res) => {
  try {
    const data = req.body || {};

    const required = ['listener_id', 'plan'];
    const missing = required.filter(f => !data[f] && data[f] !== 0);
    if (missing.length > 0) {
      return res.status(400).json({ message: `Missing required fields: ${missing.join(', ')}` });
    }

    // Validate plan
    if (!VALID_PLANS.includes(data.plan)) {
      return res.status(400).json({ message: `Invalid plan. Must be one of: ${VALID_PLANS.join(', ')}` });
    }

    // Validate listener exists
    const listener = await query('SELECT id FROM listeners WHERE id = $1 AND is_active = TRUE', [data.listener_id]);
    if (listener.rows.length === 0) {
      return res.status(404).json({ message: 'Listener not found or inactive' });
    }

    // Check no active/paused subscription exists
    const existing = await query(
      "SELECT id FROM subscriptions WHERE listener_id = $1 AND status IN ('active', 'paused')",
      [data.listener_id]
    );
    if (existing.rows.length > 0) {
      return res.status(409).json({ message: 'Listener already has an active or paused subscription' });
    }

    // Calculate expiration (free=no expiry, basic=30 days, premium=365 days)
    let expiresAt = null;
    if (data.plan === 'basic') {
      expiresAt = new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString();
    } else if (data.plan === 'premium') {
      expiresAt = new Date(Date.now() + 365 * 24 * 60 * 60 * 1000).toISOString();
    }

    const result = await query(
      `INSERT INTO subscriptions (listener_id, plan, status, expires_at)
       VALUES ($1, $2, 'active', $3) RETURNING *`,
      [data.listener_id, data.plan, expiresAt]
    );

    res.status(201).json(result.rows[0]);
  } catch (err) {
    console.error('Error creating subscription:', err);
    res.status(500).json({ message: 'Internal server error' });
  }
});

/**
 * @swagger
 * /subscriptions/{id}:
 *   get:
 *     summary: Get subscription by ID
 *     tags: [Subscriptions]
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
 *         description: Subscription found
 *       404:
 *         description: Subscription not found
 */
router.get('/:id', requireAuth, async (req, res) => {
  try {
    const { id } = req.params;
    const result = await query('SELECT * FROM subscriptions WHERE id = $1', [id]);
    if (result.rows.length === 0) {
      return res.status(404).json({ message: 'Subscription not found' });
    }
    res.json(result.rows[0]);
  } catch (err) {
    console.error('Error getting subscription:', err);
    res.status(500).json({ message: 'Internal server error' });
  }
});

/**
 * @swagger
 * /subscriptions/{id}:
 *   put:
 *     summary: Update subscription status or plan
 *     tags: [Subscriptions]
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
 *                 enum: [active, paused, cancelled, expired]
 *               plan:
 *                 type: string
 *                 enum: [free, basic, premium]
 *     responses:
 *       200:
 *         description: Subscription updated
 *       400:
 *         description: Invalid transition or validation error
 *       404:
 *         description: Subscription not found
 */
router.put('/:id', requireAuth, async (req, res) => {
  try {
    const { id } = req.params;
    const data = req.body || {};

    if (Object.keys(data).length === 0) {
      return res.status(400).json({ message: 'No data provided' });
    }

    const current = await query('SELECT * FROM subscriptions WHERE id = $1', [id]);
    if (current.rows.length === 0) {
      return res.status(404).json({ message: 'Subscription not found' });
    }
    const subscription = current.rows[0];

    // Validate status transition
    if (data.status) {
      if (!VALID_STATUSES.includes(data.status)) {
        return res.status(400).json({ message: `Invalid status. Must be one of: ${VALID_STATUSES.join(', ')}` });
      }
      const allowed = VALID_TRANSITIONS[subscription.status];
      if (!allowed.includes(data.status)) {
        return res.status(400).json({
          message: `Cannot transition from '${subscription.status}' to '${data.status}'. Allowed: ${allowed.join(', ') || 'none (terminal state)'}`,
        });
      }
    }

    // Validate plan if changing
    if (data.plan) {
      if (!VALID_PLANS.includes(data.plan)) {
        return res.status(400).json({ message: `Invalid plan. Must be one of: ${VALID_PLANS.join(', ')}` });
      }
      // Can only change plan while active
      if (subscription.status !== 'active') {
        return res.status(400).json({ message: 'Can only change plan while subscription is active' });
      }
    }

    const setClauses = [];
    const values = [];
    let paramIndex = 1;

    if (data.status) {
      setClauses.push(`status = $${paramIndex}`);
      values.push(data.status);
      paramIndex++;

      // Side effects
      if (data.status === 'paused') {
        setClauses.push(`paused_at = NOW()`);
      } else if (data.status === 'cancelled') {
        setClauses.push(`cancelled_at = NOW()`);
      } else if (data.status === 'active' && subscription.status === 'paused') {
        // Resume: clear paused_at
        setClauses.push(`paused_at = NULL`);
      }
    }

    if (data.plan) {
      setClauses.push(`plan = $${paramIndex}`);
      values.push(data.plan);
      paramIndex++;

      // Update expiration based on new plan
      if (data.plan === 'free') {
        setClauses.push('expires_at = NULL');
      } else if (data.plan === 'basic') {
        setClauses.push(`expires_at = NOW() + INTERVAL '30 days'`);
      } else if (data.plan === 'premium') {
        setClauses.push(`expires_at = NOW() + INTERVAL '365 days'`);
      }
    }

    if (setClauses.length === 0) {
      return res.status(400).json({ message: 'No valid fields to update' });
    }

    setClauses.push('updated_at = NOW()');
    values.push(id);

    const result = await query(
      `UPDATE subscriptions SET ${setClauses.join(', ')} WHERE id = $${paramIndex} RETURNING *`,
      values
    );

    res.json(result.rows[0]);
  } catch (err) {
    console.error('Error updating subscription:', err);
    res.status(500).json({ message: 'Internal server error' });
  }
});

module.exports = router;
