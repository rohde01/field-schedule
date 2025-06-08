import { fail, redirect } from '@sveltejs/kit';
import { superValidate } from 'sveltekit-superforms/server';
import { zod } from 'sveltekit-superforms/adapters';
import { updateUserSchema } from '$lib/schemas/user';
import { createClubSchema, updateClubSchema } from '$lib/schemas/club';
import type { Actions, PageServerLoad } from './$types';

export const ssr = false

export const load: PageServerLoad = async (event) => {
    const { locals: { user, supabase } } = event;
    if (!user) throw redirect(303, '/auth/login');

    const userForm = await superValidate(event, zod(updateUserSchema), {
        defaults: { email: user.email, first_name: user.first_name ?? undefined, last_name: user.last_name ?? undefined, role: user.role }
    });
    const clubForm = await superValidate(event, zod(createClubSchema));
    let clubData = null;
    let updateClubForm = await superValidate(event, zod(updateClubSchema));

    if (user.club_id) {
        const { data: club, error } = await supabase
            .from('clubs')
            .select('*')
            .eq('club_id', user.club_id)
            .single();
        if (!error && club) {
            clubData = club;
            updateClubForm = await superValidate(event, zod(updateClubSchema), {
                defaults: { name: club.name, club_url: club.club_url }
            });
        }
    }

    return { userForm, clubForm, updateClubForm, user, clubData, hasClub: Boolean(user.club_id) };
};

export const actions: Actions = {
    updateUser: async ({ request, locals: { supabase, user } }) => {

        if (!user) {
            throw redirect(303, '/auth/login');
        }

        const form = await superValidate(request, zod(updateUserSchema));

        if (!form.valid) {
            return fail(400, { form });
        }

        const { error } = await supabase
            .from('users')
            .update({ ...form.data })
            .eq('user_id', user.user_id)
            .select()
            .single();

        if (error) {
            return fail(400, {
                form: {
                    ...form,
                    message: 'Failed to update profile'
                }
            });
        }

        // Set success message and return form
        form.message = 'Profile updated successfully';
        return { form };
    },

    updateClub: async ({ request, locals: { supabase, user } }) => {
            // Ensure user is authenticated
        if (!user) {
        throw redirect(303, '/auth/login');
        }

        const form = await superValidate(request, zod(updateClubSchema));

        if (!form.valid) {
            return fail(400, { form });
        }

        const { error } = await supabase
            .from('clubs')
            .update({ ...form.data })
            .eq('club_id', user.club_id)
            .select()
            .single();

        if (error) {
            return fail(400, {
                form: {
                    ...form,
                    message: 'Failed to update club'
                }
            });
        }

        // Set success message and return form
        form.message = 'Club updated successfully';
        return { form };
    },

    createClub: async ({ request, locals: { supabase, user } }) => {
        // Ensure user is authenticated
        if (!user) {
            throw redirect(303, '/auth/login');
        }

        const form = await superValidate(request, zod(createClubSchema));

        if (!form.valid) {
            return fail(400, { form });
        }

        // Create the club with owner_id
        const { error: clubError, data: clubData } = await supabase
            .from('clubs')
            .insert({ 
                name: form.data.name,
                owner_id: user.user_id,
                club_url: form.data.club_url
            })
            .select()
            .single();

        if (clubError) {
            return fail(400, {
                form: {
                    ...form,
                    message: `Failed to create club: ${clubError.message}`
                }
            });
        }

        // Update user with club_id
        const { error: userError } = await supabase
            .from('users')
            .update({ club_id: clubData.club_id })
            .eq('user_id', user.user_id);

        if (userError) {
            return fail(400, {
                form: {
                    ...form,
                    message: `Failed to update user club: ${userError.message}`
                }
            });
        }

        throw redirect(303, '/schedules');
    },
    uploadLogo: async ({ request, locals: { supabase, user } }) => {
        if (!user) throw redirect(303, '/auth/login');
        const formData = await request.formData();
        const file = formData.get('logo');
        if (!file || !(file instanceof Blob)) {
            console.error('No file provided or invalid type');
            return fail(400, { message: 'No file provided' });
        }
        const name = (file as File).name;
        const ext = name.split('.').pop();
        const filePath = `${user.user_id}/${Date.now()}.${ext}`;
        const { error: uploadError } = await supabase.storage.from('logos').upload(filePath, file as File, { upsert: true });
        if (uploadError) {
            console.error('Supabase upload error:', uploadError);
            return fail(400, { message: `Failed to upload logo: ${uploadError.message}` });
        }
        const { data: urlData } = supabase.storage.from('logos').getPublicUrl(filePath);
        const publicUrl = urlData.publicUrl;
        const { error: updateError } = await supabase
            .from('clubs')
            .update({ logo_url: publicUrl })
            .eq('club_id', user.club_id)
            .select()
            .single();
        if (updateError) {
            return fail(400, { message: `Failed to update club logo: ${updateError.message}` });
        }
        throw redirect(303, '/settings');
    }
};