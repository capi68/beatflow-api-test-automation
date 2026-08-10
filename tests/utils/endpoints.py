"""Centralized API endpoint definitions."""

class ArtistEndpoints:
    BASE = "/artists"
    DETAIL = "/artists/{artist_id}"
    LOGIN = "/artists/login"

class ListenerEndpoints:
    BASE = "/listeners"
    DETAIL = "/listeners/{listener_id}"
    LOGIN = "/listeners/login"

class AlbumEndpoints:
    BASE = "/albums"
    DETAIL = "/albums/{album_id}"

class GenresEndpoints:
    BASE = "/genres"
    DETAIL = "/genres/{genre_id}"

class TracksEndpoints:
    BASE = "/tracks"
    DETAIL = "/tracks/{track_id}"

class PlaylistEndpoints:
    BASE = "/playlists"
    DETAIL = "/playlists/{playlist_id}"

class PlaylistTracksEndpoints:
    BASE = "/playlist-tracks"
    DETAIL = "/playlist-tracks/{playlist_track_id}"

class StreamsEndpoints:
    BASE = "/streams"
    DETAIL = "/streams/{stream_id}"

class RoyaltyEndpoints:
    BASE = "/royalties"
    DETAIL = "/royalties/{royalty_id}"

class LicenseEndpoints:
    BASE = "/licenses"
    DETAIL = "/licenses/{license_id}"

class SubscriptionEndpoints:
    BASE = "/subscriptions"
    DETAIL = "/subscriptions/{subscription_id}"