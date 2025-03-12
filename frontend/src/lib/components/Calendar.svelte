<script>
    import Calendar from '@event-calendar/core';
    import TimeGrid from '@event-calendar/time-grid';
    import DayGrid from '@event-calendar/day-grid';
    import '@event-calendar/core/index.css';
    import { activeSchedules } from '../../stores/activeSchedules';

    let plugins = [TimeGrid, DayGrid];
    
    // Event handlers
    const handleMouseEnter = () => {
    };

    const handleMouseLeave = () => {
    };
    
    // Convert active schedules to calendar events
    $: calendarEvents = $activeSchedules.map(schedule => ({
        id: schedule.schedule_id,
        title: `Schedule ${schedule.schedule_id}`,
        start: new Date(schedule.start_date),
        end: new Date(schedule.end_date),
        // Pass function references directly instead of invoking them
        mouseenter: handleMouseEnter,
        mouseleave: handleMouseLeave
    }));

    $: options = {
        view: 'timeGridWeek',
        events: calendarEvents,
        height: '800px',
        headerToolbar: {
            start: 'prev,next today',
            center: 'title',
            end: 'timeGridWeek,dayGridMonth'
        },
        buttonText: {
            today: 'Today',
            dayGridMonth: 'Month',
            timeGridWeek: 'Week'
        }
    };
</script>

<div class="calendar-wrapper">
    <Calendar {plugins} {options} />
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