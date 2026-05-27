import { useEffect } from 'react';
import { create } from 'zustand';
import { createClient } from '@/lib/supabase';
import { fetchApi } from '@/lib/api';

interface UserProfile {
  user_id: string;
  email: string;
  display_name: string;
  plan: string;
  role: string;
  trial_end: string | null;
  subscription_status: string;
}

interface AuthState {
  user: any | null;
  profile: UserProfile | null;
  isLoading: boolean;
  setUser: (user: any | null) => void;
  setProfile: (profile: UserProfile | null) => void;
  setLoading: (isLoading: boolean) => void;
  signOut: () => Promise<void>;
  fetchProfile: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  profile: null,
  isLoading: true,
  setUser: (user) => set({ user }),
  setProfile: (profile) => set({ profile }),
  setLoading: (isLoading) => set({ isLoading }),
  
  signOut: async () => {
    const supabase = createClient();
    await supabase.auth.signOut();
    set({ user: null, profile: null });
  },
  
  fetchProfile: async () => {
    try {
      const profileData = await fetchApi('/api/auth/me');
      set({ profile: profileData });
    } catch (error) {
      console.error('Failed to fetch user profile:', error);
    }
  }
}));

export function useAuth() {
  const { user, profile, isLoading, setUser, setLoading, signOut, fetchProfile } = useAuthStore();
  const supabase = createClient();

  useEffect(() => {
    let mounted = true;

    async function getInitialSession() {
      const { data: { session }, error } = await supabase.auth.getSession();
      
      if (mounted) {
        if (session?.user) {
          setUser(session.user);
          await fetchProfile();
        } else {
          setUser(null);
        }
        setLoading(false);
      }
    }

    getInitialSession();

    const { data: { subscription } } = supabase.auth.onAuthStateChange(async (event, session) => {
      if (mounted) {
        if (session?.user) {
          setUser(session.user);
          await fetchProfile();
        } else {
          setUser(null);
        }
        setLoading(false);
      }
    });

    return () => {
      mounted = false;
      subscription.unsubscribe();
    };
  }, []);

  return { user, profile, isLoading, signOut };
}
