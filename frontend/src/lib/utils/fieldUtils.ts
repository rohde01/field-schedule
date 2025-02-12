import type { Field } from '$lib/schemas/field';

export interface CandidateState {
  field_id: number;
  colIndex: number;
  width: number;
  candidateType: 'main' | 'half' | 'quarter';
}

export function getCandidateStatesForMainField(
  mainField: Field,
  fieldToGridColMap: Map<number, { colIndex: number; colSpan: number }>
): CandidateState[] {
  const candidates: CandidateState[] = [];
  const mainMapping = fieldToGridColMap.get(mainField.field_id);
  if (!mainMapping) return candidates;
  
  // Full main field candidate
  candidates.push({
    field_id: mainField.field_id,
    colIndex: mainMapping.colIndex,
    width: mainMapping.colSpan,
    candidateType: 'main'
  });
  
  if (mainField.half_subfields.length > 0) {
    for (const half of mainField.half_subfields) {
      const halfMapping = fieldToGridColMap.get(half.field_id);
      if (halfMapping) {
        const quarters = getQuarterFieldsForHalf(mainField, half.field_id);
        if (quarters.length > 0) {
          for (const q of quarters) {
            const qMapping = fieldToGridColMap.get(q.field_id);
            if (qMapping) {
              candidates.push({
                field_id: q.field_id,
                colIndex: qMapping.colIndex,
                width: qMapping.colSpan,
                candidateType: 'quarter'
              });
            }
          }
          candidates.push({
            field_id: half.field_id,
            colIndex: halfMapping.colIndex,
            width: halfMapping.colSpan,
            candidateType: 'half'
          });
        } else {
          candidates.push({
            field_id: half.field_id,
            colIndex: halfMapping.colIndex,
            width: halfMapping.colSpan,
            candidateType: 'half'
          });
        }
      }
    }
  }
  
  candidates.sort((a, b) => {
    if (a.colIndex !== b.colIndex) return a.colIndex - b.colIndex;
    return a.width - b.width;
  });
  
  return candidates;
}

export function getMainFieldForEvent(fieldId: number, activeFields: Field[]): Field | null {
  for (const field of activeFields) {
    if (field.field_id === fieldId) return field;
    if (field.half_subfields.some(h => h.field_id === fieldId)) return field;
    if (field.quarter_subfields.some(q => q.field_id === fieldId)) return field;
  }
  return null;
}

export function getQuarterFieldsForHalf(field: Field, halfFieldId: number) {
    return field.quarter_subfields.filter(
      (q) => q.parent_field_id === halfFieldId
    );
  }
  
export function getFieldColumns(field: Field): number {
    if (!field.half_subfields.length) {
      return 1;
    }
    return field.half_subfields.reduce((acc, half) => {
      const quarterCount = getQuarterFieldsForHalf(field, half.field_id).length;
      return acc + (quarterCount || 1);
    }, 0);
  }

      // Build a mapping from each field (and subfield) to its grid column start and span.
export function buildFieldToGridColumnMap(fields: Field[]) {
    const map = new Map<number, { colIndex: number; colSpan: number }>();
    let currentColIndex = 2;  // col 1 is reserved for Time
  
    for (const field of fields) {
      const totalColumnsForField = getFieldColumns(field);
      map.set(field.field_id, {
        colIndex: currentColIndex,
        colSpan: totalColumnsForField
      });
  
      if (!field.half_subfields.length) {
        currentColIndex += 1;
      } else {
        for (const half of field.half_subfields) {
          const quarterFields = getQuarterFieldsForHalf(field, half.field_id);
  
          // Add mapping for the half field itself
          map.set(half.field_id, {
            colIndex: currentColIndex,
            colSpan: quarterFields.length || 1
          });
  
          if (quarterFields.length === 0) {
            currentColIndex += 1;
          } else {
            for (const q of quarterFields) {
              map.set(q.field_id, {
                colIndex: currentColIndex,
                colSpan: 1
              });
              currentColIndex += 1;
            }
          }
        }
      }
    }
  
    return map;
  }

export interface HeaderCell {
  label: string;
  colIndex: number;
  colSpan: number;
  fieldId: number;
}

export function generateHeaderCells(activeFields: Field[], fieldToGridColMap: Map<number, { colIndex: number; colSpan: number }>): HeaderCell[] {
  const headerCells: HeaderCell[] = [];
  let colIndex = 2;  // col 1 is "Time"

  for (const field of activeFields) {
    if (!field.half_subfields.length) {
      headerCells.push({
        label: field.name,
        colIndex,
        colSpan: 1,
        fieldId: field.field_id
      });
      colIndex += 1;
    } else {
      for (const half of field.half_subfields) {
        const quarterFields = getQuarterFieldsForHalf(field, half.field_id);
        if (quarterFields.length === 0) {
          headerCells.push({
            label: half.name,
            colIndex,
            colSpan: 1,
            fieldId: half.field_id
          });
          colIndex += 1;
        } else {
          for (const q of quarterFields) {
            headerCells.push({
              label: q.name,
              colIndex,
              colSpan: 1,
              fieldId: q.field_id
            });
            colIndex += 1;
          }
        }
      }
    }
  }
  
  return headerCells;
}

export function getFieldName(fieldId: number, activeFields: Field[]): string {
  const field = activeFields.find(f => f.field_id === fieldId);
  if (field) return field.name;
  
  for (const mainField of activeFields) {
    const half = mainField.half_subfields.find(h => h.field_id === fieldId);
    if (half) return half.name;
    
    const quarter = mainField.quarter_subfields.find(q => q.field_id === fieldId);
    if (quarter) return quarter.name;
  }
  return `Field ${fieldId}`;
}

export function generateFieldOptions(fields: Field[]): { value: number; label: string }[] {
  const options: { value: number; label: string }[] = [];
  
  for (const field of fields) {
    options.push({ value: field.field_id, label: field.name });
    
    for (const half of field.half_subfields) {
      options.push({ value: half.field_id, label: half.name });
      
      const quarters = field.quarter_subfields.filter(q => q.parent_field_id === half.field_id);
      for (const quarter of quarters) {
        options.push({ value: quarter.field_id, label: quarter.name });
      }
    }
  }
  
  return options;
}


