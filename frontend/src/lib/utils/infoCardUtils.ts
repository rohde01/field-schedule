import { writable, type Writable } from 'svelte/store';
import type { ScheduleEntry } from '$lib/schemas/schedule';
import type { Event } from '$lib/schemas/event';
import { updateScheduleEntry } from '$stores/schedules';
import { updateEventOverride } from '$stores/events';
import { normalizeTime } from './calendarUtils';


interface InfoCardPosition {
  top: number;
  left: number;
}

export function calculateInfoCardPosition(
  containerRect: DOMRect,
  targetRect: DOMRect,
  INFO_CARD_WIDTH = 400,
  INFO_CARD_HEIGHT = 220
): InfoCardPosition {
  const spaceOnRight = containerRect.right - targetRect.right;
  const eventCenterY = targetRect.top + (targetRect.height / 2);
  const top = eventCenterY - containerRect.top - (INFO_CARD_HEIGHT / 2);
  
  // Determine left position based on available space
  const left = spaceOnRight >= (INFO_CARD_WIDTH + 10)
    ? targetRect.right - containerRect.left + 10 
    : targetRect.left - containerRect.left - INFO_CARD_WIDTH - 10;

  return { top, left };
}

export function createInfoCardForm(entry: ScheduleEntry | Event): Writable<Record<string, any>> {
  if ('override_id' in entry) {
    // This is an Event from events store
    return writable({
      schedule_entry_id: entry.schedule_entry_id,
      override_id: entry.override_id,
      team_id: entry.team_id ?? null,
      field_id: entry.field_id ?? null,
      week_day: entry.week_day,
      start_time: normalizeTime(entry.start_time),
      end_time: normalizeTime(entry.end_time),
      override_date: entry.override_date,
      is_event: true // Flag to identify this as an Event type
    });
  } else {
    // This is a ScheduleEntry from schedules store
    return writable({
      schedule_entry_id: entry.schedule_entry_id,
      team_id: entry.team_id!,
      field_id: entry.field_id!,
      week_day: entry.week_day,
      start_time: normalizeTime(entry.start_time),
      end_time: normalizeTime(entry.end_time),
      is_event: false // Flag to identify this as a ScheduleEntry type
    });
  }
}

export function subscribeToFormChanges(form: Writable<Record<string, any>>): () => void {
  return form.subscribe(val => {
    if (val.is_event) {
      // Handle Event from events store
      if (val.override_id) {
        updateEventOverride(val.schedule_entry_id, val.override_id, {
          team_id: val.team_id,
          field_id: val.field_id,
          start_time: val.start_time,
          end_time: val.end_time
        });
      }
    } else {
      // Handle ScheduleEntry from schedules store
      updateScheduleEntry(val.schedule_entry_id, {
        team_id: val.team_id,
        field_id: val.field_id,
        week_day: val.week_day,
        start_time: val.start_time,
        end_time: val.end_time
      });
    }
  });
}

interface InfoCardState {
  editingEvent: ScheduleEntry | Event | null;
  infoCardForm: Writable<Record<string, any>> | null;
  editingEventPosition: { top: number; left: number };
}

function createInfoCardStore() {
  const { subscribe, set } = writable<InfoCardState>({
    editingEvent: null,
    infoCardForm: null,
    editingEventPosition: { top: 0, left: 0 }
  });

  let infoCardFormUnsubscribe: () => void = () => {};

  return {
    subscribe,
    openEventInfoCard: (e: MouseEvent, event: ScheduleEntry | Event, containerElement: HTMLElement) => {
      e.stopPropagation();
      const containerRect = containerElement.getBoundingClientRect();
      const targetRect = (e.currentTarget as HTMLElement).getBoundingClientRect();
      
      const editingEventPosition = calculateInfoCardPosition(containerRect, targetRect);
      const infoCardForm = createInfoCardForm(event);
      
      if (infoCardFormUnsubscribe) infoCardFormUnsubscribe();
      infoCardFormUnsubscribe = subscribeToFormChanges(infoCardForm);

      set({
        editingEvent: event,
        infoCardForm,
        editingEventPosition
      });
    },
    closeInfoCard: () => {
      if (infoCardFormUnsubscribe) infoCardFormUnsubscribe();
      set({
        editingEvent: null,
        infoCardForm: null,
        editingEventPosition: { top: 0, left: 0 }
      });
    }
  };
}

export const infoCardStore = createInfoCardStore();
