"""Constants and enumerations for de test framework."""

class MusicGenres:
    ROCK = 1
    POP = 2
    HIP_HOP = 3
    ELECTRONIC = 4
    JAZZ = 5
    CLASSICAL = 6
    RNB = 7
    COUNTRY = 8
    LATIN = 9
    METAL = 10
    ALL = [ROCK, POP, HIP_HOP, ELECTRONIC, JAZZ, CLASSICAL, RNB, COUNTRY, LATIN, METAL]


class AlbumStatus:
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    ALL = [DRAFT, PUBLISHED]
    TERMINAL = [ARCHIVED]

class SubscriptionsPlans:
    FREE = "free"
    BASIC = "basic"
    PREMIUM = "premium"

class SubscriptionsStatus:
    ACTIVE = "active"
    PAUSED = "paused"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    ALL = [ACTIVE, PAUSED]
    TERMINAL = [CANCELLED, EXPIRED]

class RoyaltiesStatus:
    PENDING = "pending"
    FAILED = "failed"
    PROCESSING = "processing"
    PAID = "paid"
    ALL = [PENDING, FAILED, PROCESSING]
    TERMINAL = [PAID]

class LicenseStatus:
    REQUESTED = "requested"
    APPROVED = "approved"
    REVOKED = "revoked"
    ACTIVE = "active"
    EXPIRED = "expired"
    ALL = [REQUESTED, APPROVED, ACTIVE]
    TERMINAL = [REVOKED, EXPIRED]

class StatusCodes:
    OK = 200
    CREATED = 201
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    CONFLICT = 409
    INTERNAL_ERROR = 500

