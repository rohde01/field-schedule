import type { PageServerLoad, Actions } from './$types';
import type { CreateFieldResponse } from '$lib/types/field';
import { error, fail } from '@sveltejs/kit';

export const load = (async ({ locals, fetch }) => {
    if (!locals.user) {
        throw error(401, 'User not authenticated');
    }

    // If we already know the user has no facilities, return early
    if (locals.facilityStatus?.has_facilities === false) {
        return { 
            facilities: [], 
            fields: [],
            has_facilities: false 
        };
    }

    try {
        const facilitiesResponse = await fetch(`http://localhost:8000/facilities/club/${locals.user.primary_club_id}`, {
            headers: {
                'Authorization': `Bearer ${locals.token}`
            }
        });
        
        if (!facilitiesResponse.ok) {
            if (facilitiesResponse.status === 404) {
                return { 
                    facilities: [], 
                    fields: [],
                    has_facilities: false 
                };
            }
            throw error(facilitiesResponse.status, 'Failed to fetch facilities');
        }

        const facilities = await facilitiesResponse.json();
        
        if (!facilities || facilities.length === 0) {
            return { 
                facilities: [], 
                fields: [],
                has_facilities: false 
            };
        }

        let fields = [];
        if (locals.facilityStatus?.selectedFacility) {
            try {
                const fieldsResponse = await fetch(`http://localhost:8000/fields/facility/${locals.facilityStatus.selectedFacility.facility_id}`, {
                    headers: {
                        'Authorization': `Bearer ${locals.token}`
                    }
                });
                if (fieldsResponse.ok) {
                    fields = await fieldsResponse.json();
                }
            } catch (error) {
                console.error('Failed to fetch fields:', error);
            }
        }

        return { 
            facilities, 
            fields,
            has_facilities: true 
        };
    } catch (error) {
        console.error('Error in facilities load:', error);
        return { 
            facilities: [], 
            fields: [],
            has_facilities: false 
        };
    }
}) satisfies PageServerLoad;

export const actions = {
    create: async ({ request, locals, fetch }) => {
        if (!locals.user) {
            return fail(401, { error: 'User not authenticated' });
        }

        const data = await request.formData();
        const name = data.get('name')?.toString();
        const is_primary = data.get('is_primary') === 'true';

        if (!name) {
            return fail(400, { error: 'Facility name is required' });
        }

        try {
            const response = await fetch('http://localhost:8000/facilities', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${locals.token}`
                },
                body: JSON.stringify({
                    name,
                    is_primary,
                    club_id: locals.user.primary_club_id
                })
            });

            if (!response.ok) {
                return fail(response.status, { error: 'Failed to create facility' });
            }

            const facility = await response.json();
            
            if (locals.facilityStatus) {
                locals.facilityStatus.has_facilities = true;
                if (is_primary || !locals.facilityStatus.selectedFacility) {
                    locals.facilityStatus.selectedFacility = facility;
                }
            }

            return { 
                success: true, 
                facility,
                has_facilities: true 
            };
        } catch (e) {
            console.error('Error creating facility:', e);
            return fail(500, { error: 'Failed to create facility' });
        }
    },
    
    createField: async ({ request, fetch, locals }) => {
        const formData = await request.formData();
        const fieldDataString = formData.get('fieldData');
        
        if (!fieldDataString || typeof fieldDataString !== 'string') {
            return fail(400, { error: 'Field data is missing or invalid' });
        }
        
        try {
            const fieldData = JSON.parse(fieldDataString);
            
            const response = await fetch('http://localhost:8000/fields', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${locals.token}`
                },
                body: JSON.stringify(fieldData)
            });

            if (!response.ok) {
                const errorText = await response.text();
                console.error('Server error:', errorText);
                return fail(response.status, { 
                    error: `Failed to create field: ${errorText}` 
                });
            }

            const result = await response.json();
            return { success: true, field_id: result.field_id };

        } catch (error) {
            console.error('Error creating field:', error);
            return fail(500, { 
                error: error instanceof Error ? error.message : 'Failed to create field' 
            });
        }
    },

    deleteField: async ({ request, fetch, locals }) => {
        const formData = await request.formData();
        const fieldId = formData.get('fieldId');

        if (!fieldId) {
            return fail(400, { error: 'Field ID is required' });
        }

        try {
            const response = await fetch(`http://localhost:8000/fields/${fieldId}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${locals.token}`
                }
            });

            if (!response.ok) {
                const errorData = await response.json();
                return fail(response.status, { 
                    error: errorData.detail || 'Failed to delete field' 
                });
            }

            return { 
                success: true,
                field_id: fieldId
            };

        } catch (error) {
            console.error('Error deleting field:', error);
            return fail(500, { 
                error: 'Failed to delete field' 
            });
        }
    }
} satisfies Actions;
