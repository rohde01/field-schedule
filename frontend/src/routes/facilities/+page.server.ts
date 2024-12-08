import type { PageServerLoad, Actions } from './$types';
import type { CreateFieldResponse } from '$lib/types/field'; // Add this import
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
        const facilitiesResponse = await fetch(`http://localhost:8000/facilities/club/${locals.user.primary_club_id}`);
        
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
                const fieldsResponse = await fetch(`http://localhost:8000/fields/facility/${locals.facilityStatus.selectedFacility.facility_id}`);
                if (fieldsResponse.ok) {
                    fields = await fieldsResponse.json();
                }
            } catch (error) {
                console.error('Failed to fetch fields:', error);
                // Continue without fields if fetch fails
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
                    'Content-Type': 'application/json'
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
    
    createField: async ({ request, fetch }) => {
        const formData = await request.formData();
        
        try {
            const fieldData = JSON.parse(formData.get('fieldData') as string);
            const availabilityData = JSON.parse(formData.get('availabilityData') as string);
            
            // First create the field
            const response = await fetch('http://localhost:8000/fields', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(fieldData)
            });

            if (!response.ok) {
                const errorData = await response.json();
                console.error('Server error:', errorData);
                return fail(response.status, { 
                    error: errorData.detail || 'Failed to create field' 
                });
            }

            const result: CreateFieldResponse = await response.json();

            // Then add the availability
            if (availabilityData.availabilities.length > 0) {
                const availabilityResponse = await fetch(`http://localhost:8000/fields/${result.field_id}/availability`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(availabilityData)
                });

                if (!availabilityResponse.ok) {
                    console.error('Failed to add field availability');
                    // We don't fail the whole operation if availability fails
                }
            }

            return { success: true, field_id: result.field_id };

        } catch (error) {
            console.error('Error creating field:', error);
            return fail(500, { 
                error: 'Failed to create field' 
            });
        }
    },

    deleteField: async ({ request, fetch }) => {
        const formData = await request.formData();
        const fieldId = formData.get('fieldId');

        if (!fieldId) {
            return fail(400, { error: 'Field ID is required' });
        }

        try {
            const response = await fetch(`http://localhost:8000/fields/${fieldId}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
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

