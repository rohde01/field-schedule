<script lang="ts">
    import { browser } from '$app/environment';
    import Calendar from '@event-calendar/core';
    import TimeGrid from '@event-calendar/time-grid';
    import DayGrid from '@event-calendar/day-grid';
    import Interaction from '@event-calendar/interaction';
    import '@event-calendar/core/index.css';
    import { activeSchedules } from '../../stores/activeSchedules';
    import { schedules } from '../../stores/schedules';

    let plugins = [TimeGrid, DayGrid, Interaction];
    
    // Reference to the EC instance
    let ecInstance: any;
    
    // Export navigation methods that directly use the EC API
    export function navigatePrev() {
        if (ecInstance && ecInstance.getOption) {
            ecInstance.prev();
        }
    }
    
    export function navigateNext() {
        if (ecInstance && ecInstance.getOption) {
            ecInstance.next();
        }
    }
    
    export function navigateToday() {
        if (ecInstance && ecInstance.getOption) {
            ecInstance.today();
        }
    }
    
    // Get the current title (month/year)
    export function getCurrentTitle(): string {
        if (ecInstance && ecInstance.getOption) {
            return ecInstance.getOption('title');
        }
        return '';
    }
    
    // Convert active schedules to calendar events
    $: activeScheduleEvents = $activeSchedules
        .map(schedule => {
            const scheduleName = $schedules.find(s => s.schedule_id === schedule.schedule_id)?.name ?? `Schedule ${schedule.schedule_id}`;

            if (!schedule.start_date || !schedule.end_date) return null;
            
            return {
                id: `active_${schedule.active_schedule_id}`,
                title: `Active: ${scheduleName}`,
                start: new Date(schedule.start_date).toISOString(),
                end: new Date(schedule.end_date).toISOString(),
                allDay: true,
                color: '#4CAF50'
            };
        })
        .filter((event): event is { id: string; title: string; start: string; end: string; allDay: boolean; color: string; } => 
            event !== null
        ); 

    // Convert schedules to calendar events using active_from and active_until
    $: scheduleEvents = $schedules
        .filter(schedule => schedule.active_from && schedule.active_until)
        .map(schedule => {
            return {
                id: `schedule_${schedule.schedule_id}`,
                title: schedule.name,
                start: new Date(schedule.active_from!).toISOString(),
                end: new Date(schedule.active_until!).toISOString(),
                allDay: true,
                color: '#2196F3'
            };
        });

    // Combine both event types
    $: calendarEvents = [...activeScheduleEvents, ...scheduleEvents];

    $: options = {
        view: 'dayGridMonth',
        events: calendarEvents,
        height: '800px',
        headerToolbar: {
            start: '',
            center: '',
            end: ''
        },
        buttonText: {
            today: '',
            dayGridMonth: '',
        }
    };
</script>

<div class="calendar-wrapper">
    {#if browser}
        <Calendar {plugins} {options} bind:this={ecInstance} />
    {/if}
</div>

<style>
    .calendar-wrapper {
        width: 100%;
        background: white;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1);
    }
</style>