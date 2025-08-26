// filepath: src/lib/utils/entryEditUtils.ts
import { processedEntries, getOriginalRecurrenceStart, commitUpdate } from './calendarUtils';
import { computeDateUTC } from './dateUtils';
import { get } from 'svelte/store';
import type { ProcessedScheduleEntry } from './calendarUtils';

function findEntry(ui_id: string): ProcessedScheduleEntry | undefined {
  return get(processedEntries).find(e => e.ui_id === ui_id);
}

export interface ApplyOptions {
  commit?: boolean;               // default true
  originalRecurrence?: string | null; // override original recurrence reference
}

export function applyEntryChanges(ui_id: string, changes: Partial<ProcessedScheduleEntry>, opts: ApplyOptions = {}) {
  const { commit = true, originalRecurrence } = opts;
  let updated: ProcessedScheduleEntry | undefined;
  processedEntries.update(list => list.map(e => {
    if (e.ui_id !== ui_id) return e;
    updated = { ...e, ...changes } as ProcessedScheduleEntry;
    return updated!;
  }));
  if (commit && updated) {
    const orig = originalRecurrence !== undefined ? originalRecurrence : getOriginalRecurrenceStart(updated);
    commitUpdate(updated, orig);
  }
}

export function updateEntryField<T extends keyof ProcessedScheduleEntry>(ui_id: string, field: T, value: ProcessedScheduleEntry[T], opts?: ApplyOptions) {
  applyEntryChanges(ui_id, { [field]: value } as any, opts);
}

export function updateEntryDate(ui_id: string, newDate: Date, opts?: ApplyOptions) {
  const entry = findEntry(ui_id);
  if (!entry) return;
  const dtstart = computeDateUTC(newDate, entry.start_time);
  const dtend = computeDateUTC(newDate, entry.end_time);
  applyEntryChanges(ui_id, { dtstart, dtend }, opts);
}

export function updateEntryTimeRange(ui_id: string, startTime: string, endTime: string, opts?: ApplyOptions) {
  const entry = findEntry(ui_id);
  if (!entry) return;
  const dtstart = computeDateUTC(entry.dtstart as Date, startTime);
  const dtend = computeDateUTC(entry.dtstart as Date, endTime);
  applyEntryChanges(ui_id, { start_time: startTime, end_time: endTime, dtstart, dtend }, opts);
}

export function updateEntryDateAndTime(ui_id: string, date: Date, startTime: string, endTime: string, opts?: ApplyOptions) {
  const dtstart = computeDateUTC(date, startTime);
  const dtend = computeDateUTC(date, endTime);
  applyEntryChanges(ui_id, { dtstart, dtend, start_time: startTime, end_time: endTime }, opts);
}

export function toggleRecurrence(ui_id: string, enable: boolean, rule: string | null, opts?: ApplyOptions) {
  applyEntryChanges(ui_id, { recurrence_rule: enable ? rule : null }, opts);
}
