-- ============================================================
-- DeepInsight Starter Suite — Supabase Database Schema
-- ============================================================
-- Run this in the Supabase SQL Editor to create all tables,
-- indexes, and Row Level Security policies.
-- ============================================================

-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ────────────────────────────────────────────────────────────
-- 1. PROFILES
-- ────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS public.profiles (
    id              UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    display_name    TEXT,
    avatar_url      TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own profile"
    ON public.profiles FOR SELECT
    USING (auth.uid() = id);

CREATE POLICY "Users can update own profile"
    ON public.profiles FOR UPDATE
    USING (auth.uid() = id);

CREATE POLICY "Users can insert own profile"
    ON public.profiles FOR INSERT
    WITH CHECK (auth.uid() = id);

-- Auto-create profile on signup
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.profiles (id, display_name)
    VALUES (NEW.id, NEW.raw_user_meta_data->>'display_name');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- ────────────────────────────────────────────────────────────
-- 2. DATASETS
-- ────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS public.datasets (
    id                UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id           UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    file_name         TEXT NOT NULL,
    file_type         TEXT NOT NULL,
    storage_path      TEXT NOT NULL,
    row_count         INTEGER DEFAULT 0,
    column_count      INTEGER DEFAULT 0,
    null_percentage   DOUBLE PRECISION DEFAULT 0.0,
    quality_score     INTEGER DEFAULT 0,
    column_metadata   JSONB DEFAULT '[]'::JSONB,
    created_at        TIMESTAMPTZ DEFAULT NOW(),
    updated_at        TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_datasets_user_id ON public.datasets(user_id);

ALTER TABLE public.datasets ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own datasets"
    ON public.datasets FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own datasets"
    ON public.datasets FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete own datasets"
    ON public.datasets FOR DELETE
    USING (auth.uid() = user_id);

-- ────────────────────────────────────────────────────────────
-- 3. ANALYSIS RESULTS
-- ────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS public.analysis_results (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    dataset_id      UUID NOT NULL REFERENCES public.datasets(id) ON DELETE CASCADE,
    analysis_type   TEXT NOT NULL,
    results         JSONB DEFAULT '{}'::JSONB,
    charts          JSONB DEFAULT '[]'::JSONB,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_analysis_dataset_id ON public.analysis_results(dataset_id);
CREATE INDEX idx_analysis_type ON public.analysis_results(dataset_id, analysis_type);

ALTER TABLE public.analysis_results ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own analysis results"
    ON public.analysis_results FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.datasets
            WHERE datasets.id = analysis_results.dataset_id
            AND datasets.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can insert own analysis results"
    ON public.analysis_results FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.datasets
            WHERE datasets.id = analysis_results.dataset_id
            AND datasets.user_id = auth.uid()
        )
    );

-- ────────────────────────────────────────────────────────────
-- 4. CHAT SESSIONS
-- ────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS public.chat_sessions (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    dataset_id      UUID NOT NULL REFERENCES public.datasets(id) ON DELETE CASCADE,
    user_id         UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    title           TEXT DEFAULT 'New Chat',
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_chat_sessions_user ON public.chat_sessions(user_id);
CREATE INDEX idx_chat_sessions_dataset ON public.chat_sessions(dataset_id);

ALTER TABLE public.chat_sessions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own chat sessions"
    ON public.chat_sessions FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own chat sessions"
    ON public.chat_sessions FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- ────────────────────────────────────────────────────────────
-- 5. CHAT MESSAGES
-- ────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS public.chat_messages (
    id                    UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id            UUID NOT NULL REFERENCES public.chat_sessions(id) ON DELETE CASCADE,
    role                  TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
    content               TEXT NOT NULL,
    follow_up_questions   JSONB DEFAULT '[]'::JSONB,
    created_at            TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_chat_messages_session ON public.chat_messages(session_id);

ALTER TABLE public.chat_messages ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own chat messages"
    ON public.chat_messages FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.chat_sessions
            WHERE chat_sessions.id = chat_messages.session_id
            AND chat_sessions.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can insert own chat messages"
    ON public.chat_messages FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.chat_sessions
            WHERE chat_sessions.id = chat_messages.session_id
            AND chat_sessions.user_id = auth.uid()
        )
    );

-- ────────────────────────────────────────────────────────────
-- 6. TRAINED MODELS
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

CREATE INDEX idx_trained_models_user ON public.trained_models(user_id);
CREATE INDEX idx_trained_models_dataset ON public.trained_models(dataset_id);

ALTER TABLE public.trained_models ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can manage own models"
    ON public.trained_models FOR ALL
    USING (auth.uid() = user_id);

-- ────────────────────────────────────────────────────────────
-- 7. MODEL METRICS
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

CREATE INDEX idx_model_metrics_model ON public.model_metrics(model_id);

ALTER TABLE public.model_metrics ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own metrics"
    ON public.model_metrics FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.trained_models
            WHERE trained_models.id = model_metrics.model_id
            AND trained_models.user_id = auth.uid()
        )
    );

-- ────────────────────────────────────────────────────────────
-- 8. PREDICTION LOGS
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

CREATE POLICY "Users can view own prediction logs"
    ON public.prediction_logs FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.trained_models
            WHERE trained_models.id = prediction_logs.model_id
            AND trained_models.user_id = auth.uid()
        )
    );

-- ────────────────────────────────────────────────────────────
-- STORAGE BUCKET POLICY
-- ────────────────────────────────────────────────────────────
-- Run these in the Supabase dashboard under Storage > Policies:
--
-- INSERT policy: auth.uid() IS NOT NULL
-- SELECT policy: auth.uid()::text = (storage.foldername(name))[1]
-- DELETE policy: auth.uid()::text = (storage.foldername(name))[1]
-- ────────────────────────────────────────────────────────────
