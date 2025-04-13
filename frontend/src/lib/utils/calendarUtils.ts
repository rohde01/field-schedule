import type { Field } from '$lib/schemas/field';
import type { ScheduleEntry } from '$lib/schemas/schedule';
import { writable } from 'svelte/store';
import { derived } from 'svelte/store';
import { dropdownState } from '../../stores/ScheduleDropdownState';
import { browser } from '$app/environment';

export const currentDate = writable(new Date());
export const weekDays = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];

// Derive current weekday from the date using JavaScript's standard (0=Sunday, 6=Saturday)
export const currentWeekDay = derived(currentDate, ($currentDate) => {
  return $currentDate.getDay();
});

export const timeSlots = writable((() => {
  if (!browser) return [];
  const earliestStart = "16:00";
  const latestEnd = "20:30";
  const intervalMinutes = 15;
  return generateTimeSlots(earliestStart, latestEnd, intervalMinutes);
})());

// Format the date as "Monday, January 1, 2023"
export function formatDate(date: Date): string {
  return `${weekDays[date.getDay()]}, ${date.toLocaleDateString('en-US', { 
    month: 'long', 
    day: 'numeric',
    year: 'numeric'
  })}`;
}

export function getTimeFromDate(date: Date | string): string {
  if (date instanceof Date) {
    return date.toTimeString().slice(0, 5);
  } else if (typeof date === 'string') {
    // Extract time from ISO format string like "2025-04-07T17:00:00"
    const timePart = date.split('T')[1];
    if (timePart) {
      return timePart.substring(0, 5); // Get HH:MM part
    }
    return normalizeTime(date);
  }
  return "00:00"; // Default fallback
}

// Get weekday index using JavaScript's standard (0=Sunday, 6=Saturday) from a date
export function getCurrentWeekday(date: Date): number {
  return date.getDay();
}

export function buildResources(allFields: Field[], selectedSchedule: any | null): Field[] {
    if (!selectedSchedule || !selectedSchedule.facility_id) return [];
    return allFields.filter(field => field.facility_id === selectedSchedule.facility_id);
}

export function generateTimeSlots(
    start: string,
    end: string,
    intervalMinutes: number
): string[] {
    const slots: string[] = [];
    let [startH, startM] = start.split(":").map(Number);
    const [endH, endM] = end.split(":").map(Number);
  
    let currentMinutes = startH * 60 + startM;
    const endTotalMinutes = endH * 60 + endM;
  
    while (currentMinutes <= endTotalMinutes) {
      const hh = Math.floor(currentMinutes / 60).toString().padStart(2, "0");
      const mm = (currentMinutes % 60).toString().padStart(2, "0");
      slots.push(`${hh}:${mm}`);
      currentMinutes += intervalMinutes;
    }
  
    return slots;
}

export function normalizeTime(time: string): string {
  return time.slice(0, 5);
}

export function rowForTime(time: string, timeSlots: string[]): number {
  return timeSlots.indexOf(normalizeTime(time)) + 2;
}

export function getEventEndRow(endTime: string, timeSlots: string[]): number {
  const endTimeNormalized = normalizeTime(endTime);
  const lastOccupiedSlot = timeSlots.findIndex(slot => slot >= endTimeNormalized) - 1;
  return lastOccupiedSlot + 2; 
}

export function getRowForTimeWithSlots(time: string, timeSlots: string[]): number {
  return rowForTime(time, timeSlots);
}

export function getEventRowEndWithSlots(endTime: string, timeSlots: string[]): number {
  return getEventEndRow(endTime, timeSlots);
}

export function nextDay() {
  currentDate.update(date => {
    const newDate = new Date(date);
    newDate.setDate(date.getDate() + 1);
    return newDate;
  });
}

export function previousDay() {
  currentDate.update(date => {
    const newDate = new Date(date);
    newDate.setDate(date.getDate() - 1);
    return newDate;
  });
}

export function getEventContentVisibility(startRow: number, endRow: number) {
  const rowsSpanned = endRow - startRow + 1;
  
  return {
    showTeamName: true,
    showField: rowsSpanned >= 2,
    showTime: rowsSpanned >= 3
  };
}

// THIS SECTION HANDLES THE SCHEDULE ENTRIES

export const processedEvents = browser ? derived(dropdownState, ($dropdownState) => {
  const selectedSchedule = $dropdownState.selectedSchedule;
  if (!selectedSchedule) return [];
  
  // Process schedule entries to include time information
  return selectedSchedule.schedule_entries.map(event => ({
    ...event,
    start_time: getTimeFromDate(event.dtstart),
    end_time: getTimeFromDate(event.dtend)
  }));
}) : writable([]);

// Check if an event should be shown on a given date based on its dtstart date
export function shouldShowEventOnDate(event: ScheduleEntry, date: Date): boolean {
  const eventDate = new Date(event.dtstart);
  
  return isSameDay(eventDate, date);
}

// Compare two dates to see if they're the same day
export function isSameDay(date1: Date, date2: Date): boolean {
  return date1.getFullYear() === date2.getFullYear() &&
         date1.getMonth() === date2.getMonth() &&
         date1.getDate() === date2.getDate();
}