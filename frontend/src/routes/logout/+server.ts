import { redirect } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { user } from '../../stores/user';
import { facilityStatus } from '../../stores/facilityStatus';
import { dropdownState } from '../../stores/FacilityDropdownState';

export const POST: RequestHandler = async ({ cookies, locals }) => {
    user.set(null);
    facilityStatus.reset();
    dropdownState.set({
        facilityOpen: false,
        fieldsOpen: true,
        selectedField: null,
        showCreateField: false
    });

    cookies.delete('token', { path: '/' });
    locals.user = null;
    locals.facilityStatus = null;
    throw redirect(303, '/');
};