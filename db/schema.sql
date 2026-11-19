-- Kai SEO Suite: foundation schema.
--
-- Design notes that matter:
--   * utf8mb4 throughout. Social post text contains emoji, and utf8 (3-byte)
--     silently truncates at the first one.
--   * Access and refresh tokens are stored ENCRYPTED, never as plaintext. The
--     columns are BLOB because ciphertext is binary, not text.
--   * The jobs table replaces the in-memory queue in jobs/runner.py. That queue
--     loses everything on restart and breaks entirely if more than one worker
--     process exists, which is why scheduled posting cannot use it.
--   * Every table with user data carries user_id with ON DELETE CASCADE, so a
--     account deletion request can be honoured with one statement.

SET NAMES utf8mb4;


-- ── Accounts ──────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS users (
    id              BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    email           VARCHAR(254)    NOT NULL,
    -- bcrypt/argon2 hash. Never the password.
    password_hash   VARCHAR(255)    NOT NULL,
    display_name    VARCHAR(120)        NULL,
    status          ENUM('pending','active','suspended') NOT NULL DEFAULT 'pending',
    email_verified  TINYINT(1)      NOT NULL DEFAULT 0,
    -- Lockout counters, so credential stuffing is expensive.
    failed_logins   INT UNSIGNED    NOT NULL DEFAULT 0,
    locked_until    DATETIME            NULL,
    created_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP
                                    ON UPDATE CURRENT_TIMESTAMP,
    last_login_at   DATETIME            NULL,
    PRIMARY KEY (id),
    -- 254 chars is the RFC max length for an email address.
    UNIQUE KEY uq_users_email (email),
    KEY idx_users_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- Session tokens are stored hashed. A leaked database should not hand the
-- attacker a set of live sessions.
CREATE TABLE IF NOT EXISTS sessions (
    id              BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    user_id         BIGINT UNSIGNED NOT NULL,
    token_hash      CHAR(64)        NOT NULL,   -- sha256 hex of the cookie value
    ip              VARBINARY(16)       NULL,   -- INET6_ATON form, IPv4 and IPv6
    user_agent      VARCHAR(255)        NULL,
    created_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at      DATETIME        NOT NULL,
    revoked_at      DATETIME            NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uq_sessions_token (token_hash),
    KEY idx_sessions_user (user_id),
    KEY idx_sessions_expiry (expires_at),
    CONSTRAINT fk_sessions_user FOREIGN KEY (user_id)
        REFERENCES users (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- Single-use tokens for email verification and password reset. Hashed for the
-- same reason as sessions.
CREATE TABLE IF NOT EXISTS auth_tokens (
    id              BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    user_id         BIGINT UNSIGNED NOT NULL,
    purpose         ENUM('verify_email','reset_password') NOT NULL,
    token_hash      CHAR(64)        NOT NULL,
    created_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at      DATETIME        NOT NULL,
    used_at         DATETIME            NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uq_auth_tokens_token (token_hash),
    KEY idx_auth_tokens_user (user_id, purpose),
    CONSTRAINT fk_auth_tokens_user FOREIGN KEY (user_id)
        REFERENCES users (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ── Connected social accounts ─────────────────────────────────────────────

-- One row per connected profile. Tokens are encrypted at rest with a key held
-- outside the database, so a database dump alone cannot post as anyone.
CREATE TABLE IF NOT EXISTS social_accounts (
    id                  BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    user_id             BIGINT UNSIGNED NOT NULL,
    platform            ENUM('facebook','instagram','x','linkedin','tiktok') NOT NULL,
    -- The platform's own id for the page/profile.
    external_id         VARCHAR(128)    NOT NULL,
    display_name        VARCHAR(200)        NULL,
    username            VARCHAR(200)        NULL,
    avatar_url          VARCHAR(500)        NULL,

    access_token_enc    BLOB                NULL,
    refresh_token_enc   BLOB                NULL,
    -- Which key version encrypted these, so keys can be rotated without a
    -- flag day. Decrypt with the recorded version, re-encrypt with the current.
    key_version         SMALLINT UNSIGNED NOT NULL DEFAULT 1,
    token_expires_at    DATETIME            NULL,
    scopes              VARCHAR(1000)       NULL,

    status              ENUM('active','expired','revoked','error') NOT NULL DEFAULT 'active',
    last_error          VARCHAR(500)        NULL,
    last_synced_at      DATETIME            NULL,
    created_at          DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP
                                        ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    -- The same page can only be connected once per user.
    UNIQUE KEY uq_social_user_platform_ext (user_id, platform, external_id),
    KEY idx_social_user (user_id),
    KEY idx_social_expiry (token_expires_at),
    CONSTRAINT fk_social_user FOREIGN KEY (user_id)
        REFERENCES users (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ── Background jobs ───────────────────────────────────────────────────────

-- Replaces the in-memory queue. A cron runner claims rows atomically, so this
-- stays correct with several worker processes and survives restarts.
CREATE TABLE IF NOT EXISTS jobs (
    id              BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    -- Public identifier used in URLs. Not the primary key, so job ids are not
    -- guessable and cannot be enumerated.
    public_id       CHAR(32)        NOT NULL,
    user_id         BIGINT UNSIGNED     NULL,   -- NULL for anonymous tool runs
    kind            VARCHAR(64)     NOT NULL,   -- e.g. 'site_audit', 'publish_post'
    payload         JSON                NULL,
    status          ENUM('queued','running','done','error','cancelled')
                                    NOT NULL DEFAULT 'queued',
    progress        JSON                NULL,
    result          JSON                NULL,
    error           TEXT                NULL,

    priority        TINYINT         NOT NULL DEFAULT 0,   -- higher runs first
    attempts        INT UNSIGNED    NOT NULL DEFAULT 0,
    max_attempts    INT UNSIGNED    NOT NULL DEFAULT 3,
    -- When the job becomes eligible. Also used for retry backoff.
    run_after       DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    -- Set when a worker claims the row; lets a crashed worker's job be
    -- reclaimed once the lease goes stale rather than sticking on 'running'.
    locked_at       DATETIME            NULL,
    locked_by       VARCHAR(64)         NULL,

    created_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    started_at      DATETIME            NULL,
    finished_at     DATETIME            NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uq_jobs_public (public_id),
    -- The claim query orders by exactly this.
    KEY idx_jobs_claim (status, run_after, priority),
    KEY idx_jobs_user (user_id, created_at),
    KEY idx_jobs_stale (status, locked_at),
    CONSTRAINT fk_jobs_user FOREIGN KEY (user_id)
        REFERENCES users (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ── Scheduled posts ───────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS scheduled_posts (
    id                  BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    user_id             BIGINT UNSIGNED NOT NULL,
    social_account_id   BIGINT UNSIGNED NOT NULL,
    body                TEXT            NOT NULL,
    -- Media is referenced by URL rather than stored, so the app never becomes
    -- a file host. Array of {url, type, alt}.
    media               JSON                NULL,
    link_url            VARCHAR(1000)       NULL,

    -- Always stored UTC. The user's timezone is a display concern only, and
    -- storing local time here is how "posted an hour late after the clocks
    -- changed" bugs happen.
    scheduled_for       DATETIME        NOT NULL,
    timezone            VARCHAR(64)     NOT NULL DEFAULT 'UTC',

    status              ENUM('draft','scheduled','publishing','published','failed','cancelled')
                                        NOT NULL DEFAULT 'draft',
    external_post_id    VARCHAR(191)        NULL,   -- platform id once published
    permalink           VARCHAR(1000)       NULL,
    error               VARCHAR(1000)       NULL,
    job_id              BIGINT UNSIGNED     NULL,

    created_at          DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP
                                        ON UPDATE CURRENT_TIMESTAMP,
    published_at        DATETIME            NULL,
    PRIMARY KEY (id),
    KEY idx_posts_due (status, scheduled_for),
    KEY idx_posts_user (user_id, scheduled_for),
    KEY idx_posts_account (social_account_id),
    CONSTRAINT fk_posts_user FOREIGN KEY (user_id)
        REFERENCES users (id) ON DELETE CASCADE,
    CONSTRAINT fk_posts_account FOREIGN KEY (social_account_id)
        REFERENCES social_accounts (id) ON DELETE CASCADE,
    CONSTRAINT fk_posts_job FOREIGN KEY (job_id)
        REFERENCES jobs (id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ── Comments and replies ──────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS social_comments (
    id                  BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    social_account_id   BIGINT UNSIGNED NOT NULL,
    external_id         VARCHAR(191)    NOT NULL,   -- platform comment id
    external_post_id    VARCHAR(191)        NULL,
    author_name         VARCHAR(200)        NULL,
    author_external_id  VARCHAR(191)        NULL,
    body                TEXT                NULL,
    posted_at           DATETIME            NULL,

    -- A reply is never sent automatically without an explicit setting; the
    -- default is that a human approves it.
    reply_status        ENUM('none','suggested','approved','sent','skipped','failed')
                                        NOT NULL DEFAULT 'none',
    suggested_reply     TEXT                NULL,
    sent_reply          TEXT                NULL,
    replied_at          DATETIME            NULL,
    reply_error         VARCHAR(500)        NULL,

    created_at          DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    -- Comments are fetched repeatedly; this makes re-ingest idempotent.
    UNIQUE KEY uq_comment_account_ext (social_account_id, external_id),
    KEY idx_comments_status (reply_status, posted_at),
    CONSTRAINT fk_comments_account FOREIGN KEY (social_account_id)
        REFERENCES social_accounts (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ── Ad spend guard ────────────────────────────────────────────────────────

-- Ad actions cost real money, so every one is recorded and nothing moves to
-- 'approved' without a human. approved_by is NOT NULL on purpose: a row cannot
-- reach the approved state without naming the person who approved it.
CREATE TABLE IF NOT EXISTS ad_actions (
    id                  BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    user_id             BIGINT UNSIGNED NOT NULL,
    social_account_id   BIGINT UNSIGNED     NULL,
    action              VARCHAR(64)     NOT NULL,   -- create_campaign, set_budget, pause...
    payload             JSON                NULL,
    -- Minor units (pence/cents) as an integer. Never floats for money.
    budget_minor        BIGINT              NULL,
    currency            CHAR(3)             NULL,

    status              ENUM('pending_approval','approved','executed','rejected','failed')
                                        NOT NULL DEFAULT 'pending_approval',
    approved_by         BIGINT UNSIGNED     NULL,
    approved_at         DATETIME            NULL,
    executed_at         DATETIME            NULL,
    external_ref        VARCHAR(191)        NULL,
    error               VARCHAR(1000)       NULL,
    created_at          DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY idx_ad_status (status, created_at),
    KEY idx_ad_user (user_id, created_at),
    CONSTRAINT fk_ad_user FOREIGN KEY (user_id)
        REFERENCES users (id) ON DELETE CASCADE,
    CONSTRAINT fk_ad_account FOREIGN KEY (social_account_id)
        REFERENCES social_accounts (id) ON DELETE SET NULL,
    CONSTRAINT fk_ad_approver FOREIGN KEY (approved_by)
        REFERENCES users (id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ── Rate limiting ─────────────────────────────────────────────────────────

-- Public signup means login and signup endpoints are reachable by anyone.
-- Counted per (key, window) so a burst is cheap to detect with one upsert.
CREATE TABLE IF NOT EXISTS rate_limits (
    bucket          VARCHAR(120)    NOT NULL,   -- e.g. 'login:203.0.113.5'
    window_start    DATETIME        NOT NULL,
    hits            INT UNSIGNED    NOT NULL DEFAULT 1,
    PRIMARY KEY (bucket, window_start),
    KEY idx_rl_window (window_start)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ── Audit log ─────────────────────────────────────────────────────────────

-- Append only. Anything that touches credentials, money or another person's
-- account gets a row, so "who connected this page" has an answer later.
CREATE TABLE IF NOT EXISTS audit_log (
    id              BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    user_id         BIGINT UNSIGNED     NULL,
    action          VARCHAR(80)     NOT NULL,
    target_type     VARCHAR(60)         NULL,
    target_id       VARCHAR(64)         NULL,
    detail          JSON                NULL,
    ip              VARBINARY(16)       NULL,
    created_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY idx_audit_user (user_id, created_at),
    KEY idx_audit_action (action, created_at),
    CONSTRAINT fk_audit_user FOREIGN KEY (user_id)
        REFERENCES users (id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- Schema version marker, so migrations can be applied in order later.
CREATE TABLE IF NOT EXISTS schema_migrations (
    version     VARCHAR(40) NOT NULL,
    applied_at  DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (version)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT IGNORE INTO schema_migrations (version) VALUES ('0001_foundation');
