// Lightweight Supabase client wrapper using env vars set in .env
import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.REACT_APP_SUPABASE_URL || '';
const supabaseKey = process.env.REACT_APP_SUPABASE_KEY || '';

if (!supabaseUrl || !supabaseKey) {
  throw new Error('Supabase URL and Key are required');
}

export const supabase = createClient(supabaseUrl, supabaseKey);