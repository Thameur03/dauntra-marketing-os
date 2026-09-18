BEGIN;

-- ============================================================
-- PRIVATE MARKETING ASSET STORAGE
--
-- Final rendered images/videos will eventually be uploaded here.
--
-- This bucket stays PRIVATE.
-- Public social platforms will later receive either:
--   1. uploaded media through Postiz/provider APIs, or
--   2. temporary signed URLs when required.
--
-- We do NOT expose a permanent public asset bucket.
-- ============================================================

INSERT INTO storage.buckets (
    id,
    name,
    public,
    file_size_limit,
    allowed_mime_types
)
VALUES (
    'marketing-assets',
    'marketing-assets',
    FALSE,
    52428800,
    ARRAY[
        'image/jpeg',
        'image/png',
        'video/mp4',
        'audio/mpeg',
        'audio/mp4',
        'audio/wav'
    ]
)
ON CONFLICT (id)
DO UPDATE SET
    name = EXCLUDED.name,
    public = FALSE,
    file_size_limit = EXCLUDED.file_size_limit,
    allowed_mime_types = EXCLUDED.allowed_mime_types;

COMMIT;
