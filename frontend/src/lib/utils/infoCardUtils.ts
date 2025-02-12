import { writable, type Writable } from 'svelte/store';
import type { ScheduleEntry } from '$lib/schemas/schedule';
import { updateScheduleEntry } from '$stores/schedules';
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

export function createInfoCardForm(event: ScheduleEntry): Writable<Record<string, any>> {
  return writable({
    schedule_entry_id: event.schedule_entry_id,
    team_id: event.team_id!,
    field_id: event.field_id!,
    week_day: event.week_day,
    start_time: normalizeTime(event.start_time),
    end_time: normalizeTime(event.end_time)
  });
}

export function subscribeToFormChanges(form: Writable<Record<string, any>>): () => void {
  return form.subscribe(val => {
    updateScheduleEntry(val.schedule_entry_id, {
      team_id: val.team_id,
      field_id: val.field_id,
      week_day: val.week_day,
      start_time: val.start_time,
      end_time: val.end_time
    });
  });
}

interface InfoCardState {
  editingEvent: ScheduleEntry | null;
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
    openEventInfoCard: (e: MouseEvent, event: ScheduleEntry, containerElement: HTMLElement) => {
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
