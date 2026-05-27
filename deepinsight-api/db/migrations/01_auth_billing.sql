-- ============================================================
-- DeepInsight Starter Suite — Migration 01: Auth, Billing, Limits
-- ============================================================

-- 1. Extend PROFILES table with Stripe and Trial Info
ALTER TABLE public.profiles 
ADD COLUMN IF NOT EXISTS stripe_customer_id TEXT UNIQUE,
ADD COLUMN IF NOT EXISTS subscription_plan TEXT DEFAULT 'free', -- 'free', 'starter', 'pro', 'enterprise'
ADD COLUMN IF NOT EXISTS subscription_status TEXT DEFAULT 'active', -- 'active', 'past_due', 'canceled', 'trialing'
ADD COLUMN IF NOT EXISTS trial_end TIMESTAMPTZ,
ADD COLUMN IF NOT EXISTS current_period_end TIMESTAMPTZ;

-- Function to set trial end date on new user creation
CREATE OR REPLACE FUNCTION public.handle_new_user_trial()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE public.profiles 
    SET trial_end = NOW() + INTERVAL '14 days'
    WHERE id = NEW.id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger to automatically set trial
DROP TRIGGER IF EXISTS on_auth_user_created_trial ON auth.users;
CREATE TRIGGER on_auth_user_created_trial
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user_trial();

-- 2. USAGE METRICS TABLE
CREATE TABLE IF NOT EXISTS public.usage_metrics (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id         UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    period_start    TIMESTAMPTZ NOT NULL,
    period_end      TIMESTAMPTZ NOT NULL,
    dataset_count   INTEGER DEFAULT 0,
    chat_tokens     INTEGER DEFAULT 0,
    model_trainings INTEGER DEFAULT 0,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, period_start, period_end)
);

CREATE INDEX idx_usage_user ON public.usage_metrics(user_id);

ALTER TABLE public.usage_metrics ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own usage"
    ON public.usage_metrics FOR SELECT
    USING (auth.uid() = user_id);

-- 3. RATE LIMIT LOGS TABLE (For abuse protection tracking if needed)
CREATE TABLE IF NOT EXISTS public.rate_limit_logs (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ip_address      TEXT,
    user_id         UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    endpoint        TEXT NOT NULL,
    blocked_at      TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
