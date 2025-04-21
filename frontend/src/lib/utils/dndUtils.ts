import { processedEntries, timeSlots } from '$lib/utils/calendarUtils';
import { getCandidateStatesForMainField, getMainFieldForEvent } from './fieldUtils';
import type { Field } from '$lib/schemas/field';
import { get } from 'svelte/store';

export function resizeHandle(node: HTMLElement, { ui_id, edge }: { ui_id: string; edge: 'top'|'bottom' }) {
  // make handle visible as resizer and prevent text selection
  node.style.cursor = 'ns-resize';
  node.style.userSelect = 'none';
  let moved = false;
  let startY: number;
  let initialIndex: number;
  let slots: string[];
  let rowHeight: number;

  const onMouseMove = (e: MouseEvent) => {
    moved = true;
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
    node.dispatchEvent(new CustomEvent('dragend', { detail: moved, bubbles: true }));
    document.removeEventListener('mousemove', onMouseMove);
    document.removeEventListener('mouseup', onMouseUp);
  };

  const onMouseDown = (e: MouseEvent) => {
    moved = false;
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
  let moved = false;
  const onMouseDown = (ev: MouseEvent) => {
    moved = false;
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
      moved = true;
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
      node.dispatchEvent(new CustomEvent('dragend', { detail: moved, bubbles: true }));
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

export function moveHandle(node: HTMLElement, { ui_id, totalColumns, activeFields, fieldToGridColMap }: any) {
  node.style.cursor = 'move';
  node.style.userSelect = 'none';

  let startY: number;
  let initialStartIndex: number;
  let initialEndIndex: number;
  let slots: string[];
  let rowHeight: number;
  let candidates: any[];
  let originalType: string;
  let mainField: any;
  let moved = false;

  const onMouseMove = (e: MouseEvent) => {
    moved = true;
    const deltaY = e.clientY - startY;
    const sensitivityFactor = 2.5;
    const deltaSlots = deltaY >= 0
      ? Math.floor(deltaY / (rowHeight * sensitivityFactor))
      : Math.ceil(deltaY / (rowHeight * sensitivityFactor));

    let newStartIndex = Math.min(
      Math.max(0, initialStartIndex + deltaSlots),
      slots.length - 1
    );
    let newEndIndex = Math.min(
      Math.max(0, initialEndIndex + deltaSlots),
      slots.length - 1
    );
    if (newEndIndex <= newStartIndex) {
      newEndIndex = newStartIndex + (initialEndIndex - initialStartIndex);
      if (newEndIndex >= slots.length) newEndIndex = slots.length - 1;
    }

    const gridEl = node.closest('.schedule-grid') as HTMLElement;
    const { left, width } = gridEl.getBoundingClientRect();
    const relX = Math.max(0, Math.min(e.clientX - left, width));
    const columnWidth = width / totalColumns;
    const targetCol = Math.min(Math.max(1, Math.round(relX / columnWidth) + 1), totalColumns);

    const destField = activeFields.find((f: Field) => {
      const m = fieldToGridColMap.get(f.field_id);
      return m && targetCol >= m.colIndex && targetCol < m.colIndex + m.colSpan;
    });
    const baseCandidates = getCandidateStatesForMainField(destField || mainField, fieldToGridColMap);
    const filtered = baseCandidates.filter(c => c.candidateType === originalType);
    const candidatesToUse = filtered.length ? filtered : baseCandidates;
    const chosen = candidatesToUse.reduce((prev, curr) =>
      Math.abs(curr.colIndex - targetCol) < Math.abs(prev.colIndex - targetCol) ? curr : prev
    );

    processedEntries.update(entries =>
      entries.map(ent =>
        ent.ui_id === ui_id
          ? { ...ent, start_time: slots[newStartIndex], end_time: slots[newEndIndex], field_id: chosen.field_id }
          : ent
      )
    );
  };

  const onMouseUp = () => {
    document.removeEventListener('mousemove', onMouseMove);
    document.removeEventListener('mouseup', onMouseUp);
    node.dispatchEvent(new CustomEvent('dragend', { detail: moved }));
  };

  const onMouseDown = (e: MouseEvent) => {
    moved = false;
    const target = e.target as HTMLElement;
    if (target.closest('.info-card-container') || target.closest('input') || target.closest('select') || target.closest('button')) {
      return;
    }

    e.preventDefault();
    e.stopPropagation();
    startY = e.clientY;
    slots = get(timeSlots);
    const entry = get(processedEntries).find(e2 => e2.ui_id === ui_id);
    if (!entry) return;
    initialStartIndex = slots.indexOf(entry.start_time);
    initialEndIndex = slots.indexOf(entry.end_time);
    const wrapper = node.closest('.daily-schedule-wrapper') as HTMLElement;
    rowHeight = wrapper.clientHeight / slots.length;

    mainField = getMainFieldForEvent(entry.field_id!, activeFields)!;
    candidates = getCandidateStatesForMainField(mainField, fieldToGridColMap);
    const original = candidates.find(c => c.field_id === entry.field_id);
    originalType = original?.candidateType || 'main';

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

