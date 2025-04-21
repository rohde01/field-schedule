// This file contains utility functions for drag-and-drop functionality.
import { processedEntries, timeSlots } from '$lib/utils/calendarUtils';
import { getCandidateStatesForMainField, getMainFieldForEvent } from './fieldUtils';
import type { Field } from '$lib/schemas/field';
import { get } from 'svelte/store';

export function resizeHandle(node: HTMLElement, { ui_id, edge }: { ui_id: string; edge: 'top'|'bottom' }) {
  // make handle visible as resizer and prevent text selection
  node.style.cursor = 'ns-resize';
  node.style.userSelect = 'none';
  let startY: number;
  let initialIndex: number;
  let slots: string[];
  let rowHeight: number;

  const onMouseMove = (e: MouseEvent) => {
    const deltaY = e.clientY - startY;
    const sensitivityFactor = 2.5;
    const deltaSlots = deltaY >= 0
      ? Math.floor(deltaY / (rowHeight * sensitivityFactor))
      : Math.ceil(deltaY / (rowHeight * sensitivityFactor));
    const newIndex = Math.min(
      Math.max(0, initialIndex + deltaSlots),
      slots.length - 1
    );
    const newTime = slots[newIndex];
    processedEntries.update(entries =>
      entries.map(entry =>
        entry.ui_id === ui_id
          ? {
              ...entry,
              [edge === 'top' ? 'start_time' : 'end_time']: newTime
            }
          : entry
      )
    );
  };

  const onMouseUp = () => {
    document.removeEventListener('mousemove', onMouseMove);
    document.removeEventListener('mouseup', onMouseUp);
  };

  const onMouseDown = (e: MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    startY = e.clientY;
    slots = get(timeSlots);
    const entry = get(processedEntries).find(e => e.ui_id === ui_id);
    const time = edge === 'top' ? entry?.start_time : entry?.end_time;
    initialIndex = time ? slots.indexOf(time) : 0;
    const wrapper = node.closest('.daily-schedule-wrapper') as HTMLElement;
    rowHeight = wrapper.clientHeight / slots.length;
    document.addEventListener('mousemove', onMouseMove);
    document.addEventListener('mouseup', onMouseUp);
  };

  node.addEventListener('mousedown', onMouseDown);
  return {
    destroy() {
      node.removeEventListener('mousedown', onMouseDown);
    }
  };
}

