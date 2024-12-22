declare module '@event-calendar/core';
declare module '@event-calendar/resource-time-grid';
declare module '@event-calendar/resource-timeline';

export interface CalendarResource {
    id: string;
    title: string;
    parentId: string | null;
    children: CalendarResource[];
}

export interface CalendarEvent {
    id?: string;
    title: string;
    start: string;
    end: string;
    resourceId: string;
}
