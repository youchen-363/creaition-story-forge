// API Configuration
export const API_URL = (import.meta.env.VITE_API_URL || 'http://localhost:8002') + '/api/';

// Supabase Configuration  
export const SUPABASE_URL = import.meta.env.VITE_SUPABASE_URL || '';
export const SUPABASE_ANON_KEY = import.meta.env.VITE_SUPABASE_ANON_KEY || '';