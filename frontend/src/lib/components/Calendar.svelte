<script>
    import Calendar from '@event-calendar/core';
    import TimeGrid from '@event-calendar/time-grid';
    import DayGrid from '@event-calendar/day-grid';
    import '@event-calendar/core/index.css';

    let plugins = [TimeGrid, DayGrid];
    let options = {
        view: 'timeGridWeek',
        events: [],
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