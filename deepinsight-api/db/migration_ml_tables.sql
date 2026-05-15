-- ============================================================
-- DeepInsight — ML Tables Migration
-- Run this in the Supabase SQL Editor to create the missing
-- ML-related tables: trained_models, model_metrics, prediction_logs
-- ============================================================

-- Enable UUID generation (safe to re-run)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ────────────────────────────────────────────────────────────
-- 1. TRAINED MODELS
-- ────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS public.trained_models (
    id                UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id           UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    dataset_id        UUID REFERENCES public.datasets(id) ON DELETE SET NULL,
    model_name        TEXT NOT NULL,
    problem_type      TEXT NOT NULL,
    storage_path      TEXT NOT NULL,
    training_time     DOUBLE PRECISION,
    created_at        TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_trained_models_user    ON public.trained_models(user_id);
CREATE INDEX IF NOT EXISTS idx_trained_models_dataset ON public.trained_models(dataset_id);

ALTER TABLE public.trained_models ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Users can manage own models" ON public.trained_models;
CREATE POLICY "Users can manage own models"
    ON public.trained_models FOR ALL
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

-- ────────────────────────────────────────────────────────────
-- 2. MODEL METRICS
-- ────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS public.model_metrics (
    id                UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    model_id          UUID NOT NULL REFERENCES public.trained_models(id) ON DELETE CASCADE,
    accuracy          DOUBLE PRECISION,
    precision_score   DOUBLE PRECISION,
    recall            DOUBLE PRECISION,
    f1_score          DOUBLE PRECISION,
    rmse              DOUBLE PRECISION,
    r2_score          DOUBLE PRECISION,
    metrics_json      JSONB DEFAULT '{}'::JSONB,
    created_at        TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_model_metrics_model ON public.model_metrics(model_id);

ALTER TABLE public.model_metrics ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Users can view own metrics" ON public.model_metrics;
CREATE POLICY "Users can view own metrics"
    ON public.model_metrics FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM public.trained_models
            WHERE trained_models.id = model_metrics.model_id
            AND trained_models.user_id = auth.uid()
        )
    )
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.trained_models
            WHERE trained_models.id = model_metrics.model_id
            AND trained_models.user_id = auth.uid()
        )
    );

-- ────────────────────────────────────────────────────────────
-- 3. PREDICTION LOGS
-- ────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS public.prediction_logs (
    id                UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    model_id          UUID NOT NULL REFERENCES public.trained_models(id) ON DELETE CASCADE,
    input_data        JSONB NOT NULL,
    prediction        JSONB NOT NULL,
    latency_ms        DOUBLE PRECISION,
    created_at        TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE public.prediction_logs ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Users can view own prediction logs" ON public.prediction_logs;
CREATE POLICY "Users can view own prediction logs"
    ON public.prediction_logs FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM public.trained_models
            WHERE trained_models.id = prediction_logs.model_id
            AND trained_models.user_id = auth.uid()
        )
    )
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.trained_models
            WHERE trained_models.id = prediction_logs.model_id
            AND trained_models.user_id = auth.uid()
        )
    );

-- ============================================================
-- Done! All 3 ML tables have been created.
-- ============================================================
