-- ============================================================
-- DeepInsight Starter Suite — Migration 03: Auth Enhancements
-- ============================================================

-- 1. Add missing auth fields to profiles
ALTER TABLE public.profiles 
ADD COLUMN IF NOT EXISTS role TEXT DEFAULT 'member', -- 'admin', 'member', 'viewer'
ADD COLUMN IF NOT EXISTS email_verified BOOLEAN DEFAULT false,
ADD COLUMN IF NOT EXISTS last_login TIMESTAMPTZ;

-- Let's make the first user an admin for convenience in testing
UPDATE public.profiles 
SET role = 'admin' 
WHERE id IN (
    SELECT id FROM auth.users ORDER BY created_at ASC LIMIT 1
);
