const jwt = require('jsonwebtoken');

const JWT_SECRET = process.env.JWT_SECRET || 'beatflow-secret-key-2026';

/**
 * Middleware that requires a valid JWT token in the Authorization header.
 * Decodes the token and attaches the payload to req.user.
 */
function requireAuth(req, res, next) {
  const authHeader = req.headers.authorization;

  if (!authHeader) {
    return res.status(401).json({ message: 'Authorization header required' });
  }

  const parts = authHeader.split(' ');
  if (parts.length !== 2 || parts[0] !== 'Bearer') {
    return res.status(401).json({ message: 'Invalid authorization format. Use: Bearer <token>' });
  }

  const token = parts[1];

  try {
    const decoded = jwt.verify(token, JWT_SECRET);
    req.user = decoded;
    next();
  } catch (err) {
    if (err.name === 'TokenExpiredError') {
      return res.status(401).json({ message: 'Token expired' });
    }
    return res.status(401).json({ message: 'Invalid token' });
  }
}

/**
 * Generate a JWT token for a given entity.
 * @param {object} payload - { id, email, role }
 * @returns {string} JWT token valid for 24 hours
 */
function generateToken(payload) {
  return jwt.sign(payload, JWT_SECRET, { expiresIn: '24h' });
}

module.exports = { requireAuth, generateToken };
