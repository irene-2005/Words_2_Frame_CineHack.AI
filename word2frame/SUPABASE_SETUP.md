Add the Supabase URL and anon key to an .env file in the project root (create .env.local for CRA):

REACT_APP_SUPABASE_URL=https://your-supabase-project-url.supabase.co
REACT_APP_SUPABASE_ANON_KEY=your-anon-key

Then restart the dev server. The project imports `supabase` from `src/supabaseClient.js` which uses these env vars.

This is optional for your hackathon demo — you can leave the login/signup demo flows disabled, or provide actual keys to enable auth.