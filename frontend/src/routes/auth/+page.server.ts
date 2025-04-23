import { fail, redirect } from '@sveltejs/kit';
import { superValidate } from 'sveltekit-superforms/server';
import { zod } from 'sveltekit-superforms/adapters';
import { createUserSchema } from '$lib/schemas/user';
import type { Actions, PageServerLoad } from './$types';
import { dev } from '$app/environment';

export const load = (async ({}) => {
  const form = await superValidate(zod(createUserSchema));
  return { form };
})

export const actions: Actions = {
  signup: async ({ request, locals: { supabase }, url }) => {
    const form = await superValidate(request, zod(createUserSchema));
    if (!form.valid) return fail(400, { form });

    const { email, password } = form.data;
    const { error } = await supabase.auth.signUp({
      email,
      password,
      options: {
        emailRedirectTo: '/auth/confirm'
      }
    });

    if (error) {
      return fail(400, {
        form: {
          ...form,
          message: error.message ?? 'Registration failed'
        }
      });
    }

    return { form, confirmationEmailSent: true };
  },

  login: async ({ request, locals: { supabase } }) => {
    const form = await superValidate(request, zod(createUserSchema));
    if (!form.valid) return fail(400, { form });

    const { email, password } = form.data;
    const { error } = await supabase.auth.signInWithPassword({ email, password });

    if (error) {
      return fail(400, {
        form: {
          ...form,
          message: error.message ?? 'Login failed'
        }
      });
    }
    throw redirect(303, '/schedules');
  },

  logout: async ({ cookies, locals: { supabase } }) => {
    const { error } = await supabase.auth.signOut({
      scope: 'global'
    });
    
    if (error) {
      return fail(500, { message: 'Logout failed' });
    }
    // Clear supabase auth cookies
    ['sb-access-token', 'sb-refresh-token', 'sb-auth-token'].forEach(name => {
      cookies.delete(name, { path: '/', httpOnly: true, secure: !dev, sameSite: 'lax' });
    });
    
    throw redirect(303, '/');
  }
}