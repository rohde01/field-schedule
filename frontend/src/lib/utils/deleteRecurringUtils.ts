import { writable, get } from 'svelte/store';
import { deleteScheduleEntry, updateScheduleEntry, pruneFutureExceptions } from '$lib/stores/schedules';
import { processedEntries, isRecurringMaster } from './calendarUtils';
import type { ProcessedScheduleEntry } from './calendarUtils';
import { selectedSchedule } from '$lib/stores/schedules';

// Store controlling recurring delete modal flow
export const deleteRecurringEditStore = writable<{
  open: boolean;
  entry: ProcessedScheduleEntry | null;
  eventTitle: string;
  isMasterEntry: boolean;
}>({ open: false, entry: null, eventTitle: '', isMasterEntry: false });

export function requestRecurringDelete(entry: ProcessedScheduleEntry, isMaster: boolean = false) {
  deleteRecurringEditStore.set({
    open: true,
    entry,
    eventTitle: entry.summary || 'Recurring Event',
    isMasterEntry: isMaster
  });
}

export function cancelRecurringDelete() {
  deleteRecurringEditStore.update(s => ({ ...s, open: false, entry: null }));
}

export function confirmRecurringDelete(scope: 'this' | 'future') {
  const state = get(deleteRecurringEditStore);
  if (!state.entry) { 
    cancelRecurringDelete(); 
    return; 
  }

  const entry = state.entry;
  const originalOccurrenceStart = entry.dtstart.toISOString();
  const recDate = new Date(originalOccurrenceStart);

  if (state.isMasterEntry) {
    // For master entry, always delete all (ignore scope parameter)
    deleteScheduleEntry(entry.uid, entry.schedule_id!, null);
  } else {
    // For recurring instance
    if (scope === 'this') {
      // Delete only this occurrence by adding exdate
      deleteScheduleEntry(entry.uid, entry.schedule_id!, recDate);
    } else {
      // Delete this and all future occurrences by updating master rule with UNTIL
      const sched = get(selectedSchedule);
      const master = sched?.schedule_entries.find(e => 
        e.uid === entry.uid && e.recurrence_rule && !e.recurrence_id
      );
      
      if (master) {
        const untilDate = new Date(recDate.getTime() - 1000);
        const untilString = untilDate.toISOString().slice(0, 19).replace(/[-:]/g, '') + 'Z';
        let newRule = master.recurrence_rule;
        if (newRule) {
          newRule = newRule.replace(/;UNTIL=\d{8}T?\d{0,6}Z?/, '');
          newRule += `;UNTIL=${untilString}`;
          updateScheduleEntry({ uid: master.uid, schedule_id: master.schedule_id!, recurrence_rule: newRule, recurrence_id: null });
          pruneFutureExceptions(master.schedule_id!, master.uid, recDate);
        }
      }
    }
  }

  cancelRecurringDelete();
}

export function handleRecurringDelete(entry: ProcessedScheduleEntry) {
  // Check if this is a master entry (has recurrence rule but no recurrence_id)
  const isMaster = !!(!entry.isRecurring && entry.recurrence_rule && !entry.recurrence_id);
  
  // Check if this is a recurring entry that needs special handling
  if ((entry.isRecurring && !entry.recurrence_id) || isMaster) {
    // This is either a generated occurrence of a recurring master or the master itself
    requestRecurringDelete(entry, isMaster);
  } else {
    // Handle as normal delete (standalone or exception)
    const recDateStr = entry.recurrence_id ? entry.dtstart.toISOString() : null;
    const recDate = recDateStr ? new Date(recDateStr) : null;
    deleteScheduleEntry(entry.uid, entry.schedule_id!, recDate);
  }
}