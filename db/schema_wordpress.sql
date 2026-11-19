-- WordPress autopilot: connected sites, generated posts, and audit runs.
--
-- Design notes:
--   * Application Passwords are stored ENCRYPTED, same as social tokens. A WP
--     application password can create and publish posts, so a database dump
--     alone must not be enough to use one.
--   * posts_published is a counter on the site row rather than a COUNT(*) at
--     read time, because the every-10-posts audit trigger checks it on every
--     publish and a counter makes that check free.
--   * Generated article bodies live in LONGTEXT: a 1,000-word article with
--     HTML runs well past the 64KB TEXT ceiling once headings and links are in.

SET NAMES utf8mb4;


CREATE TABLE IF NOT EXISTS wp_sites (
    id                  BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    user_id             BIGINT UNSIGNED NOT NULL,
    name                VARCHAR(200)        NULL,
    site_url            VARCHAR(500)    NOT NULL,   -- https://example.com
    wp_username         VARCHAR(200)    NOT NULL,
    -- WordPress Application Password (WP 5.6+), never the account password.
    app_password_enc    BLOB            NOT NULL,
    key_version         SMALLINT UNSIGNED NOT NULL DEFAULT 1,

    -- Niche drives topic research. Detected on connect, editable by the user.
    niche               VARCHAR(300)        NULL,
    audience            VARCHAR(300)        NULL,
    tone                VARCHAR(120)        NULL,
    -- Site's own categories/tags, cached from the REST API so the generator can
    -- assign real ones instead of inventing them.
    taxonomy_cache      JSON                NULL,
    -- Slug + title of existing posts, used to build genuine internal links.
    link_index          JSON                NULL,
    link_index_at       DATETIME            NULL,

    autopilot_enabled   TINYINT(1)      NOT NULL DEFAULT 0,
    posts_per_week      TINYINT UNSIGNED NOT NULL DEFAULT 2,
    min_words           SMALLINT UNSIGNED NOT NULL DEFAULT 1000,
    publish_status      ENUM('draft','future','publish') NOT NULL DEFAULT 'future',

    -- Every 10th published post triggers an audit of what came before.
    posts_published     INT UNSIGNED    NOT NULL DEFAULT 0,
    audit_every         TINYINT UNSIGNED NOT NULL DEFAULT 10,
    last_audit_at       DATETIME            NULL,
    last_audit_post_no  INT UNSIGNED    NOT NULL DEFAULT 0,

    status              ENUM('active','error','paused') NOT NULL DEFAULT 'active',
    last_error          VARCHAR(500)        NULL,
    last_checked_at     DATETIME            NULL,
    created_at          DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP
                                        ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uq_wp_user_site (user_id, site_url),
    KEY idx_wp_user (user_id),
    KEY idx_wp_autopilot (autopilot_enabled, status),
    CONSTRAINT fk_wp_user FOREIGN KEY (user_id)
        REFERENCES users (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


CREATE TABLE IF NOT EXISTS wp_posts (
    id                  BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    user_id             BIGINT UNSIGNED NOT NULL,
    wp_site_id          BIGINT UNSIGNED NOT NULL,

    title               VARCHAR(300)    NOT NULL,
    slug                VARCHAR(300)        NULL,
    body_html           LONGTEXT            NULL,
    excerpt             VARCHAR(500)        NULL,
    meta_description    VARCHAR(320)        NULL,
    primary_keyword     VARCHAR(200)        NULL,
    secondary_keywords  JSON                NULL,
    -- Which existing posts this article links to, so the audit can verify the
    -- links still resolve after the fact.
    internal_links      JSON                NULL,
    sources             JSON                NULL,   -- research citations

    word_count          INT UNSIGNED    NOT NULL DEFAULT 0,
    -- Sequence number within the site, so "every 10th post" is unambiguous
    -- even if posts are deleted.
    post_no             INT UNSIGNED        NULL,

    status              ENUM('drafting','ready','scheduled','published','failed','corrected')
                                        NOT NULL DEFAULT 'drafting',
    scheduled_for       DATETIME            NULL,   -- always UTC
    published_at        DATETIME            NULL,
    wp_post_id          BIGINT UNSIGNED     NULL,   -- the ID WordPress assigned
    permalink           VARCHAR(1000)       NULL,
    error               VARCHAR(1000)       NULL,
    job_id              BIGINT UNSIGNED     NULL,

    -- Token spend for this article, so cost per post is answerable.
    input_tokens        INT UNSIGNED    NOT NULL DEFAULT 0,
    output_tokens       INT UNSIGNED    NOT NULL DEFAULT 0,

    created_at          DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP
                                        ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY idx_wpp_site (wp_site_id, created_at),
    KEY idx_wpp_user (user_id, created_at),
    KEY idx_wpp_due (status, scheduled_for),
    KEY idx_wpp_seq (wp_site_id, post_no),
    CONSTRAINT fk_wpp_user FOREIGN KEY (user_id)
        REFERENCES users (id) ON DELETE CASCADE,
    CONSTRAINT fk_wpp_site FOREIGN KEY (wp_site_id)
        REFERENCES wp_sites (id) ON DELETE CASCADE,
    CONSTRAINT fk_wpp_job FOREIGN KEY (job_id)
        REFERENCES jobs (id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- Topic queue. Researched ahead of time so the publisher never has to invent a
-- subject at publish time, and so duplicates can be checked before writing.
CREATE TABLE IF NOT EXISTS wp_topics (
    id                  BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    wp_site_id          BIGINT UNSIGNED NOT NULL,
    title               VARCHAR(300)    NOT NULL,
    primary_keyword     VARCHAR(200)        NULL,
    angle               VARCHAR(500)        NULL,
    rationale           VARCHAR(1000)       NULL,
    -- Guards against writing the same article twice, which is the main failure
    -- mode of an unattended content pipeline.
    dedupe_key          VARCHAR(191)    NOT NULL,
    status              ENUM('queued','writing','used','rejected') NOT NULL DEFAULT 'queued',
    priority            TINYINT         NOT NULL DEFAULT 0,
    created_at          DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uq_topic_site_key (wp_site_id, dedupe_key),
    KEY idx_topic_next (wp_site_id, status, priority),
    CONSTRAINT fk_topic_site FOREIGN KEY (wp_site_id)
        REFERENCES wp_sites (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- One row per audit run (fires every `audit_every` published posts).
CREATE TABLE IF NOT EXISTS wp_audits (
    id                  BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    wp_site_id          BIGINT UNSIGNED NOT NULL,
    user_id             BIGINT UNSIGNED NOT NULL,
    triggered_at_post   INT UNSIGNED    NOT NULL,   -- posts_published at trigger
    posts_checked       INT UNSIGNED    NOT NULL DEFAULT 0,
    issues_found        INT UNSIGNED    NOT NULL DEFAULT 0,
    issues_fixed        INT UNSIGNED    NOT NULL DEFAULT 0,
    findings            JSON                NULL,
    status              ENUM('running','done','error') NOT NULL DEFAULT 'running',
    error               VARCHAR(1000)       NULL,
    job_id              BIGINT UNSIGNED     NULL,
    created_at          DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    finished_at         DATETIME            NULL,
    PRIMARY KEY (id),
    KEY idx_wpaudit_site (wp_site_id, created_at),
    -- Names are prefixed wpaudit_ because InnoDB foreign-key names must be
    -- unique across the whole database, and audit_log already owns fk_audit_*.
    CONSTRAINT fk_wpaudit_site FOREIGN KEY (wp_site_id)
        REFERENCES wp_sites (id) ON DELETE CASCADE,
    CONSTRAINT fk_wpaudit_user FOREIGN KEY (user_id)
        REFERENCES users (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT IGNORE INTO schema_migrations (version) VALUES ('0002_wordpress');
