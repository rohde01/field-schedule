// filepath: src/lib/utils/entryEditUtils.ts
import { processedEntries, getOriginalRecurrenceStart, commitUpdate } from './calendarUtils';
import { computeDateUTC } from './dateUtils';
import { currentDate } from './dateUtils';
import { get, writable } from 'svelte/store';
import type { ProcessedScheduleEntry } from './calendarUtils';
import { selectedSchedule } from '$lib/stores/schedules';

function findEntry(ui_id: string): ProcessedScheduleEntry | undefined {
  return get(processedEntries).find(e => e.ui_id === ui_id);
}

export interface ApplyOptions { commit?: boolean; originalRecurrence?: string | null; }

// Store controlling recurring edit modal flow
export const recurringEditStore = writable<{
  open: boolean;
  ui_id: string | null;
  pending: Partial<ProcessedScheduleEntry> | null;
  newTime: string;
  eventTitle: string;
  original?: ProcessedScheduleEntry | null;
  originalOccurrenceStart?: string | null; // ISO of ORIGINAL instance start (RECURRENCE-ID target)
}>({ open: false, ui_id: null, pending: null, newTime: '', eventTitle: '', original: null, originalOccurrenceStart: null });

// Helper to produce a shallow clone of a processed entry and ensure Date objects are cloned
function cloneEntry(e: ProcessedScheduleEntry): ProcessedScheduleEntry {
  return {
    ...e,
    dtstart: e.dtstart instanceof Date ? new Date(e.dtstart.getTime()) : e.dtstart,
    dtend: e.dtend instanceof Date ? new Date(e.dtend.getTime()) : e.dtend
  };
}

function requestRecurringEdit(entry: ProcessedScheduleEntry, changes: Partial<ProcessedScheduleEntry>, originalSnapshot?: ProcessedScheduleEntry) {
  const start = changes.start_time ?? entry.start_time;
  const end = changes.end_time ?? entry.end_time;
  let changeDescription = '';
  if (changes.start_time || changes.end_time) changeDescription = `${start} - ${end}`; else if (changes.summary) changeDescription = `name to "${changes.summary}"`; else if (changes.field_id) changeDescription = `field`; else if (changes.team_id) changeDescription = `team`; else if (changes.categories) changeDescription = `category to ${changes.categories[0]}`; else changeDescription = 'properties';
  const originalCopy = originalSnapshot ? cloneEntry(originalSnapshot) : cloneEntry(entry);
  const originalOccurrenceStart = (entry.original_instance_start instanceof Date ? entry.original_instance_start : entry.dtstart instanceof Date ? entry.dtstart : new Date(entry.dtstart)).toISOString();
  console.debug('[recurringEditStore] open modal', { originalOccurrenceStart, ui_id: entry.ui_id });
  recurringEditStore.set({ open: true, ui_id: entry.ui_id, pending: changes, newTime: changeDescription, eventTitle: entry.summary || 'Recurring Event', original: originalCopy, originalOccurrenceStart });
}

export function cancelRecurringEdit(suppressRevert = false) {
  const state = get(recurringEditStore);
  if (!state.open) return;

  if (!suppressRevert && state.ui_id && state.original) {
    const restored = get(processedEntries).map(e => e.ui_id === state.ui_id ? { ...state.original! } : e);
    processedEntries.set(restored);
    const cd = get(currentDate);
    if (cd instanceof Date) currentDate.set(new Date(cd.getTime()));
    const ss = get(selectedSchedule);
    selectedSchedule.set(ss);
  }

  recurringEditStore.set({ open: false, ui_id: null, pending: null, newTime: '', eventTitle: '', original: null, originalOccurrenceStart: null });
}

export function confirmRecurringEdit(scope: 'this' | 'all') {
  const state = get(recurringEditStore);
  if (!state.ui_id || !state.pending) { cancelRecurringEdit(); return; }
  const entry = findEntry(state.ui_id); if (!entry) { cancelRecurringEdit(); return; }
  const storedOriginal = state.originalOccurrenceStart;
  const fallbackOriginal = entry.original_instance_start ? entry.original_instance_start.toISOString() : (entry.dtstart instanceof Date ? entry.dtstart.toISOString() : null);
  const originalOccurrenceStart = storedOriginal || fallbackOriginal;
  console.log('🔄 confirmRecurringEdit:', { scope, entry_ui_id: entry.ui_id, entry_uid: entry.uid, entry_isRecurring: entry.isRecurring, entry_recurrence_id: entry.recurrence_id, storedOriginal, fallbackOriginal, chosenOriginal: originalOccurrenceStart, pending_changes: state.pending });
  if (!originalOccurrenceStart) { console.warn('[confirmRecurringEdit] Missing originalOccurrenceStart; aborting single-instance edit.'); cancelRecurringEdit(true); return; }
  if (scope === 'this') {
    const sched = get(selectedSchedule);
    const master = sched?.schedule_entries.find((e: any) => e.uid === entry.uid && e.recurrence_rule && !e.recurrence_id);
    if (master) {
      const changes = { ...state.pending } as any;
      const startTime = changes.start_time ?? entry.start_time;
      const endTime = changes.end_time ?? entry.end_time;
      const originalStartDateObj = new Date(originalOccurrenceStart); // ORIGINAL occurrence start (old time)
      // New dtstart uses same date as original occurrence, but adjusted to new start time
      changes.dtstart = computeDateUTC(originalStartDateObj, startTime);
      changes.dtend = computeDateUTC(originalStartDateObj, endTime);
      changes.start_time = startTime; changes.end_time = endTime;
      const exception: ProcessedScheduleEntry = { ...entry, ...changes, schedule_entry_id: null, recurrence_id: new Date(originalOccurrenceStart), recurrence_rule: null, exdate: null, dtstart: changes.dtstart, dtend: changes.dtend, isRecurring: false, ui_id: `exception-${entry.uid}-${changes.dtstart.toISOString()}`, original_instance_start: entry.original_instance_start } as ProcessedScheduleEntry;
      console.debug('[confirmRecurringEdit] creating exception', { recurrence_id: originalOccurrenceStart, new_dtstart: changes.dtstart.toISOString(), new_dtend: changes.dtend.toISOString(), original_instance_start: entry.original_instance_start?.toISOString?.() });
      commitUpdate(exception, originalOccurrenceStart);
    }
  } else {
    const sched = get(selectedSchedule);
    const master = sched?.schedule_entries.find((e: any) => e.uid === entry.uid && e.recurrence_rule && !e.recurrence_id);
    if (master) {
      const masterDate = master.dtstart instanceof Date ? master.dtstart : new Date(master.dtstart);
      const changes = { ...state.pending } as any;
      if (changes.start_time || changes.end_time) {
        const startTime = changes.start_time ?? entry.start_time;
        const endTime = changes.end_time ?? entry.end_time;
        changes.dtstart = computeDateUTC(masterDate, startTime);
        changes.dtend = computeDateUTC(masterDate, endTime);
        changes.start_time = startTime; changes.end_time = endTime;
      }
      processedEntries.update(list => list.map(pe => (pe.uid === entry.uid && !pe.recurrence_id && !pe.isRecurring) ? { ...pe, ...changes } : pe));
      commitUpdate({ ...master, ...changes, uid: master.uid, schedule_id: master.schedule_id }, null);
    }
  }
  cancelRecurringEdit(true);
}

export function applyEntryChanges(ui_id: string, changes: Partial<ProcessedScheduleEntry>, opts: ApplyOptions = {}) {
  const { commit = true, originalRecurrence } = opts;
  let updated: ProcessedScheduleEntry | undefined;
  const entryBefore = findEntry(ui_id);
  
  console.log('⚡ applyEntryChanges called:', {
    ui_id,
    changes,
    commit,
    originalRecurrence,
    entryBefore_isRecurring: entryBefore?.isRecurring,
    entryBefore_recurrence_id: entryBefore?.recurrence_id,
    entryBefore_dtstart: entryBefore?.dtstart instanceof Date ? entryBefore?.dtstart.toISOString() : entryBefore?.dtstart
  });

  if (commit && entryBefore && entryBefore.isRecurring && !entryBefore.recurrence_id && originalRecurrence === undefined) {
    console.log('🚨 Intercepting recurring edit - showing modal (no mutation yet)');
    requestRecurringEdit(entryBefore, changes, entryBefore);
    return;
  }

  processedEntries.update(list => list.map(e => {
    if (e.ui_id !== ui_id) return e;
    updated = { ...e, ...changes } as ProcessedScheduleEntry;
    return updated!;
  }));
  if (!updated) return;
  if (commit) {
    const orig = originalRecurrence !== undefined ? originalRecurrence : getOriginalRecurrenceStart(updated);
    console.log('💾 Committing update:', { updated_uid: updated.uid, updated_schedule_id: updated.schedule_id, orig_recurrence: orig });
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
  const entry = findEntry(ui_id);
  const baseline = entry?.dtstart instanceof Date ? entry.dtstart : date;
  const dtstart = computeDateUTC(baseline, startTime);
  const dtend = computeDateUTC(baseline, endTime);
  applyEntryChanges(ui_id, { dtstart, dtend, start_time: startTime, end_time: endTime }, opts);
}

export function toggleRecurrence(ui_id: string, enable: boolean, rule: string | null, opts?: ApplyOptions) {
  applyEntryChanges(ui_id, { recurrence_rule: enable ? rule : null }, opts);
}
