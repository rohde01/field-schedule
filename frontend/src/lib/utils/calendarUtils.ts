import type { Field } from '$lib/schemas/field';
import type { ScheduleEntry } from '$lib/schemas/schedule';
import { writable } from 'svelte/store';
import { derived } from 'svelte/store';
import { dropdownState } from '../../stores/ScheduleDropdownState';
import { browser } from '$app/environment';
import * as rrulelib from 'rrule';
import { createUTCDate, getTimeFromDate, normalizeTime, currentDate } from './dateUtils';
const { RRuleSet, rrulestr } = rrulelib;

export type ProcessedScheduleEntry = ScheduleEntry & {
  start_time: string;
  end_time: string;
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
    new Date(entryDateString + 'Z') : 
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
        dtstart: startOccurrenceDate,
        dtend: end,
        start_time: getTimeFromDate(startOccurrenceDate),
        end_time: getTimeFromDate(end)
      };
    });
  } catch (error) {
    console.error("Error creating recurring events:", error, entry.recurrence_rule);
    return [];
  }
}

function findExceptionForDate(exceptions: ScheduleEntry[], date: Date, masterUid: string): ScheduleEntry | undefined {
  return exceptions.find(exception => {
    if (!exception.recurrence_id || exception.uid !== masterUid) return false;
    
    const exceptionDate = createUTCDate(exception.recurrence_id);
    const eventTime = date.getTime();
    const exceptionTime = exceptionDate.getTime();
    return Math.abs(exceptionTime - eventTime) < 60000;
  });
}

function getAllEntriesForDate(schedule: {schedule_entries?: ScheduleEntry[]} | null, date: Date): ProcessedScheduleEntry[] {
  if (!schedule) return [];
  
  const entries = schedule.schedule_entries || [];
  
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
          end_time: getTimeFromDate(dtend)
        };
      });
  }
  
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
        end_time: getTimeFromDate(dtend)
      };
    });
    
  const recurringEntries: ProcessedScheduleEntry[] = [];
  
  recurringMasters.forEach(master => {
    const instances = createRecurringEvents(master, schedule)
      .filter(instance => shouldShowEntryOnDate(instance, date));
    
    instances.forEach(instance => {
      const exception = findExceptionForDate(exceptions, instance.dtstart, master.uid);
      
      if (exception) {
        const exDtstart = createUTCDate(exception.dtstart);
        const exDtend = createUTCDate(exception.dtend);
        recurringEntries.push({
          ...exception,
          dtstart: exDtstart,
          dtend: exDtend,
          start_time: getTimeFromDate(exDtstart),
          end_time: getTimeFromDate(exDtend)
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
    const entries = getAllEntriesForDate(selectedSchedule, $currentDate);
    return entries;
  }
) : writable([]);
