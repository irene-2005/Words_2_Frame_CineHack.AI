// Lightweight Supabase client wrapper (placeholder)
// Fill REACT_APP_SUPABASE_URL and REACT_APP_SUPABASE_ANON_KEY in your .env file
import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.REACT_APP_SUPABASE_URL || '';
const supabaseAnonKey = process.env.REACT_APP_SUPABASE_ANON_KEY || '';

export const supabase = createClient(supabaseUrl, supabaseAnonKey);