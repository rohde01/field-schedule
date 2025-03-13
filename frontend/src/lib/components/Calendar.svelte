<script lang="ts">
    import { browser } from '$app/environment';
    import Calendar from '@event-calendar/core';
    import type { default as EC } from '@event-calendar/core';
    import TimeGrid from '@event-calendar/time-grid';
    import DayGrid from '@event-calendar/day-grid';
    import Interaction from '@event-calendar/interaction';
    import '@event-calendar/core/index.css';
    import { activeSchedules } from '../../stores/activeSchedules';
    import ActiveInfoCard from './ActiveInfoCard.svelte';

    let plugins = [TimeGrid, DayGrid, Interaction];
    let showEventCard = false;
    let selectedDate: Date = new Date();
    let cardPosition: { x: number; y: number } = { x: 0, y: 0 };
    
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

    type DomEvent = EC.DomEvent;
    type DateClickInfo = EC.DateClickInfo;

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
        },
        selectable: true,
        dateClick: (info: DateClickInfo) => {
            selectedDate = info.date;
            const mouseEvent = info.jsEvent as unknown as MouseEvent;
            cardPosition = { 
                x: mouseEvent.clientX, 
                y: mouseEvent.clientY 
            };
            showEventCard = true;
        }
    };

    function closeEventCard(): void {
        showEventCard = false;
    }

    function handleKeydown(event: KeyboardEvent): void {
        if (event.key === 'Escape') {
            closeEventCard();
        }
    }
</script>

<svelte:window on:keydown={handleKeydown} />

<div class="calendar-wrapper">
    {#if browser}
        <Calendar {plugins} {options} />
    {/if}
    
    {#if showEventCard}
        <ActiveInfoCard 
            position={cardPosition}
            selectedDate={selectedDate}
            onClose={closeEventCard}
        />
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