<script lang="ts">
    import { browser } from '$app/environment';
    import Calendar from '@event-calendar/core';
    import type { default as EC } from '@event-calendar/core';
    import TimeGrid from '@event-calendar/time-grid';
    import DayGrid from '@event-calendar/day-grid';
    import Interaction from '@event-calendar/interaction';
    import '@event-calendar/core/index.css';
    import { activeSchedules } from '../../stores/activeSchedules';
    import { schedules } from '../../stores/schedules';
    import ActiveInfoCard from './ActiveInfoCard.svelte';

    let plugins = [TimeGrid, DayGrid, Interaction];
    let showEventCard = false;
    let selectedDate: Date = new Date();
    let cardPosition: { x: number; y: number } = { x: 0, y: 0 };
    let editingEvent: any = null;
    
    // Variables for double-click detection
    let lastClickTime = 0;
    let lastClickedEvent: any = null;
    let lastClickedDate: Date | null = null;
    const doubleClickInterval = 300; // ms
    
    const handleMouseEnter = () => {
    };

    const handleMouseLeave = () => {
    };
    
    // Convert active schedules to calendar events
    $: calendarEvents = $activeSchedules.map(schedule => {
        const scheduleName = $schedules.find(s => s.schedule_id === schedule.schedule_id)?.name ?? `Schedule ${schedule.schedule_id}`;
        return {
            id: schedule.active_schedule_id,
            title: scheduleName,
            start: new Date(schedule.start_date),
            end: new Date(schedule.end_date),
            allDay: true,
            mouseenter: handleMouseEnter,
            mouseleave: handleMouseLeave
        };
    });

    type DomEvent = EC.DomEvent;
    type DateClickInfo = EC.DateClickInfo;

    $: options = {
        view: 'dayGridMonth',
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
        // Implement manual double-click detection for events
        eventClick: (info: any) => {
            const currentTime = new Date().getTime();
            const isSameEvent = lastClickedEvent && 
                lastClickedEvent.id === info.event.id;
            
            if (isSameEvent && (currentTime - lastClickTime) < doubleClickInterval) {
                // Double click detected
                const activeSchedule = $activeSchedules.find(
                    schedule => schedule.active_schedule_id === parseInt(info.event.id)
                );
                if (activeSchedule) {
                    editingEvent = activeSchedule;
                    cardPosition = { 
                        x: info.jsEvent.clientX, 
                        y: info.jsEvent.clientY 
                    };
                    showEventCard = true;
                }
                lastClickTime = 0;
                lastClickedEvent = null;
            } else {
                lastClickTime = currentTime;
                lastClickedEvent = info.event;
            }
        },
        dateClick: (info: DateClickInfo) => {
            const currentTime = new Date().getTime();
            const isSameDate = lastClickedDate && 
                lastClickedDate.getTime() === info.date.getTime();
                
            if (isSameDate && (currentTime - lastClickTime) < doubleClickInterval) {

                const newSchedule = {
                    active_schedule_id: -Math.floor(Math.random() * 10000 + 1),
                    schedule_id: $schedules[0]?.schedule_id || 0,
                    start_date: info.date.toISOString(),
                    end_date: new Date(info.date).toISOString(),
                    is_active: true
                };
                
                activeSchedules.add(newSchedule);
                editingEvent = newSchedule;
                
                const mouseEvent = info.jsEvent as MouseEvent;
                cardPosition = { 
                    x: mouseEvent.clientX, 
                    y: mouseEvent.clientY 
                };
                selectedDate = info.date;
                showEventCard = true;
                
                lastClickTime = 0;
                lastClickedDate = null;
            } else {
                lastClickTime = currentTime;
                lastClickedDate = info.date;
            }
        }
    };

    // Svelte action for click outside detection
    function clickOutside(node: HTMLElement, callback: () => void) {
        const handleClick = (event: MouseEvent) => {
            if (node && !node.contains(event.target as Node)) {
                callback();
            }
        };
        
        // Add event listener with a small delay to avoid the initial click
        const timeoutId = setTimeout(() => {
            document.addEventListener('click', handleClick, true);
        }, 10);
        
        return {
            destroy() {
                clearTimeout(timeoutId);
                document.removeEventListener('click', handleClick, true);
            }
        };
    }

    function closeEventCard(): void {
        showEventCard = false;
        editingEvent = null;  // Reset editing event when closing
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
        <div use:clickOutside={closeEventCard}>
            <ActiveInfoCard 
                position={cardPosition}
                onClose={closeEventCard}
                editingEvent={editingEvent}
            />
        </div>
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