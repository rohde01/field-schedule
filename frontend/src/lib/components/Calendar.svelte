<script lang="ts">
    import Calendar from '@event-calendar/core';
    import TimeLine from '@event-calendar/resource-timeline';
    import TimeGrid from '@event-calendar/resource-time-grid';
    import { fields } from '../../stores/fields';
    import { schedules } from '../../stores/schedules';
    import { dropdownState } from '../../stores/ScheduleDropdownState';
    import type { Field } from '$lib/schemas/field';
    import type { Schedule, ScheduleEntry } from '$lib/schemas/schedule';

    let plugins = [TimeLine, TimeGrid];

    function buildResources(allFields: Field[], selectedSchedule: Schedule | null): any[] {
        const facilityFields = selectedSchedule?.facility_id 
            ? allFields.filter(field => field.facility_id === selectedSchedule.facility_id)
            : [];

        // Identify top-level (full) fields
        const topLevelFields = facilityFields.filter(field => field.parent_field_id === null);

        // Convert each top-level field into a resource
        return topLevelFields.map(field => ({
            id: field.field_id.toString(),
            title: field.name,
            parentId: null,
            children: field.half_subfields.map(half => ({
                id: half.field_id.toString(),
                title: half.name,
                parentId: half.parent_field_id?.toString() ?? null,
                children: field.quarter_subfields
                    .filter(q => q.parent_field_id === half.field_id)
                    .map(q => ({
                        id: q.field_id.toString(),
                        title: q.name,
                        parentId: q.parent_field_id?.toString() ?? null,
                        children: []
                    }))
            }))
        }));
    }

    // Hardcoded schedule_id for now - this should be made configurable later
    const SCHEDULE_ID = 25;

    function getScheduleEntries(schedules: Schedule[]): ScheduleEntry[] {
        const schedule = schedules.find(s => s.schedule_id === SCHEDULE_ID);
        return schedule?.entries ?? [];
    }

    // Recompute events whenever schedules change
    $: events = getScheduleEntries($schedules).map(entry => {
        const today = new Date();
        const targetDate = new Date(today);
        targetDate.setDate(today.getDate() + ((entry.week_day + 7 - today.getDay()) % 7) + 1);
        const dateStr = targetDate.toISOString().split('T')[0];
        
        return {
            title: entry.team_id?.toString() ?? 'Unassigned',
            start: `${dateStr}T${entry.start_time}`,
            end: `${dateStr}T${entry.end_time}`,
            resourceId: entry.field_id?.toString() ?? '',
            id: entry.schedule_entry_id.toString()
        };
    });

    // Recompute resources whenever fields or selected schedule changes
    $: currentResources = buildResources($fields, $dropdownState.selectedSchedule);

    let options = {
        view: 'resourceTimelineDay',
        nowIndicator: true,
        resources: currentResources,
        events,
        slotMinTime: '09:00:00',
        slotMaxTime: '23:59:00',
        slotDuration: '00:60:00'
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

<style>
:global(.ec-sidebar-title) {
    flex-basis: 49px !important;
}
</style>