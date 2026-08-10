const express = require('express');
const cors = require('cors');
const { seed } = require('./utils/seed');
const { setupSwagger } = require('./middleware/swagger');

// Import routes
const genresRouter = require('./routes/genres');
const artistsRouter = require('./routes/artists');
const albumsRouter = require('./routes/albums');
const tracksRouter = require('./routes/tracks');
const listenersRouter = require('./routes/listeners');
const playlistsRouter = require('./routes/playlists');
const playlistTracksRouter = require('./routes/playlist-tracks');
const subscriptionsRouter = require('./routes/subscriptions');
const streamsRouter = require('./routes/streams');
const royaltiesRouter = require('./routes/royalties');
const licensesRouter = require('./routes/licenses');

const app = express();
const PORT = process.env.PORT || 3000;

// ─── MIDDLEWARE ─────────────────────────────────────────────────────────────
app.use(cors({
  origin: '*',
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'PATCH'],
  allowedHeaders: ['Content-Type', 'Authorization', 'Accept'],
  credentials: true,
}));
app.use(express.json());

// ─── SWAGGER ────────────────────────────────────────────────────────────────
setupSwagger(app);

// ─── HEALTH CHECK ───────────────────────────────────────────────────────────
app.get('/health', (req, res) => {
  res.json({ status: 'healthy', service: 'beatflow-api', timestamp: new Date().toISOString() });
});

// ─── ROUTES ─────────────────────────────────────────────────────────────────
app.use('/genres', genresRouter);
app.use('/artists', artistsRouter);
app.use('/albums', albumsRouter);
app.use('/tracks', tracksRouter);
app.use('/listeners', listenersRouter);
app.use('/playlists', playlistsRouter);
app.use('/playlist-tracks', playlistTracksRouter);
app.use('/subscriptions', subscriptionsRouter);
app.use('/streams', streamsRouter);
app.use('/royalties', royaltiesRouter);
app.use('/licenses', licensesRouter);

// ─── 404 HANDLER ────────────────────────────────────────────────────────────
app.use((req, res) => {
  res.status(404).json({ message: `Route not found: ${req.method} ${req.path}` });
});

// ─── ERROR HANDLER ──────────────────────────────────────────────────────────
app.use((err, req, res, next) => {
  console.error('Unhandled error:', err);
  res.status(500).json({ message: 'Internal server error' });
});

// ─── STARTUP ────────────────────────────────────────────────────────────────
async function start() {
  try {
    console.log('Seeding database...');
    await seed();
    console.log('Database ready.');

    app.listen(PORT, '0.0.0.0', () => {
      console.log(`BeatFlow API running on port ${PORT}`);
      console.log(`Swagger docs: http://localhost:${PORT}/api-docs`);
      console.log(`Health check: http://localhost:${PORT}/health`);
    });
  } catch (err) {
    console.error('Failed to start server:', err);
    process.exit(1);
  }
}

start();
