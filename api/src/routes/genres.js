const express = require('express');
const router = express.Router();
const { query } = require('../utils/db');

/**
 * @swagger
 * components:
 *   schemas:
 *     Genre:
 *       type: object
 *       properties:
 *         id:
 *           type: integer
 *           description: The genre ID
 *         name:
 *           type: string
 *           description: The genre name
 *         description:
 *           type: string
 *           description: A brief description of the genre
 *         created_at:
 *           type: string
 *           format: date-time
 *           description: When the genre was created
 */

/**
 * @swagger
 * /genres:
 *   get:
 *     summary: List all genres
 *     tags: [Genres]
 *     responses:
 *       200:
 *         description: A list of genres
 *         content:
 *           application/json:
 *             schema:
 *               type: array
 *               items:
 *                 $ref: '#/components/schemas/Genre'
 *       500:
 *         description: Server error
 */
router.get('/', async (req, res) => {
  try {
    const result = await query('SELECT * FROM genres ORDER BY name');
    res.json(result.rows);
  } catch (error) {
    console.error('Error fetching genres:', error);
    res.status(500).json({ message: 'Internal server error' });
  }
});

/**
 * @swagger
 * /genres/{id}:
 *   get:
 *     summary: Get a genre by ID
 *     tags: [Genres]
 *     parameters:
 *       - in: path
 *         name: id
 *         required: true
 *         schema:
 *           type: integer
 *         description: The genre ID
 *     responses:
 *       200:
 *         description: The genre
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/Genre'
 *       404:
 *         description: Genre not found
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 message:
 *                   type: string
 *                   example: Genre not found
 *       500:
 *         description: Server error
 */
router.get('/:id', async (req, res) => {
  try {
    const { id } = req.params;
    const result = await query('SELECT * FROM genres WHERE id = $1', [id]);

    if (result.rows.length === 0) {
      return res.status(404).json({ message: 'Genre not found' });
    }

    res.json(result.rows[0]);
  } catch (error) {
    console.error('Error fetching genre:', error);
    res.status(500).json({ message: 'Internal server error' });
  }
});

module.exports = router;
