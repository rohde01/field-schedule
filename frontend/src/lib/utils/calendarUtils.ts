import type { Field } from '$lib/schemas/field';
import type { ScheduleEntry } from '$lib/schemas/schedule';
import { writable } from 'svelte/store';
import { derived } from 'svelte/store';
import { dropdownState } from '../../stores/ScheduleDropdownState';
import { browser } from '$app/environment';
import * as rrulelib from 'rrule';
const { RRuleSet, rrulestr, RRule } = rrulelib;

// Helper function to create dates in the correct UTC format as recommended by RRule docs
function datetime(year, month, day, hour = 0, minute = 0, second = 0) {
  return new Date(Date.UTC(year, month - 1, day, hour, minute, second));
}

export type ProcessedScheduleEntry = ScheduleEntry & {
  start_time: string;
  end_time: string;
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

// Get only the weekday name
export function formatWeekdayOnly(date: Date): string {
  return weekDays[date.getDay()];
}

// Check if a schedule is a draft schedule (no active dates)
export function isDraftSchedule(schedule: any): boolean {
  return !schedule?.active_from || !schedule?.active_until;
}

export function getTimeFromDate(date: Date | string): string {
  if (date instanceof Date) {
    return date.toTimeString().slice(0, 5);
  } else if (typeof date === 'string') {

    const timePart = date.split('T')[1];
    if (timePart) {
      return timePart.substring(0, 5);
    }
    return normalizeTime(date);
  }
  return "00:00";
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

function createRecurringEvents(entry: ScheduleEntry, schedule: any): ProcessedScheduleEntry[] {
  if (!entry.recurrence_rule) return [];

  try {
    // Create RRuleSet
    const rruleSet = new RRuleSet();
    
    // Parse the original start date to extract components
    const dtstart = new Date(entry.dtstart);
    const dtstartYear = dtstart.getFullYear();
    const dtstartMonth = dtstart.getMonth() + 1; // Month is 0-indexed in JS Date, but 1-indexed in our helper
    const dtstartDay = dtstart.getDate();
    const dtstartHours = dtstart.getHours();
    const dtstartMinutes = dtstart.getMinutes();
    
    // Create a proper UTC date for RRule using the helper
    const dtstartUTC = datetime(dtstartYear, dtstartMonth, dtstartDay, dtstartHours, dtstartMinutes);
    
    // Parse the recurrence rule
    const ruleContent = entry.recurrence_rule.startsWith('RRULE:') 
      ? entry.recurrence_rule
      : `RRULE:${entry.recurrence_rule}`;
    
    // Create the rule with proper DTSTART in UTC
    const options = RRule.parseString(ruleContent);
    options.dtstart = dtstartUTC;
    const rule = new RRule(options);
    rruleSet.rrule(rule);

    // Process exclusion dates if any - using proper UTC dates
    if (entry.exdate && Array.isArray(entry.exdate)) {
      entry.exdate.forEach(exdate => {
        const exdateObj = new Date(exdate);
        // Create a proper UTC exclusion date
        const exYear = exdateObj.getFullYear();
        const exMonth = exdateObj.getMonth() + 1; // Month is 0-indexed in JS Date, but 1-indexed in our helper
        const exDay = exdateObj.getDate();
        const exHours = exdateObj.getHours();
        const exMinutes = exdateObj.getMinutes();
        
        const exdateUTC = datetime(exYear, exMonth, exDay, exHours, exMinutes);
        rruleSet.exdate(exdateUTC);
      });
    }

    // Convert schedule dates to UTC format
    const [activeFromYear, activeFromMonth, activeFromDay] = schedule.active_from.split('-').map(Number);
    const [activeUntilYear, activeUntilMonth, activeUntilDay] = schedule.active_until.split('-').map(Number);
    
    const startDate = datetime(activeFromYear, activeFromMonth, activeFromDay);
    const endDate = datetime(activeUntilYear, activeUntilMonth, activeUntilDay, 23, 59, 59);

    // Get all occurrences within the schedule's date range using RRule's UTC handling
    const occurrences = rruleSet.between(startDate, endDate, true);
    
    // Calculate duration in milliseconds from original entry
    const durationMs = new Date(entry.dtend).getTime() - new Date(entry.dtstart).getTime();
    
    return occurrences.map(date => {
      // Create a new date with the original event's time components
      // Note that we're using the hours/minutes extracted from original entry
      const correctedDate = new Date(
        date.getUTCFullYear(),
        date.getUTCMonth(),
        date.getUTCDate(),
        dtstartHours,
        dtstartMinutes
      );
      
      // Create end date by adding the original duration
      const endDate = new Date(correctedDate.getTime() + durationMs);
      
      return {
        ...entry,
        dtstart: correctedDate,
        dtend: endDate,
        start_time: getTimeFromDate(correctedDate),
        end_time: getTimeFromDate(endDate)
      };
    });
  } catch (error) {
    console.error("Error creating recurring events:", error, entry.recurrence_rule);
    return [];
  }
}

// Find matching exception for a recurring event instance
function findExceptionForDate(exceptions: ScheduleEntry[], date: Date, masterUid: string): ScheduleEntry | undefined {
  return exceptions.find(exception => {
    if (!exception.recurrence_id || exception.uid !== masterUid) return false;
    
    const exceptionDate = new Date(exception.recurrence_id);
    
    // Compare year, month, day, hour, and minute to match events regardless of timezone
    return exceptionDate.getFullYear() === date.getFullYear() &&
           exceptionDate.getMonth() === date.getMonth() &&
           exceptionDate.getDate() === date.getDate() &&
           exceptionDate.getHours() === date.getHours() &&
           exceptionDate.getMinutes() === date.getMinutes();
  });
}

function getAllEntriesForDate(schedule: {schedule_entries?: ScheduleEntry[]} | null, date: Date): ProcessedScheduleEntry[] {
  if (!schedule) return [];
  
  const entries = schedule.schedule_entries || [];
  
  // If this is a draft schedule, only return master recurring entries
  if (isDraftSchedule(schedule)) {
    return entries
      .filter(entry => entry.recurrence_rule)
      .filter(entry => {
        const entryDate = new Date(entry.dtstart);
        return entryDate.getDay() === date.getDay();
      })
      .map(entry => ({
        ...entry,
        start_time: getTimeFromDate(entry.dtstart),
        end_time: getTimeFromDate(entry.dtend)
      }));
  }
  
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
    
  const recurringEntries: ProcessedScheduleEntry[] = [];
  
  recurringMasters.forEach(master => {
    const instances = createRecurringEvents(master, schedule)
      .filter(instance => shouldShowEntryOnDate(instance, date));
    
    instances.forEach(instance => {
      // Use exception if one exists for this date, otherwise use the instance
      const exception = findExceptionForDate(exceptions, new Date(instance.dtstart), master.uid);
      
      if (exception) {
        recurringEntries.push({
          ...exception,
          start_time: getTimeFromDate(exception.dtstart),
          end_time: getTimeFromDate(exception.dtend)
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
    console.log("Processed Entries:", entries);
    return entries;
  }
) : writable([]);
