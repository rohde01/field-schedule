import { writable, get } from 'svelte/store';
import { deleteScheduleEntry, updateScheduleEntry } from '$lib/stores/schedules';
import { processedEntries } from './calendarUtils';
import type { ProcessedScheduleEntry } from './calendarUtils';
import { selectedSchedule } from '$lib/stores/schedules';

// Store controlling recurring delete modal flow
export const deleteRecurringEditStore = writable<{
  open: boolean;
  entry: ProcessedScheduleEntry | null;
  eventTitle: string;
}>({ open: false, entry: null, eventTitle: '' });

export function requestRecurringDelete(entry: ProcessedScheduleEntry) {
  deleteRecurringEditStore.set({
    open: true,
    entry,
    eventTitle: entry.summary || 'Recurring Event'
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
      // Create new recurrence rule with UNTIL parameter
      // Set UNTIL to one second before this occurrence to exclude it and all future
      const untilDate = new Date(recDate.getTime() - 1000); // 1 second before this occurrence
      const untilString = untilDate.toISOString().slice(0, 19).replace(/[-:]/g, '') + 'Z';
      
      let newRule = master.recurrence_rule;
      if (newRule) {
        // Remove existing UNTIL if present
        newRule = newRule.replace(/;UNTIL=\d{8}T?\d{0,6}Z?/, '');
        // Add new UNTIL with full datetime
        newRule += `;UNTIL=${untilString}`;
        
        // Update the master entry with new rule
        updateScheduleEntry({
          uid: master.uid,
          schedule_id: master.schedule_id!,
          recurrence_rule: newRule,
          recurrence_id: null
        });
      }
    }
  }

  cancelRecurringDelete();
}

export function handleRecurringDelete(entry: ProcessedScheduleEntry) {
  // Check if this is a recurring entry that needs special handling
  if (entry.isRecurring && !entry.recurrence_id) {
    // This is a generated occurrence of a recurring master
    requestRecurringDelete(entry);
  } else {
    // Handle as normal delete (standalone or exception)
    const recDateStr = entry.recurrence_id ? entry.dtstart.toISOString() : null;
    const recDate = recDateStr ? new Date(recDateStr) : null;
    deleteScheduleEntry(entry.uid, entry.schedule_id!, recDate);
  }
}