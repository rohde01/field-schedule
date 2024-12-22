<script lang="ts">
    import Calendar from '@event-calendar/core';
    import TimeLine from '@event-calendar/resource-timeline';
    import TimeGrid from '@event-calendar/resource-time-grid';
    import { fields } from '../../stores/fields';
    import { dropdownState } from '../../stores/ScheduleDropdownState';
    import type { Field } from '$lib/schemas/field';
    import type { CalendarResource, CalendarEvent } from '$lib/types/event-calendar';
    import type { Schedule } from '$lib/schemas/schedule';

    let plugins = [TimeLine, TimeGrid];

    function buildResources(allFields: Field[], selectedSchedule: Schedule | null): CalendarResource[] {
        const facilityFields = selectedSchedule?.facility_id 
            ? allFields.filter(field => field.facility_id === selectedSchedule.facility_id)
            : [];

        // Identify top-level (full) fields
        const topLevelFields = facilityFields.filter(field => field.parent_field_id === null);

        // Convert each top-level field into a resource
        return topLevelFields.map(field => toResource(field));
    }

    function toResource(field: Field): CalendarResource {
        // For each half subfield, find its quarter subfields
        const halfChildren = field.half_subfields.map(half => {
            const quarterChildren = field.quarter_subfields
                .filter(q => q.parent_field_id === half.field_id)
                .map(q => ({
                    id: q.field_id.toString(),
                    title: q.name,
                    parentId: q.parent_field_id?.toString() ?? null,
                    children: []
                }));

            return {
                id: half.field_id.toString(),
                title: half.name,
                parentId: half.parent_field_id?.toString() ?? null,
                children: quarterChildren
            };
        });

        return {
            id: field.field_id.toString(),
            title: field.name,
            parentId: field.parent_field_id?.toString() ?? null,
            children: halfChildren
        };
    }

    let events: CalendarEvent[] = [
        {
            title: 'Event 1',
            start: '2024-12-20T09:00:00',
            end: '2024-12-20T10:00:00',
            resourceId: '1'
        },
        {
            title: 'Event 2',
            start: '2024-12-20T10:00:00',
            end: '2024-12-20T11:00:00',
            resourceId: '5'
        }
    ];

    // Recompute resources whenever fields or selected schedule changes
    $: currentResources = buildResources($fields, $dropdownState.selectedSchedule);

    let options: {
        view: string;
        nowIndicator: boolean;
        resources: CalendarResource[];
        events: CalendarEvent[];
    } = {
        view: 'resourceTimelineDay',
        nowIndicator: true,
        resources: currentResources,
        events
    };

    $: options = {
        ...options,
        resources: currentResources,
        events
    };
</script>

<div>
    <Calendar {plugins} {options} />
</div>