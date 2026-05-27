-- ============================================================
-- DeepInsight Starter Suite — Migration 05: Report Versions
-- ============================================================

CREATE TABLE IF NOT EXISTS public.report_documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    dataset_id UUID REFERENCES public.datasets(id) ON DELETE SET NULL,
    title TEXT NOT NULL,
    content_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    version INTEGER DEFAULT 1,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.report_revisions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    report_id UUID NOT NULL REFERENCES public.report_documents(id) ON DELETE CASCADE,
    instruction TEXT NOT NULL,
    diff JSONB,
    version INTEGER NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_reports_user ON public.report_documents(user_id);
CREATE INDEX idx_revisions_report ON public.report_revisions(report_id);

ALTER TABLE public.report_documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.report_revisions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can manage own reports"
    ON public.report_documents FOR ALL
    USING (auth.uid() = user_id);

-- Cannot easily join for RLS on revisions, so we allow if user can select report
CREATE POLICY "Users can view own report revisions"
    ON public.report_revisions FOR SELECT
    USING (
        report_id IN (
            SELECT id FROM public.report_documents WHERE user_id = auth.uid()
        )
    );
