-- DeepInsight Starter Suite — Migration 02
-- Add Multi-Tenant Architecture (Organizations) and Audit Logging

-- 1. Create Organizations table
CREATE TABLE IF NOT EXISTS public.organizations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    domain TEXT,
    stripe_customer_id TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. Link Profiles to Organizations
ALTER TABLE public.profiles
ADD COLUMN IF NOT EXISTS org_id UUID REFERENCES public.organizations(id);

-- 3. Create Audit Logs table for tracking actions
CREATE TABLE IF NOT EXISTS public.audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    org_id UUID REFERENCES public.organizations(id),
    user_id UUID REFERENCES public.profiles(id),
    action TEXT NOT NULL, -- e.g., 'dataset.uploaded', 'model.trained'
    resource_type TEXT NOT NULL,
    resource_id TEXT,
    details JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable RLS on audit_logs
ALTER TABLE public.audit_logs ENABLE ROW LEVEL SECURITY;

-- Admins can view audit logs for their org
CREATE POLICY "Admins can view org audit logs" 
ON public.audit_logs FOR SELECT 
USING (
    org_id IN (
        SELECT org_id FROM public.profiles 
        WHERE id = auth.uid() AND role = 'admin'
    )
);

-- Note: A function or backend service should handle inserting audit logs (usually bypasses RLS)
