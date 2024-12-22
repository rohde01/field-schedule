<script lang="ts">
    import Calendar from '@event-calendar/core';
    import TimeLine from '@event-calendar/resource-timeline';
    import TimeGrid from '@event-calendar/resource-time-grid';
    import { fields } from '../../stores/fields';
    import { schedules } from '../../stores/schedules';
    import { dropdownState } from '../../stores/ScheduleDropdownState';
    import type { Field } from '$lib/schemas/field';
    import type { CalendarResource, CalendarEvent } from '$lib/types/event-calendar';
    import type { Schedule, ScheduleEntry } from '$lib/schemas/schedule';

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

    // Hardcoded schedule_id for now - this should be made configurable later
    const SCHEDULE_ID = 25;

    function createEventFromScheduleEntry(entry: ScheduleEntry): CalendarEvent {
        const now = new Date();
        const currentDay = now.getDay();
        const adjustedCurrentDay = currentDay === 0 ? 6 : currentDay - 1;
        const daysUntilNext = ((entry.week_day - adjustedCurrentDay + 7) % 7);
        const nextDate = new Date(now);
        nextDate.setDate(now.getDate() + daysUntilNext);
        
        const dateStr = nextDate.toISOString().split('T')[0];
        
        return {
            title: entry.team_id?.toString() ?? 'Unassigned',
            start: `${dateStr}T${entry.start_time}`,
            end: `${dateStr}T${entry.end_time}`,
            resourceId: entry.field_id?.toString() ?? '',
            id: entry.schedule_entry_id.toString()
        };
    }

    // Convert schedule entries to calendar events
    function getEventsFromSchedule(schedules: Schedule[]): CalendarEvent[] {
        const schedule = schedules.find(s => s.schedule_id === SCHEDULE_ID);
        if (!schedule) return [];
        
        return schedule.entries.map(createEventFromScheduleEntry);
    }

    // Recompute events whenever schedules change
    $: events = getEventsFromSchedule($schedules);

    // Recompute resources whenever fields or selected schedule changes
    $: currentResources = buildResources($fields, $dropdownState.selectedSchedule);

    let options: {
        view: string;
        nowIndicator: boolean;
        resources: CalendarResource[];
        events: CalendarEvent[];
        slotMinTime: string;
        slotMaxTime: string;
        slotDuration: string;
    } = {
        view: 'resourceTimelineDay',
        nowIndicator: true,
        resources: currentResources,
        events,
        slotMinTime: '12:00:00',
        slotMaxTime: '23:00:00',
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