-- ============================================================
-- DeepInsight Starter Suite — Migration 06: Connectors
-- ============================================================

CREATE TABLE IF NOT EXISTS public.saved_connections (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    org_id UUID REFERENCES public.organizations(id) ON DELETE CASCADE,
    connector_type TEXT NOT NULL, -- 'postgres', 'mysql', 'snowflake', 'bigquery', 'google_analytics'
    name TEXT NOT NULL,
    config_encrypted TEXT NOT NULL, -- Encrypted JSON string of connection params
    last_sync TIMESTAMPTZ,
    status TEXT DEFAULT 'active', -- 'active', 'failing'
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_connections_user ON public.saved_connections(user_id);
CREATE INDEX idx_connections_org ON public.saved_connections(org_id);

ALTER TABLE public.saved_connections ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can manage own connections"
    ON public.saved_connections FOR ALL
    USING (auth.uid() = user_id);

CREATE POLICY "Org members can view org connections"
    ON public.saved_connections FOR SELECT
    USING (
        org_id IN (
            SELECT org_id FROM public.profiles WHERE id = auth.uid()
        )
    );
