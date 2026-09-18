BEGIN;

CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- ============================================================
-- GENERIC UPDATED_AT TRIGGER
-- ============================================================

CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$;


-- ============================================================
-- SUBJECTS
-- One founder-supplied marketing idea.
-- ============================================================

CREATE TABLE subjects (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

  subject_text TEXT NOT NULL,
  note TEXT,

  source TEXT NOT NULL DEFAULT 'founder'
    CHECK (source IN ('founder', 'analytics', 'research', 'manual', 'other')),

  content_family TEXT
    CHECK (
      content_family IS NULL OR
      content_family IN ('C01', 'C02', 'C03', 'C04')
    ),

  market TEXT NOT NULL DEFAULT 'GLOBAL',
  language TEXT NOT NULL DEFAULT 'en',

  status TEXT NOT NULL DEFAULT 'QUEUED'
    CHECK (
      status IN (
        'QUEUED',
        'RESEARCHING',
        'GENERATING',
        'READY',
        'DONE',
        'ERROR',
        'CANCELLED'
      )
    ),

  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_subjects_status
  ON subjects(status);

CREATE INDEX idx_subjects_created_at
  ON subjects(created_at DESC);

CREATE TRIGGER trg_subjects_updated_at
BEFORE UPDATE ON subjects
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();


-- ============================================================
-- RESEARCH PACKETS
--
-- One factual evidence package generated before platform copy.
--
-- packet_json is validated by Pydantic in application code.
-- ============================================================

CREATE TABLE research_packets (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

  subject_id UUID NOT NULL
    REFERENCES subjects(id)
    ON DELETE CASCADE,

  status TEXT NOT NULL DEFAULT 'DRAFT'
    CHECK (
      status IN (
        'DRAFT',
        'READY',
        'NEEDS_REVIEW',
        'REJECTED',
        'ERROR'
      )
    ),

  packet_json JSONB NOT NULL,

  prompt_version TEXT NOT NULL,
  model TEXT NOT NULL,

  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_research_packets_subject_id
  ON research_packets(subject_id);

CREATE TRIGGER trg_research_packets_updated_at
BEFORE UPDATE ON research_packets
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();


-- ============================================================
-- CONTENT TESTS
--
-- Simple V1 experiment/test definition.
-- Not a Bayesian optimizer.
-- ============================================================

CREATE TABLE content_tests (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

  subject_id UUID NOT NULL
    REFERENCES subjects(id)
    ON DELETE CASCADE,

  research_packet_id UUID
    REFERENCES research_packets(id)
    ON DELETE SET NULL,

  hypothesis TEXT,

  independent_variable TEXT,
  primary_metric TEXT NOT NULL DEFAULT 'qualified_signups_per_1000_impressions',

  observation_window_hours INTEGER NOT NULL DEFAULT 72
    CHECK (observation_window_hours > 0),

  minimum_impressions INTEGER NOT NULL DEFAULT 0
    CHECK (minimum_impressions >= 0),

  minimum_clicks INTEGER NOT NULL DEFAULT 0
    CHECK (minimum_clicks >= 0),

  status TEXT NOT NULL DEFAULT 'ACTIVE'
    CHECK (
      status IN (
        'ACTIVE',
        'COMPLETE',
        'PAUSED',
        'CANCELLED'
      )
    ),

  decision TEXT
    CHECK (
      decision IS NULL OR
      decision IN (
        'DOUBLE_DOWN',
        'KEEP_TESTING',
        'PAUSE',
        'INSUFFICIENT_DATA'
      )
    ),

  decision_rationale TEXT,

  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_content_tests_subject_id
  ON content_tests(subject_id);

CREATE TRIGGER trg_content_tests_updated_at
BEFORE UPDATE ON content_tests
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();


-- ============================================================
-- CONTENT ITEMS
--
-- One platform-native generated output.
-- ============================================================

CREATE TABLE content_items (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

  subject_id UUID NOT NULL
    REFERENCES subjects(id)
    ON DELETE CASCADE,

  research_packet_id UUID
    REFERENCES research_packets(id)
    ON DELETE SET NULL,

  content_test_id UUID
    REFERENCES content_tests(id)
    ON DELETE SET NULL,

  variant_parent_id UUID
    REFERENCES content_items(id)
    ON DELETE SET NULL,

  platform TEXT NOT NULL
    CHECK (
      platform IN (
        'instagram',
        'tiktok',
        'x',
        'facebook',
        'reddit'
      )
    ),

  format TEXT NOT NULL
    CHECK (
      format IN (
        'carousel',
        'video',
        'text',
        'thread',
        'discussion',
        'image'
      )
    ),

  content_family TEXT NOT NULL
    CHECK (
      content_family IN ('C01', 'C02', 'C03', 'C04')
    ),

  market TEXT NOT NULL DEFAULT 'GLOBAL',
  language TEXT NOT NULL DEFAULT 'en',
  timezone_window TEXT,

  status TEXT NOT NULL DEFAULT 'DRAFT'
    CHECK (
      status IN (
        'DRAFT',
        'GENERATED',
        'QA_PENDING',
        'QA_FAILED',
        'NEEDS_HUMAN_REVIEW',
        'APPROVED',
        'READY_TO_PUBLISH',
        'SCHEDULED',
        'PUBLISHED',
        'REJECTED',
        'ERROR'
      )
    ),

  content_json JSONB NOT NULL,

  prompt_version TEXT NOT NULL,
  model TEXT NOT NULL,

  capability_manifest_version TEXT NOT NULL,
  brand_profile_version TEXT NOT NULL,
  content_strategy_version TEXT NOT NULL,

  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_content_items_subject_id
  ON content_items(subject_id);

CREATE INDEX idx_content_items_test_id
  ON content_items(content_test_id);

CREATE INDEX idx_content_items_platform_status
  ON content_items(platform, status);

CREATE TRIGGER trg_content_items_updated_at
BEFORE UPDATE ON content_items
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();


-- ============================================================
-- ASSETS
--
-- Rendered files live in object storage.
-- The database stores metadata and immutable object keys.
-- ============================================================

CREATE TABLE assets (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

  content_item_id UUID NOT NULL
    REFERENCES content_items(id)
    ON DELETE CASCADE,

  asset_type TEXT NOT NULL
    CHECK (
      asset_type IN (
        'image',
        'carousel_slide',
        'video',
        'audio',
        'thumbnail'
      )
    ),

  storage_bucket TEXT NOT NULL DEFAULT 'marketing-assets',
  storage_key TEXT NOT NULL,

  mime_type TEXT NOT NULL,

  width INTEGER
    CHECK (width IS NULL OR width > 0),

  height INTEGER
    CHECK (height IS NULL OR height > 0),

  duration_ms INTEGER
    CHECK (duration_ms IS NULL OR duration_ms >= 0),

  sha256 TEXT NOT NULL,

  render_profile TEXT,
  template_id TEXT,
  template_version TEXT,
  renderer_version TEXT,

  metadata_json JSONB NOT NULL DEFAULT '{}'::jsonb,

  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

  UNIQUE(storage_bucket, storage_key),
  UNIQUE(sha256, content_item_id, asset_type)
);

CREATE INDEX idx_assets_content_item_id
  ON assets(content_item_id);


-- ============================================================
-- QA RESULTS
--
-- One content item can have many QA gate results.
-- ============================================================

CREATE TABLE qa_results (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

  content_item_id UUID NOT NULL
    REFERENCES content_items(id)
    ON DELETE CASCADE,

  gate TEXT NOT NULL
    CHECK (
      gate IN (
        'SCHEMA',
        'PRODUCT_CAPABILITY',
        'FACTUAL',
        'HEALTH_CLAIM',
        'BRAND',
        'DUPLICATE',
        'VISUAL',
        'PLATFORM_FORMAT',
        'HUMAN_REVIEW'
      )
    ),

  result TEXT NOT NULL
    CHECK (
      result IN (
        'PASS',
        'FAIL',
        'WARNING',
        'NEEDS_REVIEW'
      )
    ),

  reason_code TEXT,
  message TEXT,

  evidence_json JSONB NOT NULL DEFAULT '{}'::jsonb,

  attempt INTEGER NOT NULL DEFAULT 1
    CHECK (attempt > 0),

  reviewer_type TEXT NOT NULL DEFAULT 'SYSTEM'
    CHECK (
      reviewer_type IN (
        'SYSTEM',
        'LLM',
        'HUMAN'
      )
    ),

  reviewer TEXT,

  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_qa_results_content_item_id
  ON qa_results(content_item_id);

CREATE INDEX idx_qa_results_gate_result
  ON qa_results(gate, result);


-- ============================================================
-- CAMPAIGNS / TRACKED LINKS
--
-- One content item may receive a tracked campaign code.
-- ============================================================

CREATE TABLE campaigns (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

  content_item_id UUID NOT NULL
    REFERENCES content_items(id)
    ON DELETE CASCADE,

  campaign_code TEXT NOT NULL UNIQUE,

  destination_url TEXT NOT NULL,

  market TEXT NOT NULL DEFAULT 'GLOBAL',

  utm_source TEXT,
  utm_medium TEXT,
  utm_campaign TEXT,
  utm_content TEXT,

  is_active BOOLEAN NOT NULL DEFAULT TRUE,

  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_campaigns_content_item_id
  ON campaigns(content_item_id);


-- ============================================================
-- PUBLICATION JOBS
--
-- Idempotency is critical here.
-- ============================================================

CREATE TABLE publication_jobs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

  content_item_id UUID NOT NULL
    REFERENCES content_items(id)
    ON DELETE CASCADE,

  platform TEXT NOT NULL
    CHECK (
      platform IN (
        'instagram',
        'tiktok',
        'x',
        'facebook',
        'reddit'
      )
    ),

  provider TEXT NOT NULL DEFAULT 'postiz'
    CHECK (
      provider IN (
        'postiz',
        'manual',
        'native_api'
      )
    ),

  scheduled_at TIMESTAMPTZ,

  status TEXT NOT NULL DEFAULT 'PENDING'
    CHECK (
      status IN (
        'PENDING',
        'SUBMITTING',
        'SCHEDULED',
        'PUBLISHED',
        'FAILED',
        'UNKNOWN',
        'CANCELLED'
      )
    ),

  idempotency_key TEXT NOT NULL UNIQUE,

  provider_request_id TEXT,

  attempt_count INTEGER NOT NULL DEFAULT 0
    CHECK (attempt_count >= 0),

  last_error TEXT,
  unknown_reason TEXT,

  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_publication_jobs_status
  ON publication_jobs(status);

CREATE INDEX idx_publication_jobs_schedule
  ON publication_jobs(scheduled_at);

CREATE INDEX idx_publication_jobs_content_item_id
  ON publication_jobs(content_item_id);

CREATE TRIGGER trg_publication_jobs_updated_at
BEFORE UPDATE ON publication_jobs
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();


-- ============================================================
-- POSTS
--
-- Represents a post known to exist at a provider/platform.
-- ============================================================

CREATE TABLE posts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

  publication_job_id UUID NOT NULL UNIQUE
    REFERENCES publication_jobs(id)
    ON DELETE CASCADE,

  content_item_id UUID NOT NULL
    REFERENCES content_items(id)
    ON DELETE CASCADE,

  platform TEXT NOT NULL,

  provider TEXT NOT NULL,

  provider_post_id TEXT,
  platform_post_url TEXT,

  published_at TIMESTAMPTZ,

  status TEXT NOT NULL DEFAULT 'PUBLISHED'
    CHECK (
      status IN (
        'SCHEDULED',
        'PUBLISHED',
        'DELETED',
        'FAILED',
        'UNKNOWN'
      )
    ),

  raw_provider_json JSONB NOT NULL DEFAULT '{}'::jsonb,

  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

  UNIQUE(provider, platform, provider_post_id)
);

CREATE INDEX idx_posts_content_item_id
  ON posts(content_item_id);

CREATE INDEX idx_posts_platform
  ON posts(platform);

CREATE TRIGGER trg_posts_updated_at
BEFORE UPDATE ON posts
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();


-- ============================================================
-- METRIC SNAPSHOTS
--
-- Append-only time series.
-- ============================================================

CREATE TABLE metric_snapshots (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

  post_id UUID NOT NULL
    REFERENCES posts(id)
    ON DELETE CASCADE,

  impressions BIGINT
    CHECK (impressions IS NULL OR impressions >= 0),

  reach BIGINT
    CHECK (reach IS NULL OR reach >= 0),

  views BIGINT
    CHECK (views IS NULL OR views >= 0),

  likes BIGINT
    CHECK (likes IS NULL OR likes >= 0),

  comments BIGINT
    CHECK (comments IS NULL OR comments >= 0),

  shares BIGINT
    CHECK (shares IS NULL OR shares >= 0),

  saves BIGINT
    CHECK (saves IS NULL OR saves >= 0),

  watch_time_ms BIGINT
    CHECK (watch_time_ms IS NULL OR watch_time_ms >= 0),

  average_watch_time_ms BIGINT
    CHECK (average_watch_time_ms IS NULL OR average_watch_time_ms >= 0),

  completion_rate NUMERIC(7,6)
    CHECK (
      completion_rate IS NULL OR
      (completion_rate >= 0 AND completion_rate <= 1)
    ),

  profile_visits BIGINT
    CHECK (profile_visits IS NULL OR profile_visits >= 0),

  followers_gained BIGINT
    CHECK (followers_gained IS NULL OR followers_gained >= 0),

  raw_metrics_json JSONB NOT NULL DEFAULT '{}'::jsonb,

  captured_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_metric_snapshots_post_time
  ON metric_snapshots(post_id, captured_at DESC);


-- ============================================================
-- CLICK EVENTS
--
-- Visitor identifiers are anonymous/pseudonymous.
-- ============================================================

CREATE TABLE click_events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

  campaign_id UUID NOT NULL
    REFERENCES campaigns(id)
    ON DELETE CASCADE,

  click_id UUID NOT NULL DEFAULT gen_random_uuid() UNIQUE,

  visitor_id TEXT,

  referrer TEXT,
  landing_url TEXT,

  user_agent_family TEXT,

  metadata_json JSONB NOT NULL DEFAULT '{}'::jsonb,

  clicked_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_click_events_campaign_id
  ON click_events(campaign_id);

CREATE INDEX idx_click_events_visitor_id
  ON click_events(visitor_id);

CREATE INDEX idx_click_events_clicked_at
  ON click_events(clicked_at DESC);


-- ============================================================
-- CONVERSIONS
--
-- Does NOT require email storage.
-- ============================================================

CREATE TABLE conversions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

  conversion_id TEXT NOT NULL UNIQUE,

  conversion_type TEXT NOT NULL
    CHECK (
      conversion_type IN (
        'WAITLIST_SIGNUP',
        'INSTALL',
        'TRIAL',
        'SUBSCRIPTION'
      )
    ),

  qualified BOOLEAN NOT NULL DEFAULT FALSE,

  visitor_id TEXT,

  first_touch_click_id UUID
    REFERENCES click_events(click_id)
    ON DELETE SET NULL,

  last_touch_click_id UUID
    REFERENCES click_events(click_id)
    ON DELETE SET NULL,

  first_touch_campaign_id UUID
    REFERENCES campaigns(id)
    ON DELETE SET NULL,

  last_touch_campaign_id UUID
    REFERENCES campaigns(id)
    ON DELETE SET NULL,

  attribution_status TEXT NOT NULL DEFAULT 'UNKNOWN'
    CHECK (
      attribution_status IN (
        'ATTRIBUTED',
        'DIRECT',
        'UNKNOWN'
      )
    ),

  metadata_json JSONB NOT NULL DEFAULT '{}'::jsonb,

  converted_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_conversions_type_time
  ON conversions(conversion_type, converted_at DESC);

CREATE INDEX idx_conversions_first_campaign
  ON conversions(first_touch_campaign_id);

CREATE INDEX idx_conversions_last_campaign
  ON conversions(last_touch_campaign_id);


-- ============================================================
-- DECISIONS
--
-- Human/system conclusions based on results.
-- ============================================================

CREATE TABLE decisions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

  subject_id UUID
    REFERENCES subjects(id)
    ON DELETE CASCADE,

  content_test_id UUID
    REFERENCES content_tests(id)
    ON DELETE CASCADE,

  content_item_id UUID
    REFERENCES content_items(id)
    ON DELETE CASCADE,

  decision TEXT NOT NULL
    CHECK (
      decision IN (
        'DOUBLE_DOWN',
        'KEEP_TESTING',
        'PAUSE',
        'INSUFFICIENT_DATA'
      )
    ),

  rationale TEXT NOT NULL,

  decided_by TEXT NOT NULL DEFAULT 'SYSTEM'
    CHECK (
      decided_by IN (
        'SYSTEM',
        'HUMAN'
      )
    ),

  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

  CHECK (
    subject_id IS NOT NULL OR
    content_test_id IS NOT NULL OR
    content_item_id IS NOT NULL
  )
);


-- ============================================================
-- SYSTEM ERRORS
--
-- payload_json must be sanitized before insertion.
-- ============================================================

CREATE TABLE system_errors (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

  source TEXT NOT NULL,

  entity_type TEXT,
  entity_id UUID,

  error_code TEXT,
  error_message TEXT NOT NULL,

  payload_json JSONB NOT NULL DEFAULT '{}'::jsonb,

  status TEXT NOT NULL DEFAULT 'OPEN'
    CHECK (
      status IN (
        'OPEN',
        'RETRIED',
        'RESOLVED',
        'IGNORED'
      )
    ),

  retry_count INTEGER NOT NULL DEFAULT 0
    CHECK (retry_count >= 0),

  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  resolved_at TIMESTAMPTZ
);

CREATE INDEX idx_system_errors_status
  ON system_errors(status);

CREATE INDEX idx_system_errors_source
  ON system_errors(source);


-- ============================================================
-- PRIVATE-BY-DEFAULT SUPABASE SECURITY
--
-- Service-role/server-side access bypasses RLS.
-- No anonymous browser policies are created in V1.
-- ============================================================

ALTER TABLE subjects ENABLE ROW LEVEL SECURITY;
ALTER TABLE research_packets ENABLE ROW LEVEL SECURITY;
ALTER TABLE content_tests ENABLE ROW LEVEL SECURITY;
ALTER TABLE content_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE assets ENABLE ROW LEVEL SECURITY;
ALTER TABLE qa_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE campaigns ENABLE ROW LEVEL SECURITY;
ALTER TABLE publication_jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE posts ENABLE ROW LEVEL SECURITY;
ALTER TABLE metric_snapshots ENABLE ROW LEVEL SECURITY;
ALTER TABLE click_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversions ENABLE ROW LEVEL SECURITY;
ALTER TABLE decisions ENABLE ROW LEVEL SECURITY;
ALTER TABLE system_errors ENABLE ROW LEVEL SECURITY;


COMMIT;
