import React from 'react';
import { Auth } from '@supabase/auth-ui-react';
import { ThemeSupa } from '@supabase/auth-ui-shared';
import { supabase } from '../supabaseClient';

// A small wrapper component that renders Supabase's hosted auth UI.
// It will work once env vars are set and Supabase is configured.
const SupabaseAuth = () => {
  return (
    <div style={{ maxWidth: 420, margin: '0 auto' }}>
      <Auth
        supabaseClient={supabase}
        appearance={{ theme: ThemeSupa }}
        providers={[]}
        socialLayout="horizontal"
        view="sign_in"
        localization={{
          variables: {
            sign_in: { email_label: 'Email', password_label: 'Password' },
          },
        }}
      />
    </div>
  );
};

export default SupabaseAuth;
