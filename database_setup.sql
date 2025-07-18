-- CreAItion Database Schema - Clean Setup for Email-Based Authentication
-- Drop and recreate all tables to ensure clean state

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Drop all existing tables in correct order (reverse of dependencies)
DROP TABLE IF EXISTS public.scenes CASCADE;
DROP TABLE IF EXISTS public.user_character CASCADE;
DROP TABLE IF EXISTS public.stories CASCADE;
DROP TABLE IF EXISTS public.users CASCADE;

-- Drop any existing functions
DROP FUNCTION IF EXISTS update_updated_at_column() CASCADE;

-- Create users table (simplified - email-based authentication)
CREATE TABLE public.users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    credits INTEGER NOT NULL DEFAULT 999,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create stories table
CREATE TABLE public.stories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    nb_scenes INTEGER NOT NULL DEFAULT 1,
    nb_chars INTEGER NOT NULL DEFAULT 1,
    story_mode VARCHAR(100) NOT NULL DEFAULT 'adventure',
    cover_image_url TEXT,
    cover_image_name VARCHAR(255),
    background_story TEXT,
    status VARCHAR(50) DEFAULT 'created',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    scenes_paragraph TEXT
);

-- Create user_character table
CREATE TABLE public.user_character (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    story_id UUID NOT NULL REFERENCES public.stories(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    image_url TEXT,
    analysis TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    image_name TEXT
);

-- Create scenes table
CREATE TABLE public.scenes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    story_id UUID NOT NULL REFERENCES public.stories(id) ON DELETE CASCADE,
    scene_number INTEGER NOT NULL,
    title VARCHAR(255),
    narrative_text TEXT,
    image_prompt TEXT,
    image_url TEXT,
    paragraph TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(story_id, scene_number)
);

-- Create indexes for performance
CREATE INDEX idx_users_email ON public.users(email);
CREATE INDEX idx_stories_user_id ON public.stories(user_id);
CREATE INDEX idx_stories_created_at ON public.stories(created_at);
CREATE INDEX idx_user_character_story_id ON public.user_character(story_id);
CREATE INDEX idx_scenes_story_id ON public.scenes(story_id);
CREATE INDEX idx_scenes_scene_number ON public.scenes(story_id, scene_number);

-- Add constraints
ALTER TABLE public.stories 
ADD CONSTRAINT chk_nb_scenes_positive CHECK (nb_scenes > 0),
ADD CONSTRAINT chk_nb_chars_positive CHECK (nb_chars > 0);

ALTER TABLE public.users
ADD CONSTRAINT chk_credits_non_negative CHECK (credits >= 0);

ALTER TABLE public.scenes
ADD CONSTRAINT chk_scene_number_positive CHECK (scene_number > 0);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_users_updated_at 
    BEFORE UPDATE ON public.users 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_stories_updated_at 
    BEFORE UPDATE ON public.stories 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_character_updated_at 
    BEFORE UPDATE ON public.user_character 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_scenes_updated_at 
    BEFORE UPDATE ON public.scenes 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Disable Row Level Security (RLS) for simplified development
-- This ensures no authentication issues during development
ALTER TABLE public.users DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.stories DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_character DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.scenes DISABLE ROW LEVEL SECURITY;

-- Insert a test user for development (optional)
INSERT INTO public.users (username, email, credits) 
VALUES ('testuser', 'test@example.com', 999)
ON CONFLICT (email) DO NOTHING;

-- Grant necessary permissions (adjust as needed for your setup)
GRANT ALL ON public.users TO authenticated, anon;
GRANT ALL ON public.stories TO authenticated, anon;
GRANT ALL ON public.user_character TO authenticated, anon;
GRANT ALL ON public.scenes TO authenticated, anon;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO authenticated, anon;

-- Display completion message
DO $$
BEGIN
    RAISE NOTICE 'Database setup completed successfully!';
    RAISE NOTICE 'Tables created: users, stories, user_character, scenes';
    RAISE NOTICE 'RLS disabled for development';
    RAISE NOTICE 'Test user created: test@example.com with 999 credits';
END $$;
