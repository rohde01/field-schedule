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

export function horizontalDrag(node: HTMLElement, { ui_id, direction, totalColumns, activeFields, fieldToGridColMap }: any) {
  node.style.cursor = 'ew-resize';
  node.style.userSelect = 'none';
  const onMouseDown = (ev: MouseEvent) => {
    ev.preventDefault(); ev.stopPropagation();
    const entry = get(processedEntries).find(e => e.ui_id === ui_id);
    if (!entry) return;
    const gridEl = node.closest('.schedule-grid') as HTMLElement;
    const { left, width } = gridEl.getBoundingClientRect();
    const columnWidth = width / totalColumns;
    const mainField = getMainFieldForEvent(entry.field_id!, activeFields);
    if (!mainField) return;
    const candidates = getCandidateStatesForMainField(mainField, fieldToGridColMap);
    const original = candidates.find(c => c.field_id === entry.field_id);
    if (!original) return;
    const isRight = direction === 'right';
    const edgeIndex = isRight ? original.colIndex : original.colIndex + original.width - 1;
    const forEdge = candidates
      .filter(c => isRight ? c.colIndex === edgeIndex : (c.colIndex + c.width - 1) === edgeIndex)
      .sort((a, b) => isRight
        ? (a.colIndex + a.width) - (b.colIndex + b.width)
        : b.colIndex - a.colIndex
      );
    let lastUpdate: Partial<any> | null = null;
    const onMove = (e2: MouseEvent) => {
      const currentEntry = get(processedEntries).find(e => e.ui_id === ui_id);
      if (!currentEntry) return;
      const currentOriginal = candidates.find(c => c.field_id === currentEntry.field_id);
      if (!currentOriginal) return;
      const rel = Math.max(0, Math.min(e2.clientX - left, width));
      const target = Math.floor(rel / columnWidth) + 1;
      let chosen = currentOriginal;
      for (const c of forEdge) {
        const edge = isRight ? c.colIndex + c.width - 1 : c.colIndex;
        if (isRight ? target >= edge : target <= edge) chosen = c;
      }
      if (chosen.field_id !== currentEntry.field_id) {
        lastUpdate = { field_id: chosen.field_id };
        processedEntries.update(entries =>
          entries.map(ent =>
            ent.ui_id === ui_id ? { ...ent, ...lastUpdate! } : ent
          )
        );
      }
    };
    const onUp = () => {
      if (lastUpdate) processedEntries.update(entries =>
        entries.map(ent =>
          ent.ui_id === entry.ui_id ? { ...ent, ...lastUpdate! } : ent
        )
      );
      window.removeEventListener('mousemove', onMove);
      window.removeEventListener('mouseup', onUp);
    };
    window.addEventListener('mousemove', onMove);
    window.addEventListener('mouseup', onUp);
  };
  node.addEventListener('mousedown', onMouseDown);
  return {
    destroy() {
      node.removeEventListener('mousedown', onMouseDown);
    }
  };
}

