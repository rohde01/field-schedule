import type { Field } from '$lib/schemas/field';
import type { ScheduleEntry } from '$lib/schemas/schedule';
import { writable } from 'svelte/store';
import { derived } from 'svelte/store';
import { dropdownState } from '../../stores/ScheduleDropdownState';
import { browser } from '$app/environment';

export const currentWeekDay = writable(0);
export const weekDays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];

export const activeEvents = browser ? derived(dropdownState, ($dropdownState): ScheduleEntry[] => {
  const selectedSchedule = $dropdownState.selectedSchedule;
  if (!selectedSchedule) return [];
  return selectedSchedule.schedule_entries;
}) : writable([]);

export const timeSlots = writable((() => {
  if (!browser) return [];
  const earliestStart = "16:00";
  const latestEnd = "20:30";
  const intervalMinutes = 15;
  return generateTimeSlots(earliestStart, latestEnd, intervalMinutes);
})());

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
  currentWeekDay.update(day => (day + 1) % 7);
}

export function previousDay() {
  currentWeekDay.update(day => (day - 1 + 7) % 7);
}

export function getEventContentVisibility(startRow: number, endRow: number) {
  const rowsSpanned = endRow - startRow + 1;
  
  return {
    showTeamName: true,
    showField: rowsSpanned >= 2,
    showTime: rowsSpanned >= 3
  };
}

export function getWeekDayFromRRule(rrule: string | null | undefined): number | null {
  if (!rrule) return null;
  const match = rrule.match(/BYDAY=([A-Z]{2})/);
  if (!match) return null;
  const dayMap: { [key: string]: number } = { MO: 0, TU: 1, WE: 2, TH: 3, FR: 4, SA: 5, SU: 6 };
  return dayMap[match[1]];
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


