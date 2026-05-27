-- ============================================================
-- DeepInsight Starter Suite — Migration 07: Schedules
-- ============================================================

CREATE TABLE IF NOT EXISTS public.scheduled_jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    dataset_id UUID REFERENCES public.datasets(id) ON DELETE CASCADE,
    job_type TEXT NOT NULL, -- 'analysis', 'report_export', 'model_retrain'
    cron_expression TEXT NOT NULL,
    config JSONB DEFAULT '{}'::jsonb,
    enabled BOOLEAN DEFAULT true,
    last_run TIMESTAMPTZ,
    next_run TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_schedules_user ON public.scheduled_jobs(user_id);

ALTER TABLE public.scheduled_jobs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can manage own schedules"
    ON public.scheduled_jobs FOR ALL
    USING (auth.uid() = user_id);
