const { pool } = require('./db');
const bcrypt = require('bcryptjs');

async function seed() {
  const client = await pool.connect();
  try {
    await client.query('BEGIN');

    // ─── GENRES (reference table) ───────────────────────────────────────
    await client.query(`
      CREATE TABLE IF NOT EXISTS genres (
        id SERIAL PRIMARY KEY,
        name VARCHAR(50) NOT NULL UNIQUE,
        description VARCHAR(255),
        created_at TIMESTAMP DEFAULT NOW()
      )
    `);

    // ─── ARTISTS ────────────────────────────────────────────────────────
    await client.query(`
      CREATE TABLE IF NOT EXISTS artists (
        id SERIAL PRIMARY KEY,
        stage_name VARCHAR(100) NOT NULL,
        first_name VARCHAR(100) NOT NULL,
        last_name VARCHAR(100) NOT NULL,
        email VARCHAR(255) NOT NULL UNIQUE,
        password_hash VARCHAR(255) NOT NULL,
        genre_id INTEGER REFERENCES genres(id),
        bio VARCHAR(500),
        country VARCHAR(100),
        total_earnings DECIMAL(12,2) DEFAULT 0.00,
        is_active BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP DEFAULT NOW(),
        updated_at TIMESTAMP DEFAULT NOW()
      )
    `);

    // ─── ALBUMS ─────────────────────────────────────────────────────────
    await client.query(`
      CREATE TABLE IF NOT EXISTS albums (
        id SERIAL PRIMARY KEY,
        artist_id INTEGER NOT NULL REFERENCES artists(id),
        title VARCHAR(200) NOT NULL,
        description VARCHAR(500),
        release_year INTEGER,
        genre_id INTEGER REFERENCES genres(id),
        cover_url VARCHAR(500),
        status VARCHAR(20) DEFAULT 'draft' CHECK (status IN ('draft', 'published', 'archived')),
        created_at TIMESTAMP DEFAULT NOW(),
        updated_at TIMESTAMP DEFAULT NOW()
      )
    `);

    // ─── TRACKS ─────────────────────────────────────────────────────────
    await client.query(`
      CREATE TABLE IF NOT EXISTS tracks (
        id SERIAL PRIMARY KEY,
        album_id INTEGER NOT NULL REFERENCES albums(id),
        title VARCHAR(200) NOT NULL,
        duration_seconds INTEGER NOT NULL,
        track_number INTEGER NOT NULL,
        genre_id INTEGER REFERENCES genres(id),
        is_available BOOLEAN DEFAULT TRUE,
        is_explicit BOOLEAN DEFAULT FALSE,
        play_count INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT NOW(),
        updated_at TIMESTAMP DEFAULT NOW()
      )
    `);

    // ─── LISTENERS ──────────────────────────────────────────────────────
    await client.query(`
      CREATE TABLE IF NOT EXISTS listeners (
        id SERIAL PRIMARY KEY,
        username VARCHAR(50) NOT NULL UNIQUE,
        email VARCHAR(255) NOT NULL UNIQUE,
        password_hash VARCHAR(255) NOT NULL,
        first_name VARCHAR(100) NOT NULL,
        last_name VARCHAR(100) NOT NULL,
        date_of_birth DATE,
        country VARCHAR(100),
        is_active BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP DEFAULT NOW(),
        updated_at TIMESTAMP DEFAULT NOW()
      )
    `);

    // ─── SUBSCRIPTIONS ──────────────────────────────────────────────────
    await client.query(`
      CREATE TABLE IF NOT EXISTS subscriptions (
        id SERIAL PRIMARY KEY,
        listener_id INTEGER NOT NULL REFERENCES listeners(id),
        plan VARCHAR(20) NOT NULL CHECK (plan IN ('free', 'basic', 'premium')),
        status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'paused', 'cancelled', 'expired')),
        started_at TIMESTAMP DEFAULT NOW(),
        expires_at TIMESTAMP,
        paused_at TIMESTAMP,
        cancelled_at TIMESTAMP,
        created_at TIMESTAMP DEFAULT NOW(),
        updated_at TIMESTAMP DEFAULT NOW()
      )
    `);

    // ─── PLAYLISTS ──────────────────────────────────────────────────────
    await client.query(`
      CREATE TABLE IF NOT EXISTS playlists (
        id SERIAL PRIMARY KEY,
        listener_id INTEGER NOT NULL REFERENCES listeners(id),
        name VARCHAR(200) NOT NULL,
        description VARCHAR(500),
        is_public BOOLEAN DEFAULT FALSE,
        track_count INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT NOW(),
        updated_at TIMESTAMP DEFAULT NOW()
      )
    `);

    // ─── PLAYLIST TRACKS (junction) ─────────────────────────────────────
    await client.query(`
      CREATE TABLE IF NOT EXISTS playlist_tracks (
        id SERIAL PRIMARY KEY,
        playlist_id INTEGER NOT NULL REFERENCES playlists(id) ON DELETE CASCADE,
        track_id INTEGER NOT NULL REFERENCES tracks(id),
        position INTEGER NOT NULL,
        added_at TIMESTAMP DEFAULT NOW(),
        UNIQUE(playlist_id, track_id)
      )
    `);

    // ─── STREAMS (play events) ──────────────────────────────────────────
    await client.query(`
      CREATE TABLE IF NOT EXISTS streams (
        id SERIAL PRIMARY KEY,
        listener_id INTEGER NOT NULL REFERENCES listeners(id),
        track_id INTEGER NOT NULL REFERENCES tracks(id),
        duration_seconds INTEGER NOT NULL,
        completed BOOLEAN DEFAULT FALSE,
        streamed_at TIMESTAMP DEFAULT NOW()
      )
    `);

    // ─── ROYALTIES ──────────────────────────────────────────────────────
    await client.query(`
      CREATE TABLE IF NOT EXISTS royalties (
        id SERIAL PRIMARY KEY,
        artist_id INTEGER NOT NULL REFERENCES artists(id),
        track_id INTEGER NOT NULL REFERENCES tracks(id),
        stream_count INTEGER NOT NULL DEFAULT 0,
        amount DECIMAL(10,2) NOT NULL,
        status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'paid', 'failed')),
        period_start DATE NOT NULL,
        period_end DATE NOT NULL,
        processed_at TIMESTAMP,
        paid_at TIMESTAMP,
        failed_at TIMESTAMP,
        failure_reason VARCHAR(255),
        created_at TIMESTAMP DEFAULT NOW(),
        updated_at TIMESTAMP DEFAULT NOW()
      )
    `);

    // ─── LICENSES ───────────────────────────────────────────────────────
    await client.query(`
      CREATE TABLE IF NOT EXISTS licenses (
        id SERIAL PRIMARY KEY,
        track_id INTEGER NOT NULL REFERENCES tracks(id),
        licensee_name VARCHAR(200) NOT NULL,
        licensee_email VARCHAR(255) NOT NULL,
        license_type VARCHAR(30) NOT NULL CHECK (license_type IN ('sync', 'mechanical', 'performance', 'master')),
        status VARCHAR(20) DEFAULT 'requested' CHECK (status IN ('requested', 'approved', 'active', 'expired', 'revoked')),
        fee DECIMAL(10,2) NOT NULL,
        territory VARCHAR(100) DEFAULT 'worldwide',
        starts_at DATE,
        expires_at DATE,
        approved_at TIMESTAMP,
        revoked_at TIMESTAMP,
        revocation_reason VARCHAR(255),
        created_at TIMESTAMP DEFAULT NOW(),
        updated_at TIMESTAMP DEFAULT NOW()
      )
    `);

    // ─── SEED DATA ──────────────────────────────────────────────────────

    // Genres
    const genres = ['rock', 'pop', 'hip-hop', 'electronic', 'jazz', 'classical', 'r&b', 'country', 'latin', 'metal'];
    for (const genre of genres) {
      await client.query(
        `INSERT INTO genres (name, description) VALUES ($1, $2) ON CONFLICT (name) DO NOTHING`,
        [genre, `${genre.charAt(0).toUpperCase() + genre.slice(1)} music genre`]
      );
    }

    // Admin Artist
    const artistHash = await bcrypt.hash('Artist123!', 10);
    await client.query(`
      INSERT INTO artists (stage_name, first_name, last_name, email, password_hash, genre_id, bio, country)
      VALUES ($1, $2, $3, $4, $5, 1, $6, $7)
      ON CONFLICT (email) DO NOTHING
    `, ['DJ Thunder', 'Carlos', 'Rivera', 'artist@beatflow.com', artistHash, 'Producer and DJ with 10 years of experience', 'US']);

    // Admin Listener
    const listenerHash = await bcrypt.hash('Listener123!', 10);
    await client.query(`
      INSERT INTO listeners (username, email, password_hash, first_name, last_name, country)
      VALUES ($1, $2, $3, $4, $5, $6)
      ON CONFLICT (email) DO NOTHING
    `, ['musiclover', 'listener@beatflow.com', listenerHash, 'Maria', 'Santos', 'US']);

    // Admin Label (uses artists table with a label-like profile)
    const labelHash = await bcrypt.hash('Label123!', 10);
    await client.query(`
      INSERT INTO artists (stage_name, first_name, last_name, email, password_hash, genre_id, bio, country)
      VALUES ($1, $2, $3, $4, $5, 2, $6, $7)
      ON CONFLICT (email) DO NOTHING
    `, ['Nova Records', 'Nova', 'Records', 'label@beatflow.com', labelHash, 'Independent record label focused on emerging artists', 'US']);

    // Give admin listener a subscription
    const listenerResult = await client.query(`SELECT id FROM listeners WHERE email = 'listener@beatflow.com'`);
    if (listenerResult.rows.length > 0) {
      const listenerId = listenerResult.rows[0].id;
      await client.query(`
        INSERT INTO subscriptions (listener_id, plan, status, expires_at)
        VALUES ($1, 'premium', 'active', NOW() + INTERVAL '1 year')
        ON CONFLICT DO NOTHING
      `, [listenerId]);
    }

    await client.query('COMMIT');
    console.log('Database seeded successfully!');
  } catch (err) {
    await client.query('ROLLBACK');
    console.error('Seed failed:', err);
    throw err;
  } finally {
    client.release();
  }
}

module.exports = { seed };
