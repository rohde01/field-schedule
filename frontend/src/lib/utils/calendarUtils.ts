import type { Field } from '$lib/schemas/field';
import { updateScheduleEntry, selectedSchedule } from '../stores/schedules';
import type { ScheduleEntry } from '$lib/schemas/schedule';
import { writable, derived } from 'svelte/store';
import { browser } from '$app/environment';
import * as rrulelib from 'rrule';
import { createUTCDate, getTimeFromDate, normalizeTime, currentDate, isSameDay } from './dateUtils';
const { RRuleSet, rrulestr } = rrulelib;

// ---------------- Recurrence Helpers ----------------
function parseRecurrenceFrequency(recurrenceRule: string | null | undefined): string {
  if (!recurrenceRule) return 'WEEKLY';
  const m = recurrenceRule.match(/FREQ=(\w+)/); return m ? m[1] : 'WEEKLY';
}
function createRecurrenceRule(frequency: string): string { return `FREQ=${frequency}`; }
function isRecurringMaster(entry: ScheduleEntry): boolean { return !!entry.recurrence_rule && !entry.recurrence_id; }
function isRecurrenceException(entry: ScheduleEntry): boolean { return !!entry.recurrence_id; }
function isStandaloneEntry(entry: ScheduleEntry): boolean { return !entry.recurrence_rule && !entry.recurrence_id; }
function canEditRecurrence(entry: ProcessedScheduleEntry): boolean { return !entry.isRecurring && !entry.recurrence_id; }

export type ProcessedScheduleEntry = ScheduleEntry & {
  start_time: string;
  end_time: string;
  ui_id: string;
  isRecurring: boolean;
  occurrence_origin?: Date; // original unmodified start of generated occurrence
};

// ---------------- UI Time Slots ----------------
export const showEarlyTimeslots = writable(false);
export const timeSlots = writable<string[]>([]);
if (browser) {
  derived([showEarlyTimeslots], ([$showEarlyTimeslots]) => {
    const earliestStart = $showEarlyTimeslots ? '05:45' : '13:45';
    return generateTimeSlots(earliestStart, '23:45', 15);
  }).subscribe(val => timeSlots.set(val));
}

export function buildResources(allFields: Field[], sched: any | null): Field[] {
  if (!sched?.facility_id) return []; return allFields.filter(f => f.facility_id === sched.facility_id);
}
export function generateTimeSlots(start: string, end: string, intervalMinutes: number): string[] {
  const slots: string[] = []; const [sH,sM] = start.split(':').map(Number); const [eH,eM] = end.split(':').map(Number);
  let cur = sH*60+sM; const endMin = eH*60+eM; while (cur <= endMin) { const hh = String(Math.floor(cur/60)).padStart(2,'0'); const mm = String(cur%60).padStart(2,'0'); slots.push(`${hh}:${mm}`); cur += intervalMinutes; }
  return slots;
}

export function getRowForTimeWithSlots(time: string, slots: string[]): number { return slots.indexOf(normalizeTime(time)) + 2; }
export function getEntryRowEndWithSlots(endTime: string, slots: string[]): number { const norm = normalizeTime(endTime); const lastSlot = slots.findIndex(s => s >= norm) - 1; return lastSlot + 2; }
export function getEntryContentVisibility(startRow: number, endRow: number) { const span = endRow - startRow + 1; return { showTeamName: true, showField: span >= 2, showTime: span >= 3 }; }

// ---------------- Date / Filtering ----------------
export function shouldShowEntryOnDate(entry: ScheduleEntry, date: Date): boolean {
  const dt = typeof entry.dtstart === 'string' ? createUTCDate(entry.dtstart) : entry.dtstart;
  return dt.getUTCFullYear() === date.getUTCFullYear() && dt.getUTCMonth() === date.getUTCMonth() && dt.getUTCDate() === date.getUTCDate();
}

function getScheduleDateRange(schedule: any) {
  if (schedule?.active_from && schedule?.active_until) {
    const start = createUTCDate(schedule.active_from); const end = createUTCDate(schedule.active_until); end.setUTCHours(23,59,59,999); return { startDate: start, endDate: end };
  }
  const y = new Date().getUTCFullYear();
  return { startDate: new Date(Date.UTC(y-1,0,1)), endDate: new Date(Date.UTC(y+1,11,31,23,59,59)) };
}

// ---------------- Processing ----------------
function createProcessedEntry(entry: ScheduleEntry, kind: string, idx: number, isRecurring = false): ProcessedScheduleEntry {
  const dtstart = createUTCDate(entry.dtstart); const dtend = createUTCDate(entry.dtend);
  const start_time = getTimeFromDate(dtstart); const end_time = getTimeFromDate(dtend);
  const prefix = kind === 'onetime' ? 'S' : kind === 'master' ? 'M' : kind === 'exception' ? 'X' : 'R';
  const base: ProcessedScheduleEntry = { ...entry, dtstart, dtend, start_time, end_time, ui_id: `${prefix}|${entry.uid}|${dtstart.toISOString()}|${idx}`, isRecurring } as ProcessedScheduleEntry;
  if (isRecurring) base.occurrence_origin = new Date(dtstart.getTime());
  return base;
}

function dayBounds(date: Date) { const start = new Date(Date.UTC(date.getUTCFullYear(), date.getUTCMonth(), date.getUTCDate(),0,0,0,0)); const end = new Date(start.getTime()); end.setUTCHours(23,59,59,999); return { dayStart: start, dayEnd: end }; }

function expandMasterForDate(master: ScheduleEntry, date: Date, exceptionRecIds: Set<number>, schedule: any): ProcessedScheduleEntry[] {
  if (!master.recurrence_rule) return [];
  const { dayStart, dayEnd } = dayBounds(date);
  const set = new RRuleSet();
  const masterDtStart = createUTCDate(master.dtstart);
  const ruleString = master.recurrence_rule.startsWith('RRULE:') ? master.recurrence_rule : `RRULE:${master.recurrence_rule}`;
  try { set.rrule(rrulestr(ruleString, { dtstart: masterDtStart })); } catch { return []; }
  (master.exdate || [])?.forEach(d => { try { set.exdate(createUTCDate(d)); } catch {/*ignore*/} });
  const occ = set.between(dayStart, dayEnd, true);
  const masterOriginalTs = masterDtStart.getTime();
  const duration = createUTCDate(master.dtend).getTime() - masterDtStart.getTime();
  return occ
    .filter(o => o.getTime() !== masterOriginalTs)
    .filter(o => !exceptionRecIds.has(o.getTime()))
    .map((o, i) => {
      const instEnd = new Date(o.getTime() + duration);
      const inst: ScheduleEntry = { ...master, schedule_entry_id: null, dtstart: o, dtend: instEnd } as any;
      const pe = createProcessedEntry(inst, 'recurring', i, true);
      pe.occurrence_origin = new Date(o.getTime());
      return pe;
    });
}

function categorizeScheduleEntries(entries: ScheduleEntry[]) {
  const regular: ScheduleEntry[] = []; const masters: ScheduleEntry[] = []; const exceptions: ScheduleEntry[] = [];
  entries.forEach(e => { if (isRecurrenceException(e)) exceptions.push(e); else if (isRecurringMaster(e)) masters.push(e); else regular.push(e); });
  return { regular, masters, exceptions };
}

function getAllEntriesForDate(schedule: { schedule_entries?: ScheduleEntry[] } | null, date: Date): ProcessedScheduleEntry[] {
  if (!schedule) return [];
  const { regular, masters, exceptions } = categorizeScheduleEntries(schedule.schedule_entries || []);
  const exceptionRecurrenceMap = new Map<string, Set<number>>();
  exceptions.forEach(ex => { if (!ex.uid || !ex.recurrence_id) return; const d = ex.recurrence_id instanceof Date ? ex.recurrence_id : new Date(ex.recurrence_id); const ts = d.getTime(); if (!exceptionRecurrenceMap.has(ex.uid)) exceptionRecurrenceMap.set(ex.uid, new Set()); exceptionRecurrenceMap.get(ex.uid)!.add(ts); });
  const oneTimes = regular.filter(e => shouldShowEntryOnDate(e, date)).map((e,i) => createProcessedEntry(e,'onetime',i,false));
  const masterOriginals = masters.filter(e => shouldShowEntryOnDate(e, date)).map((e,i) => createProcessedEntry(e,'master',i,false));
  const dayExceptions = exceptions.filter(e => shouldShowEntryOnDate(e, date)).map((e,i) => createProcessedEntry(e,'exception',i,false));
  const recurrences: ProcessedScheduleEntry[] = []; masters.forEach(m => recurrences.push(...expandMasterForDate(m,date,exceptionRecurrenceMap.get(m.uid)||new Set(),schedule)));
  return [...oneTimes, ...masterOriginals, ...dayExceptions, ...recurrences];
}

// ---------------- Store ----------------
export const processedEntries = writable<ProcessedScheduleEntry[]>([]);
if (browser) {
  derived([selectedSchedule, currentDate], ([$sched,$date]) => $sched ? getAllEntriesForDate($sched,$date) : [])
    .subscribe(newList => {
      processedEntries.update(prev => newList.map(ne => {
        const ex = prev.find(p => p.uid === ne.uid && p.dtstart.getTime() === ne.dtstart.getTime() && (!!p.recurrence_id === !!ne.recurrence_id));
        return ex ? { ...ne, ui_id: ex.ui_id, occurrence_origin: ex.occurrence_origin } : ne;
      }));
    });
} else { writable<ProcessedScheduleEntry[]>([]); }

// ---------------- Update / Exports ----------------
export { parseRecurrenceFrequency, createRecurrenceRule, canEditRecurrence, isRecurringMaster, isRecurrenceException, isStandaloneEntry };

export function getOriginalRecurrenceStart(entry: any): string | null {
  if (entry.isRecurring) return entry.dtstart instanceof Date ? entry.dtstart.toISOString() : entry.dtstart; // generated instance
  if (entry.recurrence_id) return entry.recurrence_id instanceof Date ? entry.recurrence_id.toISOString() : entry.recurrence_id; // exception
  return null; // standalone or master edit (apply to master)
}

export function commitUpdate(entry: any, originalRecurrence: string | null) {
  updateScheduleEntry({
    uid: entry.uid,
    schedule_id: entry.schedule_id,
    field_id: entry.field_id,
    dtstart: entry.dtstart,
    dtend: entry.dtend,
    team_id: entry.team_id,
    summary: entry.summary,
    recurrence_rule: entry.recurrence_rule,
    recurrence_id: originalRecurrence ? new Date(originalRecurrence) : (entry.recurrence_id ? new Date(entry.recurrence_id) : null)
  });
}

export function getEntryTitle(entry: ProcessedScheduleEntry, teamNameLookup: Map<number, string>): string {
  if (entry.summary) return entry.summary;
  if (entry.team_id != null) return teamNameLookup.get(entry.team_id) ?? `Team ${entry.team_id}`;
  return 'Untitled Event';
}
