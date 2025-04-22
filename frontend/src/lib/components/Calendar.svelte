<script lang="ts">
    import { browser } from '$app/environment';
    import Calendar from '@event-calendar/core';
    import TimeGrid from '@event-calendar/time-grid';
    import DayGrid from '@event-calendar/day-grid';
    import Interaction from '@event-calendar/interaction';
    import '@event-calendar/core/index.css';
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

    $: options = {
        view: 'dayGridMonth',
        events: scheduleEvents,
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