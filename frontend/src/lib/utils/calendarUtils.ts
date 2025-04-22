import type { Field } from '$lib/schemas/field';
import { updateScheduleEntry } from '../../stores/schedules';
import type { ScheduleEntry } from '$lib/schemas/schedule';
import { writable } from 'svelte/store';
import { derived } from 'svelte/store';
import { dropdownState } from '../../stores/ScheduleDropdownState';
import { browser } from '$app/environment';
import * as rrulelib from 'rrule';
import { createUTCDate, getTimeFromDate, normalizeTime, currentDate, isSameDay } from './dateUtils';
const { RRuleSet, rrulestr } = rrulelib;

export type ProcessedScheduleEntry = ScheduleEntry & {
  start_time: string;
  end_time: string;
  ui_id: string;
  isRecurring: boolean;
};

export const timeSlots = writable((() => {
  if (!browser) return [];
  const earliestStart = "00:00";
  const latestEnd = "23:45";
  const intervalMinutes = 15;
  return generateTimeSlots(earliestStart, latestEnd, intervalMinutes);
})());

export function isDraftSchedule(schedule: any): boolean {
  return !schedule?.active_from || !schedule?.active_until;
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

export function getRowForTimeWithSlots(time: string, timeSlots: string[]): number {
  return timeSlots.indexOf(normalizeTime(time)) + 2;
}

export function getEntryRowEndWithSlots(endTime: string, timeSlots: string[]): number {
  const endTimeNormalized = normalizeTime(endTime);
  const lastOccupiedSlot = timeSlots.findIndex(slot => slot >= endTimeNormalized) - 1;
  return lastOccupiedSlot + 2; 
}

export function getEntryContentVisibility(startRow: number, endRow: number) {
  const rowsSpanned = endRow - startRow + 1;
  
  return {
    showTeamName: true,
    showField: rowsSpanned >= 2,
    showTime: rowsSpanned >= 3 
  };
}

export function shouldShowEntryOnDate(entry: ScheduleEntry, date: Date): boolean {
  const entryDateString = typeof entry.dtstart === 'string' ? entry.dtstart : null;
  const entryDate = entryDateString ? 
    createUTCDate(entryDateString) : 
    entry.dtstart;
  
  return entryDate.getUTCFullYear() === date.getUTCFullYear() &&
         entryDate.getUTCMonth() === date.getUTCMonth() &&
         entryDate.getUTCDate() === date.getUTCDate();
}

function createRecurringEvents(entry: ScheduleEntry, schedule: any): ProcessedScheduleEntry[] {
  if (!entry.recurrence_rule) return [];

  try {
    const rruleSet = new RRuleSet();
    const dtstart = createUTCDate(entry.dtstart);
    const ruleContent = entry.recurrence_rule;
    
    try {
      const ruleText = ruleContent.startsWith('RRULE:') ? ruleContent : `RRULE:${ruleContent}`;
      const rule = rrulestr(ruleText, { dtstart });
      rruleSet.rrule(rule);
    } catch (error) {
      console.warn("Error with rrulestr", error);
    }

    if (entry.exdate && Array.isArray(entry.exdate)) {
      entry.exdate.forEach(exdate => {
        const exdateObj = createUTCDate(exdate);
        rruleSet.exdate(exdateObj);
      });
    }

    let startDate, endDate;
    
    if (schedule.active_from && schedule.active_until) {
      startDate = createUTCDate(schedule.active_from);
      endDate = createUTCDate(schedule.active_until);
      endDate.setUTCHours(23, 59, 59, 999);
    } else {
      const currentYear = new Date().getFullYear();
      startDate = new Date(Date.UTC(currentYear - 1, 0, 1));
      endDate = new Date(Date.UTC(currentYear + 1, 11, 31, 23, 59, 59));
    }

    const occurrences = rruleSet.between(startDate, endDate, true);
    
    const dtend = createUTCDate(entry.dtend);
    const durationMs = dtend.getTime() - dtstart.getTime();
    
    return occurrences.map(startOccurrenceDate => {
      const end = new Date(startOccurrenceDate.getTime() + durationMs);

      return {
        ...entry,
        schedule_entry_id: null,
        dtstart: startOccurrenceDate,
        dtend: end,
        start_time: getTimeFromDate(startOccurrenceDate),
        end_time: getTimeFromDate(end),
        ui_id: `${entry.uid}-${startOccurrenceDate.toISOString()}`,
        isRecurring: true
      };
    });
  } catch (error) {
    console.error("Error creating recurring events:", error, entry.recurrence_rule);
    return [];
  }
}

function getAllEntriesForDate(schedule: {schedule_entries?: ScheduleEntry[]} | null, date: Date): ProcessedScheduleEntry[] {
  if (!schedule) return [];

  const entries = schedule.schedule_entries || [];

  // --- Draft Schedule Handling ---
  if (isDraftSchedule(schedule)) {
    return entries
      .filter(entry => entry.recurrence_rule)
      .filter(entry => {
        const entryDate = createUTCDate(entry.dtstart);
        return entryDate.getUTCDay() === date.getUTCDay();
      })
      .map(entry => {
        const dtstart = createUTCDate(entry.dtstart);
        const dtend = createUTCDate(entry.dtend);
        return {
          ...entry,
          dtstart,
          dtend,
          start_time: getTimeFromDate(dtstart),
          end_time: getTimeFromDate(dtend),
          ui_id: `${entry.uid}-${dtstart.toISOString()}`,
          isRecurring: false 
        };
      });
  }
  
  // Categorize all entries
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
  
  // Process single occurrences (non-recurring events)
  const oneTimeEntries = regularEntries
    .filter(entry => shouldShowEntryOnDate(entry, date))
    .map(entry => {
      const dtstart = createUTCDate(entry.dtstart);
      const dtend = createUTCDate(entry.dtend);
      return {
        ...entry,
        dtstart,
        dtend,
        start_time: getTimeFromDate(dtstart),
        end_time: getTimeFromDate(dtend),
        ui_id: `${entry.uid}-${dtstart.toISOString()}`,
        isRecurring: false
      };
    });

  // Process exceptions for this date - only include exceptions that match this date
  const exceptionEntries = exceptions
    .filter(entry => {
      const dtstart = createUTCDate(entry.dtstart);
      return isSameDay(dtstart, date);
    })
    .map(entry => {
      const dtstart = createUTCDate(entry.dtstart);
      const dtend = createUTCDate(entry.dtend);
      return {
        ...entry,
        dtstart,
        dtend,
        start_time: getTimeFromDate(dtstart),
        end_time: getTimeFromDate(dtend),
        ui_id: `${entry.uid}-${dtstart.toISOString()}`,
        isRecurring: false
      };
    });

  // Process recurring entries
  const recurringEntries: ProcessedScheduleEntry[] = [];
  
  // Create a set of all exception dates per master UID for quick lookup
  const masterExceptions: Map<string, Date[]> = new Map();
  exceptions.forEach(exception => {
    if (!exception.recurrence_id || !exception.uid) return;
    
    const exDate = createUTCDate(exception.recurrence_id);
    if (!masterExceptions.has(exception.uid)) {
      masterExceptions.set(exception.uid, []);
    }
    masterExceptions.get(exception.uid)?.push(exDate);
  });

  recurringMasters.forEach(master => {
    // Get all occurrences for this master event on the selected date
    const instances = createRecurringEvents(master, schedule)
      .filter(instance => isSameDay(instance.dtstart, date));
    
    // Filter out instances that match an exception's recurrence ID
    const exceptDates = masterExceptions.get(master.uid) || [];
    
    instances.forEach(instance => {
      const hasMatchingException = exceptDates.some(exceptDate => 
        isSameDay(exceptDate, instance.dtstart) && 
        exceptDate.getUTCHours() === instance.dtstart.getUTCHours() && 
        exceptDate.getUTCMinutes() === instance.dtstart.getUTCMinutes()
      );
      
      // Only add instances that don't have exceptions replacing them
      if (!hasMatchingException) {
        recurringEntries.push(instance);
      }
    });
  });
  
  return [...oneTimeEntries, ...exceptionEntries, ...recurringEntries];
}

export const processedEntries = writable<ProcessedScheduleEntry[]>([]);

// Populate processedEntries on state change
if (browser) {
  derived(
    [dropdownState, currentDate],
    ([$dropdownState, $currentDate]) => {
      const selectedSchedule = $dropdownState.selectedSchedule;
      if (!selectedSchedule) return [];
      const entries = getAllEntriesForDate(selectedSchedule, $currentDate);
      const processed = entries.map(entry => {
        const dtstampStr = entry.dtstart instanceof Date
          ? entry.dtstart.toISOString()
          : typeof entry.dtstart === 'string'
            ? entry.dtstart
            : '';
        return {
          ...entry,
          ui_id: `${entry.uid}-${dtstampStr}`
        };
      });
      console.log('Processed Entries:', processed);
      return processed;
    }
  ).subscribe(val => processedEntries.set(val));
} else {
  // Server-side fallback
  writable<ProcessedScheduleEntry[]>([]);
}

// Determine original recurrence start time for update logic
export function getOriginalRecurrenceStart(entry: any): string | null {
  if (entry.isRecurring) {
    return entry.dtstart instanceof Date ? entry.dtstart.toISOString() : entry.dtstart;
  } else if (entry.recurrence_id) {
    return entry.recurrence_id instanceof Date ? entry.recurrence_id.toISOString() : entry.recurrence_id;
  } else {
    return null;
  }
}

// Commit schedule update using processed entry and original recurrence
export function commitUpdate(entry: any, originalRecurrence: string | null) {
  updateScheduleEntry({
    uid: entry.uid,
    schedule_id: entry.schedule_id,
    field_id: entry.field_id,
    dtstart: entry.dtstart,
    dtend: entry.dtend,
    recurrence_id: originalRecurrence
      ? new Date(originalRecurrence)
      : (entry.recurrence_id ? new Date(entry.recurrence_id) : null)
  });
}
