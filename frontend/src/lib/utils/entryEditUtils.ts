// filepath: src/lib/utils/entryEditUtils.ts
import { processedEntries, getOriginalRecurrenceStart, commitUpdate } from './calendarUtils';
import { computeDateUTC, currentDate } from './dateUtils';
import { get, writable } from 'svelte/store';
import type { ProcessedScheduleEntry } from './calendarUtils';
import { selectedSchedule } from '$lib/stores/schedules';

function findEntry(ui_id: string): ProcessedScheduleEntry | undefined { return get(processedEntries).find(e => e.ui_id === ui_id); }
export interface ApplyOptions { commit?: boolean; originalRecurrence?: string | null; }

export const recurringEditStore = writable<{ open: boolean; ui_id: string | null; pending: Partial<ProcessedScheduleEntry> | null; changeDesc: string; title: string; snapshot?: ProcessedScheduleEntry | null; originalOccurrence?: string | null; }>({ open: false, ui_id: null, pending: null, changeDesc: '', title: '', snapshot: null, originalOccurrence: null });

function cloneEntry(e: ProcessedScheduleEntry): ProcessedScheduleEntry { return { ...e, dtstart: new Date(e.dtstart), dtend: new Date(e.dtend) }; }

function describeChange(entry: ProcessedScheduleEntry, changes: Partial<ProcessedScheduleEntry>): string {
  if (changes.start_time || changes.end_time) return `${changes.start_time ?? entry.start_time} - ${changes.end_time ?? entry.end_time}`;
  if (changes.summary) return `title → "${changes.summary}"`;
  if (changes.field_id) return 'field change';
  if (changes.team_id) return 'team change';
  if (changes.categories) return `category → ${changes.categories[0]}`;
  return 'update';
}

function requestRecurringEdit(entry: ProcessedScheduleEntry, changes: Partial<ProcessedScheduleEntry>) {
  // Use occurrence_origin (original generated instance start) if present; fallback to current dtstart
  const origin = entry.occurrence_origin instanceof Date ? entry.occurrence_origin : (entry.dtstart as Date);
  const originalOccurrence = origin.toISOString();
  const changeDesc = describeChange(entry, changes);
  console.debug('[recurringEdit] open modal', {
    ui_id: entry.ui_id,
    uid: entry.uid,
    originalOccurrence,
    occurrence_origin: entry.occurrence_origin?.toISOString?.(),
    current_dtstart: entry.dtstart instanceof Date ? entry.dtstart.toISOString() : entry.dtstart,
    pending: changes
  });
  recurringEditStore.set({
    open: true,
    ui_id: entry.ui_id,
    pending: changes,
    changeDesc,
    title: entry.summary || 'Recurring Event',
    snapshot: cloneEntry(entry),
    originalOccurrence
  });
}

export function cancelRecurringEdit(suppressRevert = false) {
  const st = get(recurringEditStore); if (!st.open) return;
  if (!suppressRevert && st.ui_id && st.snapshot) {
    processedEntries.update(list => list.map(e => e.ui_id === st.ui_id ? { ...st.snapshot! } : e));
    const d = get(currentDate); if (d instanceof Date) currentDate.set(new Date(d.getTime()));
    selectedSchedule.set(get(selectedSchedule));
  }
  recurringEditStore.set({ open: false, ui_id: null, pending: null, changeDesc: '', title: '', snapshot: null, originalOccurrence: null });
}

export function confirmRecurringEdit(scope: 'this' | 'all') {
  const st = get(recurringEditStore); if (!st.ui_id || !st.pending) { cancelRecurringEdit(); return; }
  const entry = findEntry(st.ui_id); if (!entry) { cancelRecurringEdit(); return; }
  const originalOccurrence = st.originalOccurrence; // ISO or null
  console.debug('[recurringEdit] confirm', { scope, ui_id: st.ui_id, uid: entry.uid, storedOriginal: originalOccurrence, entry_dtstart: entry.dtstart.toISOString(), occurrence_origin: entry.occurrence_origin?.toISOString?.(), pending: st.pending });

  if (scope === 'this') {
    if (!originalOccurrence) { console.warn('[recurringEdit] missing originalOccurrence for single edit'); cancelRecurringEdit(true); return; }
    const sched = get(selectedSchedule);
    const master = sched?.schedule_entries.find((e: any) => e.uid === entry.uid && e.recurrence_rule && !e.recurrence_id);
    if (master) {
      const baseDate = new Date(originalOccurrence); // ORIGINAL generated occurrence start (old time)
      const changes = { ...st.pending } as any;
      const startT = changes.start_time ?? entry.start_time; const endT = changes.end_time ?? entry.end_time;
      const newDtStart = computeDateUTC(baseDate, startT);
      const newDtEnd = computeDateUTC(baseDate, endT);
      changes.dtstart = newDtStart; changes.dtend = newDtEnd; changes.start_time = startT; changes.end_time = endT;
      const exception: ProcessedScheduleEntry = {
        ...entry,
        ...changes,
        schedule_entry_id: null,
        recurrence_id: new Date(originalOccurrence), // IMPORTANT: original occurrence start, not new time
        recurrence_rule: null,
        exdate: null,
        dtstart: newDtStart,
        dtend: newDtEnd,
        isRecurring: false,
        ui_id: `X|${entry.uid}|${newDtStart.toISOString()}|0`
      } as ProcessedScheduleEntry;
      console.debug('[recurringEdit] create exception', {
        uid: entry.uid,
        recurrence_id: originalOccurrence,
        new_dtstart: newDtStart.toISOString(),
        new_dtend: newDtEnd.toISOString(),
        willExcludeTs: new Date(originalOccurrence).getTime()
      });
      commitUpdate(exception, originalOccurrence);
    }
  } else {
    const sched = get(selectedSchedule);
    const master = sched?.schedule_entries.find((e: any) => e.uid === entry.uid && e.recurrence_rule && !e.recurrence_id);
    if (master) {
      const masterBase = master.dtstart instanceof Date ? master.dtstart : new Date(master.dtstart);
      const changes = { ...st.pending } as any;
      if (changes.start_time || changes.end_time) {
        const startT = changes.start_time ?? entry.start_time; const endT = changes.end_time ?? entry.end_time;
        changes.dtstart = computeDateUTC(masterBase, startT); changes.dtend = computeDateUTC(masterBase, endT);
        changes.start_time = startT; changes.end_time = endT;
      }
      console.debug('[recurringEdit] update master', { uid: entry.uid, changes });
      commitUpdate({ ...master, ...changes }, null);
    }
  }
  cancelRecurringEdit(true);
}

export function applyEntryChanges(ui_id: string, changes: Partial<ProcessedScheduleEntry>, opts: ApplyOptions = {}) {
  const { commit = true, originalRecurrence } = opts; let updated: ProcessedScheduleEntry | undefined; const before = findEntry(ui_id);
  if (commit && before && before.isRecurring && !before.recurrence_id && originalRecurrence === undefined) { requestRecurringEdit(before, changes); return; }
  processedEntries.update(list => list.map(e => e.ui_id === ui_id ? (updated = { ...e, ...changes } as ProcessedScheduleEntry) : e));
  if (!updated || !commit) return; const orig = originalRecurrence !== undefined ? originalRecurrence : getOriginalRecurrenceStart(updated); commitUpdate(updated, orig);
}

export const updateEntryField = <T extends keyof ProcessedScheduleEntry>(ui_id: string, field: T, value: ProcessedScheduleEntry[T], opts?: ApplyOptions) => applyEntryChanges(ui_id, { [field]: value } as any, opts);
export function updateEntryDate(ui_id: string, newDate: Date, opts?: ApplyOptions) { const e = findEntry(ui_id); if (!e) return; applyEntryChanges(ui_id, { dtstart: computeDateUTC(newDate,e.start_time), dtend: computeDateUTC(newDate,e.end_time) }, opts); }
export function updateEntryTimeRange(ui_id: string, startTime: string, endTime: string, opts?: ApplyOptions) { const e = findEntry(ui_id); if (!e) return; const ds = computeDateUTC(e.dtstart as Date, startTime); const de = computeDateUTC(e.dtstart as Date, endTime); applyEntryChanges(ui_id, { start_time: startTime, end_time: endTime, dtstart: ds, dtend: de }, opts); }
export function updateEntryDateAndTime(ui_id: string, date: Date, startTime: string, endTime: string, opts?: ApplyOptions) { const ds = computeDateUTC(date,startTime); const de = computeDateUTC(date,endTime); applyEntryChanges(ui_id, { dtstart: ds, dtend: de, start_time: startTime, end_time: endTime }, opts); }
export function toggleRecurrence(ui_id: string, enable: boolean, rule: string | null, opts?: ApplyOptions) { applyEntryChanges(ui_id, { recurrence_rule: enable ? rule : null }, opts); }
