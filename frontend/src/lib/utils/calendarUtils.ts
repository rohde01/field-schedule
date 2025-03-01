import type { Field } from '$lib/schemas/field';
import type { Schedule } from '$lib/schemas/schedule';
import type { ScheduleEntry } from '$lib/schemas/schedule';
import { writable } from 'svelte/store';
import { derived } from 'svelte/store';
import { dropdownState } from '../../stores/ScheduleDropdownState';


export const currentWeekDay = writable(0);
export const timeSlotGranularity = writable(15);
export const weekDays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];

export const activeEvents = derived(dropdownState, ($dropdownState): ScheduleEntry[] => {
  const selectedSchedule = $dropdownState.selectedSchedule;
  if (!selectedSchedule) return [];
  return selectedSchedule.entries;
});

export const timeSlots = derived([timeSlotGranularity], ([$timeSlotGranularity]) => {
  const earliestStart = "16:00";
  const latestEnd = "20:30";
  
  return generateTimeSlots(earliestStart, latestEnd, $timeSlotGranularity);
});

export function buildResources(allFields: Field[], selectedSchedule: Schedule | null): Field[] {
    if (!selectedSchedule) return [];
    
    return allFields.filter(field => {
      if (field.facility_id !== selectedSchedule.facility_id) return false;
      
      const scheduleFieldIds = new Set(selectedSchedule.entries.map(entry => entry.field_id));
      
      if (scheduleFieldIds.has(field.field_id)) return true;
      
      const hasHalfFieldInSchedule = field.half_subfields.some(half => 
        scheduleFieldIds.has(half.field_id)
      );
      if (hasHalfFieldInSchedule) return true;
      
      const hasQuarterFieldInSchedule = field.quarter_subfields.some(quarter => 
        scheduleFieldIds.has(quarter.field_id)
      );
      if (hasQuarterFieldInSchedule) return true;
      
      return false;
    });
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

export function getNextDay(currentDay: number): number {
  return (currentDay + 1) % 7;
}

export function getPreviousDay(currentDay: number): number {
  return (currentDay - 1 + 7) % 7;
}

export function handleGranularityChange(e: Event) {
  const select = e.target as HTMLSelectElement;
  timeSlotGranularity.set(parseInt(select.value));
}
  
export function nextDay() {
  currentWeekDay.update(day => (day + 1) % 7);
}

export function previousDay() {
  currentWeekDay.update(day => (day - 1 + 7) % 7);
}

export function addMinutes(time: string, minutes: number): string {
  const [h, m] = time.split(':').map(Number);
  const total = h * 60 + m + minutes;
  const nh = Math.floor(total / 60) % 24;
  const nm = total % 60;
  return `${nh.toString().padStart(2, '0')}:${nm.toString().padStart(2, '0')}`;
}


