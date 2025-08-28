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
}>({ open: false, ui_id: null, pending: null, newTime: '', eventTitle: '', original: null });

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
  
  // Determine what changed for display
  let changeDescription = '';
  if (changes.start_time || changes.end_time) {
    changeDescription = `${start} - ${end}`;
  } else if (changes.summary) {
    changeDescription = `name to "${changes.summary}"`;
  } else if (changes.field_id) {
    changeDescription = `field`;
  } else if (changes.team_id) {
    changeDescription = `team`;
  } else if (changes.categories) {
    changeDescription = `category to ${changes.categories[0]}`;
  } else {
    changeDescription = 'properties';
  }

  // Use clone helper for original snapshot
  const originalCopy = originalSnapshot ? cloneEntry(originalSnapshot) : cloneEntry(entry);

  recurringEditStore.set({
    open: true,
    ui_id: entry.ui_id,
    pending: changes,
    newTime: changeDescription,
    eventTitle: entry.summary || 'Recurring Event',
    original: originalCopy
  });
}

export function cancelRecurringEdit(suppressRevert = false) {
  const state = get(recurringEditStore);
  if (!state.open) return;

  if (!suppressRevert && state.ui_id && state.original) {
    // Restore the original snapshot and set the store to a fresh array to force subscribers
    const restored = get(processedEntries).map(e => e.ui_id === state.ui_id ? { ...state.original! } : e);
    processedEntries.set(restored);

    // Trigger derived stores that depend on currentDate/selectedSchedule to recompute
    const cd = get(currentDate);
    if (cd instanceof Date) currentDate.set(new Date(cd.getTime()));
    const ss = get(selectedSchedule);
    selectedSchedule.set(ss);
  }

  // Clear the modal store
  recurringEditStore.set({ open: false, ui_id: null, pending: null, newTime: '', eventTitle: '', original: null });
}

export function confirmRecurringEdit(scope: 'this' | 'all') {
  const state = get(recurringEditStore);
  if (!state.ui_id || !state.pending) { cancelRecurringEdit(); return; }
  const entry = findEntry(state.ui_id);
  if (!entry) { cancelRecurringEdit(); return; }
  const originalOccurrenceStart = entry.dtstart.toISOString(); // Use the actual occurrence start time

  console.log('🔄 confirmRecurringEdit:', {
    scope,
    entry_ui_id: entry.ui_id,
    entry_uid: entry.uid,
    entry_isRecurring: entry.isRecurring,
    entry_recurrence_id: entry.recurrence_id,
    originalOccurrenceStart,
    pending_changes: state.pending
  });

  if (scope === 'this') {
    // create exception with the original occurrence time as recurrence_id
    const changes = { ...state.pending };
    // Ensure dtstart/dtend are properly set
    if (changes.start_time || changes.end_time) {
      const startTime = changes.start_time ?? entry.start_time;
      const endTime = changes.end_time ?? entry.end_time;
      changes.dtstart = computeDateUTC(entry.dtstart as Date, startTime);
      changes.dtend = computeDateUTC(entry.dtstart as Date, endTime);
      changes.start_time = startTime;
      changes.end_time = endTime;
    }
    console.log('📝 Creating exception with changes:', changes);
    console.log('📅 Using originalRecurrence:', originalOccurrenceStart);
    // Force the exception creation by using the original occurrence time as recurrence_id
    applyEntryChanges(state.ui_id, changes, { commit: true, originalRecurrence: originalOccurrenceStart });
  } else {
    // Update master entry (recurrence_id null). Need to find master in selectedSchedule.
    const sched = get(selectedSchedule);
    const master = sched?.schedule_entries.find(e => e.uid === entry.uid && e.recurrence_rule && !e.recurrence_id);
    if (master) {
      const masterDate = master.dtstart instanceof Date ? master.dtstart : new Date(master.dtstart);
      const changes = { ...state.pending } as any;
      // Re-map dtstart/dtend to master date if time changed.
      if (changes.start_time || changes.end_time) {
        const startTime = changes.start_time ?? entry.start_time;
        const endTime = changes.end_time ?? entry.end_time;
        changes.dtstart = computeDateUTC(masterDate, startTime);
        changes.dtend = computeDateUTC(masterDate, endTime);
        changes.start_time = startTime;
        changes.end_time = endTime;
      }
      // Apply directly to processedEntries master if visible; then commit with recurrence_id null.
      processedEntries.update(list => list.map(pe => {
        if (pe.uid === entry.uid && !pe.recurrence_id && !pe.isRecurring) return { ...pe, ...changes };
        return pe;
      }));
      commitUpdate({ ...master, ...changes, uid: master.uid, schedule_id: master.schedule_id }, null);
    }
  }
  // Close without reverting since we've committed
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
    entryBefore_recurrence_id: entryBefore?.recurrence_id
  });

  processedEntries.update(list => list.map(e => {
    if (e.ui_id !== ui_id) return e;
    updated = { ...e, ...changes } as ProcessedScheduleEntry;
    return updated!;
  }));
  if (!updated) return;
  if (commit) {
    // Only intercept if this is a recurring entry WITHOUT a recurrence_id (i.e., not already an exception)
    // AND we're not explicitly providing originalRecurrence (which means we're creating an exception)
    if (updated.isRecurring && !updated.recurrence_id && originalRecurrence === undefined) {
      console.log('🚨 Intercepting recurring edit - showing modal');
      // Intercept to ask user scope (editing a generated occurrence of a master rule)
      requestRecurringEdit(updated, changes, entryBefore);
      return; // defer commit
    }
    const orig = originalRecurrence !== undefined ? originalRecurrence : getOriginalRecurrenceStart(updated);
    console.log('💾 Committing update:', {
      updated_uid: updated.uid,
      updated_schedule_id: updated.schedule_id,
      orig_recurrence: orig
    });
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
