import type { Field } from '$lib/schemas/field';
import type { ScheduleEntry } from '$lib/schemas/schedule';


// Function to check if a field is a subfield of another (either half or quarter)
export function isSubfieldOf(potentialParentId: number, subfieldId: number, fields: Field[]): boolean {
    const parentField = fields.find(f => f.field_id === potentialParentId);
    if (!parentField) return false;
    
    // Check half subfields
    if (parentField.half_subfields.some(half => half.field_id === subfieldId)) {
      return true;
    }
    
    // Check quarter subfields
    if (parentField.quarter_subfields.some(quarter => quarter.field_id === subfieldId)) {
      return true;
    }
    
    return false;
  }
  
  // Function to check if fields are related (either same field or one is subfield of another)
  export function areFieldsRelated(field1Id: number, field2Id: number, fields: Field[]): boolean {
    if (field1Id === field2Id) return true;
    return isSubfieldOf(field1Id, field2Id, fields) || isSubfieldOf(field2Id, field1Id, fields);
  }
  
  // Function to check if two time ranges overlap
  export function doTimesOverlap(start1: string, end1: string, start2: string, end2: string): boolean {
    return start1 < end2 && start2 < end1;
  }
  
  // Function to check if two events overlap (considering time and field hierarchy)
  export function eventsOverlap(event1: ScheduleEntry, event2: ScheduleEntry, fields: Field[]): boolean {
    if (event1.week_day !== event2.week_day) return false;
    
    if (!doTimesOverlap(event1.start_time, event1.end_time, event2.start_time, event2.end_time)) {
      return false;
    }
    return areFieldsRelated(event1.field_id!, event2.field_id!, fields);
  }
  
  // Function to detect all overlapping events for a given day
  export function detectOverlappingEvents(events: ScheduleEntry[], weekDay: number, fields: Field[]): Map<number, number[]> {
    const dayEvents = events.filter(event => event.week_day === weekDay);
    const overlapMap = new Map<number, number[]>();
    
    dayEvents.forEach(event => {
      overlapMap.set(event.schedule_entry_id, []);
    });
    
    for (let i = 0; i < dayEvents.length; i++) {
      for (let j = i + 1; j < dayEvents.length; j++) {
        const event1 = dayEvents[i];
        const event2 = dayEvents[j];
        
        if (eventsOverlap(event1, event2, fields)) {
          overlapMap.get(event1.schedule_entry_id)!.push(event2.schedule_entry_id);
          overlapMap.get(event2.schedule_entry_id)!.push(event1.schedule_entry_id);
        }
      }
    }
    
    return overlapMap;
  }
  
  // Function to assign offset positions to overlapping events
  export function calculateEventOffsets(overlapMap: Map<number, number[]>): Map<number, number> {
    const offsetMap = new Map<number, number>();
    const processed = new Set<number>();
    
    for (const [eventId, overlaps] of overlapMap.entries()) {
      if (processed.has(eventId)) continue;
      
      if (overlaps.length === 0) {
        offsetMap.set(eventId, 0);
        processed.add(eventId);
        continue;
      }
      
      const group = [eventId, ...overlaps].filter(id => !processed.has(id));
      group.sort();
      
      group.forEach((id, index) => {
        offsetMap.set(id, index);
        processed.add(id);
      });
    }
    
    return offsetMap;
  }
  
  // Function to get the total number of overlaps for an event
  export function getTotalOverlaps(eventId: number, overlapMap: Map<number, number[]>): number {
    const overlaps = overlapMap.get(eventId) || [];
    return overlaps.length > 0 ? overlaps.length : 0;
  }
  