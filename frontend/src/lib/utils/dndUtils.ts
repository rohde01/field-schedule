import type { Field } from '$lib/schemas/field';
import type { ScheduleEntry } from '$lib/schemas/schedule';
import { getCandidateStatesForMainField, getMainFieldForEvent } from './fieldUtils';

export function handleTopDragMove(
  deltaY: number,
  rowHeight: number,
  initialStartIndex: number,
  initialEndIndex: number,
  timeSlotsArr: string[]
): { newStartIndex: number, newStartTime: string } | null {
  const deltaRows = Math.round(deltaY / rowHeight);
  let newStartIndex = initialStartIndex + deltaRows;
  newStartIndex = Math.max(0, Math.min(newStartIndex, initialEndIndex - 1));
  const newStartTime = timeSlotsArr[newStartIndex];
  return { newStartIndex, newStartTime };
}

export function handleBottomDragMove(
  deltaY: number,
  rowHeight: number,
  initialStartIndex: number,
  initialEndIndex: number,
  timeSlotsArr: string[]
): { newEndIndex: number, newEndTime: string } | null {
  const deltaRows = Math.round(deltaY / rowHeight);
  let newEndIndex = initialEndIndex + deltaRows;
  newEndIndex = Math.max(initialStartIndex + 1, Math.min(newEndIndex, timeSlotsArr.length - 1));
  const newEndTime = timeSlotsArr[newEndIndex];
  return { newEndIndex, newEndTime };
}

export function calculateNewFieldId(
  relativeX: number,
  gridWidth: number,
  totalColumns: number,
  headerCells: { colIndex: number; fieldId: number }[],
  scheduleEntry: ScheduleEntry,
  activeFields: Field[],
  fieldToGridColMap: Map<number, { colIndex: number; colSpan: number }>
): number {
  const columnWidth = gridWidth / totalColumns;
  relativeX = Math.max(0, Math.min(relativeX, gridWidth));
  const targetCol = Math.floor(relativeX / columnWidth) + 1;

  // Find closest header cell
  let chosenHeader = headerCells[0];
  let minHeaderDiff = Math.abs(chosenHeader.colIndex - targetCol);
  for (const cell of headerCells) {
    const diff = Math.abs(cell.colIndex - targetCol);
    if (diff < minHeaderDiff) {
      chosenHeader = cell;
      minHeaderDiff = diff;
    }
  }

  // Get main field and calculate candidates
  const newMainField = getMainFieldForEvent(chosenHeader.fieldId, activeFields);
  if (!newMainField) return scheduleEntry.field_id!;

  const candidates = getCandidateStatesForMainField(newMainField, fieldToGridColMap);

  // Get original candidate width
  const originalMainField = getMainFieldForEvent(scheduleEntry.field_id!, activeFields);
  let desiredWidth = 1;
  if (originalMainField) {
    const originalCandidates = getCandidateStatesForMainField(originalMainField, fieldToGridColMap);
    const originalCandidate = originalCandidates.find(c => c.field_id === scheduleEntry.field_id);
    if (originalCandidate) {
      desiredWidth = originalCandidate.width;
    }
  }

  // Filter and sort candidates
  let validCandidates = candidates.filter(c => c.width === desiredWidth);
  if (validCandidates.length === 0) {
    validCandidates = candidates;
  }

  // Find closest candidate
  let chosenCandidate = validCandidates[0];
  let minDiff = Math.abs(chosenCandidate.colIndex - targetCol);
  for (const cand of validCandidates) {
    const diff = Math.abs(cand.colIndex - targetCol);
    if (diff < minDiff) {
      chosenCandidate = cand;
      minDiff = diff;
    }
  }

  return chosenCandidate.field_id;
}

interface DragCallbacks {
  onUpdate: (updates: Partial<ScheduleEntry>, isLocal?: boolean) => void;
}

export function initializeTopDrag(
  e: MouseEvent,
  scheduleEntry: ScheduleEntry,
  gridElement: HTMLElement,
  timeSlots: string[],
  callbacks: DragCallbacks
) {
  e.stopPropagation();
  e.preventDefault();
  
  const timeCell = gridElement.querySelector('.schedule-time') as HTMLElement;
  if (!timeCell) return;
  
  const rowHeight = timeCell.clientHeight;
  const initialClientY = e.clientY;
  const initialStartIndex = timeSlots.indexOf(normalizeTime(scheduleEntry.start_time));
  const initialEndIndex = timeSlots.indexOf(normalizeTime(scheduleEntry.end_time));
  let lastUpdate: Partial<ScheduleEntry> | null = null;

  function onMouseMove(moveEvent: MouseEvent) {
    const deltaY = moveEvent.clientY - initialClientY;
    const result = handleTopDragMove(deltaY, rowHeight, initialStartIndex, initialEndIndex, timeSlots);
    if (result && result.newStartTime !== scheduleEntry.start_time) {
      lastUpdate = { start_time: result.newStartTime };
      callbacks.onUpdate(lastUpdate, true);
    }
  }

  function onMouseUp() {
    if (lastUpdate) {
      callbacks.onUpdate(lastUpdate, false);
    }
    window.removeEventListener('mousemove', onMouseMove);
    window.removeEventListener('mouseup', onMouseUp);
  }

  window.addEventListener('mousemove', onMouseMove);
  window.addEventListener('mouseup', onMouseUp);
}

export function initializeBottomDrag(
  e: MouseEvent,
  scheduleEntry: ScheduleEntry,
  gridElement: HTMLElement,
  timeSlots: string[],
  callbacks: DragCallbacks
) {
  e.stopPropagation();
  e.preventDefault();
  
  const timeCell = gridElement.querySelector('.schedule-time') as HTMLElement;
  if (!timeCell) return;
  
  const rowHeight = timeCell.clientHeight;
  const initialClientY = e.clientY;
  const initialStartIndex = timeSlots.indexOf(normalizeTime(scheduleEntry.start_time));
  const initialEndIndex = timeSlots.indexOf(normalizeTime(scheduleEntry.end_time));
  let lastUpdate: Partial<ScheduleEntry> | null = null;

  function onMouseMove(moveEvent: MouseEvent) {
    const deltaY = moveEvent.clientY - initialClientY;
    const result = handleBottomDragMove(deltaY, rowHeight, initialStartIndex, initialEndIndex, timeSlots);
    if (result && result.newEndTime !== scheduleEntry.end_time) {
      lastUpdate = { end_time: result.newEndTime };
      callbacks.onUpdate(lastUpdate, true);
    }
  }

  function onMouseUp() {
    if (lastUpdate) {
      callbacks.onUpdate(lastUpdate, false);
    }
    window.removeEventListener('mousemove', onMouseMove);
    window.removeEventListener('mouseup', onMouseUp);
  }

  window.addEventListener('mousemove', onMouseMove);
  window.addEventListener('mouseup', onMouseUp);
}

export function initializeEventDrag(
  e: MouseEvent,
  scheduleEntry: ScheduleEntry,
  gridElement: HTMLElement,
  timeSlots: string[],
  totalColumns: number,
  headerCells: { colIndex: number; fieldId: number }[],
  activeFields: Field[],
  fieldToGridColMap: Map<number, { colIndex: number; colSpan: number }>,
  callbacks: DragCallbacks
) {
  e.stopPropagation();
  e.preventDefault();
  
  const timeCell = gridElement.querySelector('.schedule-time') as HTMLElement;
  if (!timeCell) return;
  
  const rowHeight = timeCell.clientHeight;
  const initialClientY = e.clientY;
  const initialStartIndex = timeSlots.indexOf(normalizeTime(scheduleEntry.start_time));
  const initialEndIndex = timeSlots.indexOf(normalizeTime(scheduleEntry.end_time));
  const duration = initialEndIndex - initialStartIndex;

  const gridRect = gridElement.getBoundingClientRect();
  let lastUpdate: Partial<ScheduleEntry> | null = null;

  function clamp(val: number, min: number, max: number) {
    return Math.max(min, Math.min(val, max));
  }

  function onMouseMove(moveEvent: MouseEvent) {
    const deltaY = moveEvent.clientY - initialClientY;
    const deltaRows = Math.round(deltaY / rowHeight);
    const maxStartIndex = timeSlots.length - 1 - duration;
    const newStartIndex = clamp(initialStartIndex + deltaRows, 0, maxStartIndex);
    const newEndIndex = newStartIndex + duration;
    const newStartTime = timeSlots[newStartIndex];
    const newEndTime = timeSlots[newEndIndex];

    let relativeX = moveEvent.clientX - gridRect.left;
    relativeX = clamp(relativeX, 0, gridRect.width);
    
    const newFieldId = calculateNewFieldId(
      relativeX,
      gridRect.width,
      totalColumns,
      headerCells,
      scheduleEntry,
      activeFields,
      fieldToGridColMap
    );

    lastUpdate = { 
      start_time: newStartTime, 
      end_time: newEndTime, 
      field_id: newFieldId 
    };
    callbacks.onUpdate(lastUpdate, true);
  }

  function onMouseUp() {
    if (lastUpdate) {
      callbacks.onUpdate(lastUpdate, false);
    }
    window.removeEventListener('mousemove', onMouseMove);
    window.removeEventListener('mouseup', onMouseUp);
  }

  window.addEventListener('mousemove', onMouseMove);
  window.addEventListener('mouseup', onMouseUp);
}

export function initializeHorizontalDrag(
  e: MouseEvent,
  scheduleEntry: ScheduleEntry,
  direction: 'left' | 'right',
  gridElement: HTMLElement,
  totalColumns: number,
  activeFields: Field[],
  fieldToGridColMap: Map<number, { colIndex: number; colSpan: number }>,
  callbacks: DragCallbacks
) {
  e.stopPropagation();
  e.preventDefault();

  const gridRect = gridElement.getBoundingClientRect();
  const columnWidth = gridRect.width / totalColumns;
  
  const mainField = getMainFieldForEvent(scheduleEntry.field_id!, activeFields);
  if (!mainField) return;
  
  const candidates = getCandidateStatesForMainField(mainField, fieldToGridColMap);
  const originalCandidate = candidates.find(c => c.field_id === scheduleEntry.field_id);
  if (!originalCandidate) return;

  let lastUpdate: Partial<ScheduleEntry> | null = null;

  if (direction === 'right') {
    const originalLeft = originalCandidate.colIndex;
    
    function onMouseMove(moveEvent: MouseEvent) {
      let relativeX = moveEvent.clientX - gridRect.left;
      relativeX = Math.max(0, Math.min(relativeX, gridRect.width));
      const targetRight = Math.floor(relativeX / columnWidth) + 1;
      
      const candidatesForSameLeft = candidates.filter(c => c.colIndex === originalLeft)
        .sort((a, b) => (a.colIndex + a.width) - (b.colIndex + b.width));
      
      if (candidatesForSameLeft.length === 0) return;
      
      let chosenCandidate = originalCandidate;
      for (const cand of candidatesForSameLeft) {
        const candRight = cand.colIndex + cand.width - 1;
        if (targetRight >= candRight) {
          chosenCandidate = cand;
        }
      }
      
      if (chosenCandidate && chosenCandidate.field_id !== scheduleEntry.field_id) {
        lastUpdate = { field_id: chosenCandidate.field_id };
        callbacks.onUpdate(lastUpdate, true);
      }
    }

    const cleanup = () => {
      if (lastUpdate) {
        callbacks.onUpdate(lastUpdate, false);
      }
      window.removeEventListener('mousemove', onMouseMove);
      window.removeEventListener('mouseup', cleanup);
    };

    window.addEventListener('mousemove', onMouseMove);
    window.addEventListener('mouseup', cleanup);
  } else {
    const originalRight = originalCandidate.colIndex + originalCandidate.width - 1;
    
    function onMouseMove(moveEvent: MouseEvent) {
      let relativeX = moveEvent.clientX - gridRect.left;
      relativeX = Math.max(0, Math.min(relativeX, gridRect.width));
      const targetLeft = Math.floor(relativeX / columnWidth) + 1;
      
      const candidatesForSameRight = candidates.filter(c => (c.colIndex + c.width - 1) === originalRight)
        .sort((a, b) => b.colIndex - a.colIndex);
      
      if (candidatesForSameRight.length === 0) return;
      
      let chosenCandidate = originalCandidate;
      for (const cand of candidatesForSameRight) {
        if (targetLeft <= cand.colIndex) {
          chosenCandidate = cand;
        }
      }
      
      if (chosenCandidate && chosenCandidate.field_id !== scheduleEntry.field_id) {
        lastUpdate = { field_id: chosenCandidate.field_id };
        callbacks.onUpdate(lastUpdate, true);
      }
    }

    const cleanup = () => {
      if (lastUpdate) {
        callbacks.onUpdate(lastUpdate, false);
      }
      window.removeEventListener('mousemove', onMouseMove);
      window.removeEventListener('mouseup', cleanup);
    };

    window.addEventListener('mousemove', onMouseMove);
    window.addEventListener('mouseup', cleanup);
  }
}

function normalizeTime(time: string): string {
  return time.split(':').slice(0, 2).join(':');
}