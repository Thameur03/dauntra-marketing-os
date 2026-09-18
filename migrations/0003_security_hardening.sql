-- ============================================================
-- DAUNTRA Marketing OS
-- Migration 0003 — Security hardening
-- ============================================================


-- ------------------------------------------------------------
-- Migration registry
--
-- Internal infrastructure metadata.
-- It must not be accessible through application/API roles.
--
-- RLS is enabled with no application policies.
-- Explicit privilege revocation adds a second protection layer.
-- ------------------------------------------------------------

ALTER TABLE public.marketing_schema_migrations
    ENABLE ROW LEVEL SECURITY;


REVOKE ALL
ON TABLE public.marketing_schema_migrations
FROM PUBLIC;


REVOKE ALL
ON TABLE public.marketing_schema_migrations
FROM anon;


REVOKE ALL
ON TABLE public.marketing_schema_migrations
FROM authenticated;


REVOKE ALL
ON TABLE public.marketing_schema_migrations
FROM service_role;


COMMENT ON TABLE public.marketing_schema_migrations IS
'Internal DAUNTRA migration registry. Accessible only through privileged direct database administration.';
