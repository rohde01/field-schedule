import type { Field } from '$lib/schemas/field';
import { updateScheduleEntry, selectedSchedule } from '../stores/schedules';
import type { ScheduleEntry } from '$lib/schemas/schedule';
import { writable } from 'svelte/store';
import { derived } from 'svelte/store';
import { browser } from '$app/environment';
import * as rrulelib from 'rrule';
import { createUTCDate, getTimeFromDate, normalizeTime, currentDate, isSameDay } from './dateUtils';
const { RRuleSet, rrulestr } = rrulelib;

// Helper functions for recurrence logic
function parseRecurrenceFrequency(recurrenceRule: string | null | undefined): string {
  if (!recurrenceRule) return 'WEEKLY';
  const freqMatch = recurrenceRule.match(/FREQ=(\w+)/);
  return freqMatch ? freqMatch[1] : 'WEEKLY';
}

function createRecurrenceRule(frequency: string): string {
  return `FREQ=${frequency}`;
}

function isRecurringMaster(entry: ScheduleEntry): boolean {
  return !!entry.recurrence_rule && !entry.recurrence_id;
}

function isRecurrenceException(entry: ScheduleEntry): boolean {
  return !!entry.recurrence_id;
}

function isStandaloneEntry(entry: ScheduleEntry): boolean {
  return !entry.recurrence_rule && !entry.recurrence_id;
}

function canEditRecurrence(entry: ProcessedScheduleEntry): boolean {
  return !entry.isRecurring && !entry.recurrence_id;
}

export type ProcessedScheduleEntry = ScheduleEntry & {
  start_time: string;
  end_time: string;
  ui_id: string;
  isRecurring: boolean;
  original_instance_start?: Date; // immutable original start of generated recurring instance
};

// Store to control whether early time slots should be displayed
export const showEarlyTimeslots = writable(false);
export const timeSlots = writable<string[]>([]);

if (browser) {
  derived(
    [showEarlyTimeslots],
    ([$showEarlyTimeslots]) => {
      const earliestStart = $showEarlyTimeslots ? "05:45" : "13:45";
      const latestEnd = "23:45";
      const intervalMinutes = 15;
      return generateTimeSlots(earliestStart, latestEnd, intervalMinutes);
    }
  ).subscribe(val => timeSlots.set(val));
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
    const ruleText = ruleContent.startsWith('RRULE:') ? ruleContent : `RRULE:${ruleContent}`;
    const rule = rrulestr(ruleText, { dtstart });
    rruleSet.rrule(rule);
    if (entry.exdate && Array.isArray(entry.exdate)) {
      entry.exdate.forEach(exdate => { const exdateObj = createUTCDate(exdate); rruleSet.exdate(exdateObj); });
    }
    const { startDate, endDate } = getScheduleDateRange(schedule);
    const occurrences = rruleSet.between(startDate, endDate, true);
    const dtend = createUTCDate(entry.dtend); const durationMs = dtend.getTime() - dtstart.getTime();
    return occurrences.map(startOccurrenceDate => {
      const end = new Date(startOccurrenceDate.getTime() + durationMs);
      return { ...entry, schedule_entry_id: null, dtstart: startOccurrenceDate, dtend: end, start_time: getTimeFromDate(startOccurrenceDate), end_time: getTimeFromDate(end), ui_id: `${entry.uid}-${startOccurrenceDate.toISOString()}`, isRecurring: true, original_instance_start: new Date(startOccurrenceDate.getTime()) };
    });
  } catch (error) { console.error("Error creating recurring events:", error, entry.recurrence_rule); return []; }
}

function getScheduleDateRange(schedule: any) {
  let startDate, endDate;
  
  if (schedule?.active_from && schedule?.active_until) {
    startDate = createUTCDate(schedule.active_from);
    endDate = createUTCDate(schedule.active_until);
    endDate.setUTCHours(23, 59, 59, 999);
  } else {
    const currentYear = new Date().getFullYear();
    startDate = new Date(Date.UTC(currentYear - 1, 0, 1));
    endDate = new Date(Date.UTC(currentYear + 1, 11, 31, 23, 59, 59));
  }
  
  return { startDate, endDate };
}

function categorizeScheduleEntries(entries: ScheduleEntry[]) {
  const regularEntries: ScheduleEntry[] = [];
  const recurringMasters: ScheduleEntry[] = [];
  const exceptions: ScheduleEntry[] = [];
  
  entries.forEach(entry => {
    if (isRecurrenceException(entry)) {
      exceptions.push(entry);
    } else if (isRecurringMaster(entry)) {
      recurringMasters.push(entry);
    } else {
      regularEntries.push(entry);
    }
  });
  
  return { regularEntries, recurringMasters, exceptions };
}

function createProcessedEntry(entry: ScheduleEntry, uiIdPrefix: string, index: number, isRecurring = false): ProcessedScheduleEntry {
  const dtstart = createUTCDate(entry.dtstart);
  const dtend = createUTCDate(entry.dtend);
  return {
    ...entry,
    dtstart,
    dtend,
    start_time: getTimeFromDate(dtstart),
    end_time: getTimeFromDate(dtend),
    ui_id: `${uiIdPrefix}-${entry.uid}-${dtstart.toISOString()}-${index}`,
    isRecurring
  };
}

function getAllEntriesForDate(schedule: {schedule_entries?: ScheduleEntry[]} | null, date: Date): ProcessedScheduleEntry[] {
  if (!schedule) return [];
  
  const { regularEntries, recurringMasters, exceptions } = categorizeScheduleEntries(schedule.schedule_entries || []);
  console.debug('[getAllEntriesForDate] date', date.toISOString(), {
    total: (schedule.schedule_entries || []).length,
    regular: regularEntries.length,
    masters: recurringMasters.length,
    exceptions: exceptions.length
  });
  
  const oneTimeEntries = regularEntries
    .filter(entry => shouldShowEntryOnDate(entry, date))
    .map((entry, index) => createProcessedEntry(entry, 'onetime', index, false));

  const masterEntries = recurringMasters
    .filter(entry => shouldShowEntryOnDate(entry, date))
    .map((entry, index) => createProcessedEntry(entry, 'master', index, false));

  const exceptionEntries = exceptions
    .filter(entry => {
      const dtstart = createUTCDate(entry.dtstart);
      return isSameDay(dtstart, date);
    })
    .map((entry, index) => createProcessedEntry(entry, 'exception', index, false));

  const recurringEntries = processRecurringEvents(recurringMasters, exceptions, schedule, date);
  
  console.debug('[getAllEntriesForDate] result counts', {
    oneTime: oneTimeEntries.length,
    masterOriginals: masterEntries.length,
    exceptions: exceptionEntries.length,
    recurringGenerated: recurringEntries.length
  });
  return [...oneTimeEntries, ...masterEntries, ...exceptionEntries, ...recurringEntries];
}

function processRecurringEvents(
  recurringMasters: ScheduleEntry[], 
  exceptions: ScheduleEntry[], 
  schedule: any, 
  date: Date
): ProcessedScheduleEntry[] {
  const recurringEntries: ProcessedScheduleEntry[] = [];

  const exclusionMap = new Map<string, Set<number>>();
  const addExclusion = (uid: string, dateLike: any) => {
    try {
      const d = createUTCDate(dateLike);
      const ts = d.getTime();
      if (!exclusionMap.has(uid)) exclusionMap.set(uid, new Set());
      exclusionMap.get(uid)!.add(ts);
    } catch (err) {
      console.warn('[processRecurringEvents] failed to add exclusion', { uid, dateLike, err });
    }
  };
  recurringMasters.forEach(master => { if (master.exdate) master.exdate.forEach(d => addExclusion(master.uid, d)); });
  exceptions.forEach(ex => { if (ex.recurrence_id) addExclusion(ex.uid, ex.recurrence_id); });

  console.debug('[processRecurringEvents] start', {
    date: date.toISOString(),
    masters: recurringMasters.length,
    exceptions: exceptions.length,
    exclusionSummary: Array.from(exclusionMap.entries()).map(([uid,set]) => ({ uid, count: set.size }))
  });

  const seenRecurringIds = new Set<string>();
  let recurringIndex = 0;

  recurringMasters.forEach(master => {
    const masterOriginalStartTs = createUTCDate(master.dtstart).getTime();
    const exclusionSet = exclusionMap.get(master.uid) || new Set<number>();
    const instances = createRecurringEvents(master, schedule).filter(instance => isSameDay(instance.dtstart, date));

    console.debug('[processRecurringEvents] master expand', {
      uid: master.uid,
      instances: instances.length,
      exclusionCount: exclusionSet.size,
      masterOriginalStart: masterOriginalStartTs
    });

    instances.forEach(instance => {
      const instTs = instance.dtstart.getTime();
      const skipOriginal = instTs === masterOriginalStartTs;
      const skipExcluded = exclusionSet.has(instTs);
      const instanceKey = `${master.uid}-${instTs}`;
      const skipSeen = seenRecurringIds.has(instanceKey);
      if (skipOriginal || skipExcluded || skipSeen) {
        console.debug('[processRecurringEvents] skip instance', {
          uid: master.uid,
            inst: instance.dtstart.toISOString(),
            skipOriginal,
            skipExcluded,
            skipSeen
        });
        return;
      }
      seenRecurringIds.add(instanceKey);
      instance.ui_id = `recurring-${master.uid}-${instance.dtstart.toISOString()}-${recurringIndex}`;
      instance.isRecurring = true;
      recurringEntries.push(instance);
      console.debug('[processRecurringEvents] add instance', { uid: master.uid, ui_id: instance.ui_id });
      recurringIndex++;
    });
  });
  console.debug('[processRecurringEvents] done', { generated: recurringEntries.length });
  return recurringEntries;
}

export const processedEntries = writable<ProcessedScheduleEntry[]>([]);

// Populate processedEntries on state change
if (browser) {
  derived(
    [selectedSchedule, currentDate],
    ([$selectedSchedule, $currentDate]) => {
      if (!$selectedSchedule) return [];
      const entries = getAllEntriesForDate($selectedSchedule, $currentDate);
      return entries;
    }
  ).subscribe(val => {
    console.log('processedEntries updated:', val);
    processedEntries.update(currentEntries => {
      const preservedEntries = val.map(newEntry => {
        // Only preserve ui_id if previous entry matches both time and recurrence exception status (to avoid copying from mutated recurring to exception)
        const existing = currentEntries.find(e => 
          e.uid === newEntry.uid &&
          e.dtstart.getTime() === newEntry.dtstart.getTime() &&
          (!!e.recurrence_id === !!newEntry.recurrence_id)
        );
        if (existing) {
          if (existing.ui_id !== newEntry.ui_id) {
            console.debug('[processedEntries] preserve ui_id', { old: existing.ui_id, incoming: newEntry.ui_id, uid: newEntry.uid, start: newEntry.dtstart.toISOString(), recurrence_id: newEntry.recurrence_id });
          }
          return { ...newEntry, ui_id: existing.ui_id };
        }
        return newEntry;
      });
      const seen = new Set<string>(); const duplicates: any[] = [];
      const unique = preservedEntries.map((e, idx) => {
        if (!seen.has(e.ui_id)) { seen.add(e.ui_id); return e; }
        const newId = `${e.ui_id}-d${idx}`; duplicates.push({ original: e.ui_id, newId, idx, uid: e.uid, start: e.dtstart.toISOString(), recurrence_id: e.recurrence_id });
        return { ...e, ui_id: newId };
      });
      if (duplicates.length) {
        console.warn('[processedEntries] duplicate ui_ids detected', duplicates);
        const byUid: Record<string, number> = {}; unique.forEach(u => { byUid[u.ui_id] = (byUid[u.ui_id] || 0) + 1; });
        console.warn('[processedEntries] current ui_id counts snapshot', byUid);
      }
      return unique;
    });
  });
} else { writable<ProcessedScheduleEntry[]>([]); }

export { 
  parseRecurrenceFrequency, 
  createRecurrenceRule, 
  canEditRecurrence,
  isRecurringMaster,
  isRecurrenceException,
  isStandaloneEntry
};

export function getOriginalRecurrenceStart(entry: any): string | null {
  if (entry.isRecurring) {
    return entry.dtstart instanceof Date ? entry.dtstart.toISOString() : entry.dtstart;
  } else if (entry.recurrence_id) {
    return entry.recurrence_id instanceof Date ? entry.recurrence_id.toISOString() : entry.recurrence_id;
  } else {
    return null;
  }
}

export function commitUpdate(entry: any, originalRecurrence: string | null) {
  console.log('🔧 commitUpdate called:', {
    entry_uid: entry.uid,
    entry_schedule_id: entry.schedule_id,
    originalRecurrence,
    entry_field_id: entry.field_id,
    entry_summary: entry.summary
  });
  
  updateScheduleEntry({
    uid: entry.uid,
    schedule_id: entry.schedule_id,
    field_id: entry.field_id,
    dtstart: entry.dtstart,
    dtend: entry.dtend,
    team_id: entry.team_id,
    summary: entry.summary,
    recurrence_rule: entry.recurrence_rule,
    recurrence_id: originalRecurrence
      ? new Date(originalRecurrence)
      : (entry.recurrence_id ? new Date(entry.recurrence_id) : null)
  });
}

export function getEntryTitle(entry: ProcessedScheduleEntry, teamNameLookup: Map<number, string>): string {
  if (entry.summary) return entry.summary;
  if (entry.team_id != null) return teamNameLookup.get(entry.team_id) ?? `Team ${entry.team_id}`;
  return 'Untitled Event';
}
