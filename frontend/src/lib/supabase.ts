import { createClient } from '@supabase/supabase-js';
import { SUPABASE_URL, SUPABASE_ANON_KEY } from './config';

if (!SUPABASE_URL || !SUPABASE_ANON_KEY) {
  throw new Error('Missing Supabase environment variables. Please check your .env file.');
}

export const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

// Types for better TypeScript support
export type Database = {
  public: {
    Tables: {
      user_profiles: {
        Row: {
          id: string;
          username: string | null;
          credits: number;
          created_at: string;
          updated_at: string;
        };
        Insert: {
          id: string;
          username?: string | null;
          credits?: number;
          created_at?: string;
          updated_at?: string;
        };
        Update: {
          id?: string;
          username?: string | null;
          credits?: number;
          created_at?: string;
          updated_at?: string;
        };
      };
      characters: {
        Row: {
          id: string;
          user_id: string;
          name: string;
          description: string;
          image_url: string | null;
          image_path: string | null;
          created_at: string;
        };
        Insert: {
          id?: string;
          user_id: string;
          name: string;
          description: string;
          image_url?: string | null;
          image_path?: string | null;
          created_at?: string;
        };
        Update: {
          id?: string;
          user_id?: string;
          name?: string;
          description?: string;
          image_url?: string | null;
          image_path?: string | null;
          created_at?: string;
        };
      };
      stories: {
        Row: {
          id: string;
          user_id: string;
          title: string;
          background_story: string | null;
          future_story: string | null;
          analysis: string | null;
          num_scenes: number;
          status: string;
          created_at: string;
          updated_at: string;
        };
        Insert: {
          id?: string;
          user_id: string;
          title: string;
          background_story?: string | null;
          future_story?: string | null;
          analysis?: string | null;
          num_scenes?: number;
          status?: string;
          created_at?: string;
          updated_at?: string;
        };
        Update: {
          id?: string;
          user_id?: string;
          title?: string;
          background_story?: string | null;
          future_story?: string | null;
          analysis?: string | null;
          num_scenes?: number;
          status?: string;
          created_at?: string;
          updated_at?: string;
        };
      };
    };
  };
};
