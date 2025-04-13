import type { Field } from '$lib/schemas/field';
import type { ScheduleEntry } from '$lib/schemas/schedule';
import { writable } from 'svelte/store';
import { derived } from 'svelte/store';
import { dropdownState } from '../../stores/ScheduleDropdownState';
import { browser } from '$app/environment';
import * as rrulelib from 'rrule';
const { RRuleSet, rrulestr } = rrulelib;

type RRuleSetType = typeof RRuleSet;

export type ProcessedScheduleEntry = ScheduleEntry & {
  start_time: string;
  end_time: string;
  master_schedule_entry_id?: number;
};

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

export function getEntryEndRow(endTime: string, timeSlots: string[]): number {
  const endTimeNormalized = normalizeTime(endTime);
  const lastOccupiedSlot = timeSlots.findIndex(slot => slot >= endTimeNormalized) - 1;
  return lastOccupiedSlot + 2; 
}

export function getRowForTimeWithSlots(time: string, timeSlots: string[]): number {
  return rowForTime(time, timeSlots);
}

export function getEntryRowEndWithSlots(endTime: string, timeSlots: string[]): number {
  return getEntryEndRow(endTime, timeSlots);
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

export function getEntryContentVisibility(startRow: number, endRow: number) {
  const rowsSpanned = endRow - startRow + 1;
  
  return {
    showTeamName: true,
    showField: rowsSpanned >= 2,
    showTime: rowsSpanned >= 3 
  };
}

export function isSameDay(date1: Date, date2: Date): boolean {
  return date1.getFullYear() === date2.getFullYear() &&
         date1.getMonth() === date2.getMonth() &&
         date1.getDate() === date2.getDate();
}

// SCHEDULE ENTRIES SECTION
export function shouldShowEntryOnDate(entry: ScheduleEntry, date: Date): boolean {
  const entryDate = new Date(entry.dtstart);
  return isSameDay(entryDate, date);
}

function createRecurringEvents(entry: ScheduleEntry, startDate: Date, endDate: Date): ProcessedScheduleEntry[] {
  if (!entry.recurrence_rule) return [];

  try {
    // Create RRuleSet and parse the recurrence rule
    const rruleSet = new RRuleSet();
    const dtstart = new Date(entry.dtstart);
    
    const ruleContent = entry.recurrence_rule.startsWith('RRULE:') 
      ? entry.recurrence_rule
      : `RRULE:${entry.recurrence_rule}`;
      
    const ruleString = `DTSTART:${dtstart.toISOString().replace(/[-:]/g, '').split('.')[0]}Z\n${ruleContent}`;
    const rule = rrulestr(ruleString);
    rruleSet.rrule(rule);

    // Process exclusion dates if any
    if (entry.exdate && Array.isArray(entry.exdate)) {
      entry.exdate.forEach(exdate => {
        rruleSet.exdate(new Date(exdate));
      });
    }

    // Get all occurrences and generate entries for each date
    const occurrences = rruleSet.between(startDate, endDate, true);
    return occurrences.map(date => {
      const durationMs = new Date(entry.dtend).getTime() - new Date(entry.dtstart).getTime();
      const endDate = new Date(date.getTime() + durationMs);
      
      return {
        ...entry,
        dtstart: date,
        dtend: endDate,
        start_time: getTimeFromDate(date),
        end_time: getTimeFromDate(endDate),
        master_schedule_entry_id: entry.schedule_entry_id
      };
    });
  } catch (error) {
    console.error("Error creating recurring events:", error, entry.recurrence_rule);
    return [];
  }
}

// Find matching exception for a recurring event instance
function findExceptionForDate(exceptions: ScheduleEntry[], date: Date): ScheduleEntry | undefined {
  return exceptions.find(exception => {
    if (!exception.recurrence_id) return false;
    return isSameDay(new Date(exception.recurrence_id), date);
  });
}

function getAllEntriesForDate(schedule: {schedule_entries?: ScheduleEntry[]} | null, date: Date): ProcessedScheduleEntry[] {
  if (!schedule) return [];
  
  const entries = schedule.schedule_entries || [];
  
  // Categorize entries into regular, recurring masters, and exceptions
  const regularEntries: ScheduleEntry[] = [];
  const recurringMasters: ScheduleEntry[] = [];
  const exceptions: ScheduleEntry[] = [];
  
  entries.forEach(entry => {
    if (entry.recurrence_id) {
      exceptions.push(entry);
    } else if (entry.recurrence_rule) {
      recurringMasters.push(entry);
    } else {
      regularEntries.push(entry);
    }
  });
  
  // Process one-time entries for this day
  const oneTimeEntries = regularEntries
    .filter(entry => shouldShowEntryOnDate(entry, date))
    .map(entry => ({
      ...entry,
      start_time: getTimeFromDate(entry.dtstart),
      end_time: getTimeFromDate(entry.dtend)
    }));
    
  // Set date range for recurring events (30 days back and forward)
  const lookBackDate = new Date(date);
  lookBackDate.setDate(lookBackDate.getDate() - 30);
  
  const lookForwardDate = new Date(date);
  lookForwardDate.setDate(lookForwardDate.getDate() + 30);
    
  const recurringEntries: ProcessedScheduleEntry[] = [];
  
  recurringMasters.forEach(master => {
    // Get instances for this recurring pattern falling on our target date
    const instances = createRecurringEvents(master, lookBackDate, lookForwardDate)
      .filter(instance => shouldShowEntryOnDate(instance, date));
    
    instances.forEach(instance => {
      // Use exception if one exists for this date, otherwise use the instance
      const exception = findExceptionForDate(exceptions, new Date(instance.dtstart));
      
      if (exception) {
        recurringEntries.push({
          ...exception,
          start_time: getTimeFromDate(exception.dtstart),
          end_time: getTimeFromDate(exception.dtend),
          master_schedule_entry_id: master.schedule_entry_id
        });
      } else {
        recurringEntries.push(instance);
      }
    });
  });
  
  return [...oneTimeEntries, ...recurringEntries];
}

export const processedEntries = browser ? derived(
  [dropdownState, currentDate], 
  ([$dropdownState, $currentDate]) => {
    const selectedSchedule = $dropdownState.selectedSchedule;
    if (!selectedSchedule) return [];
    
    return getAllEntriesForDate(selectedSchedule, $currentDate);
  }
) : writable([]);
