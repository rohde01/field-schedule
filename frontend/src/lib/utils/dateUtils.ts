import type { ActiveSchedule, CalendarDate } from '$lib/schemas/schedule';

export function formatDateYYYYMMDD(date: Date): string {
  return date.toISOString().split('T')[0];
}

export function parseDate(dateString: string): Date {
  return new Date(dateString);
}

function getJSDayOfWeek(date: Date): number {
  return date.getDay();
}

// Get custom day of week (0-6, Monday-Sunday)
export function getDayOfWeek(date: Date): number {
  const jsDay = date.getDay();
  // Convert from JS day (0=Sunday) to our custom day (0=Monday)
  return jsDay === 0 ? 6 : jsDay - 1;
}

export function addDays(date: Date, days: number): Date {
  const result = new Date(date);
  result.setDate(result.getDate() + days);
  return result;
}

// Format date for display (e.g., "Mon, Jan 15")
export function formatDateForDisplay(date: Date): string {
  return date.toLocaleDateString('en-US', { 
    weekday: 'short', 
    month: 'short', 
    day: 'numeric' 
  });
}

// Get the ISO week number of the year (1-53)
export function getWeekNumber(date: Date): number {
  const d = new Date(Date.UTC(date.getFullYear(), date.getMonth(), date.getDate()));
  const dayNum = d.getUTCDay() || 7;
  d.setUTCDate(d.getUTCDate() + 4 - dayNum);
  const yearStart = new Date(Date.UTC(d.getUTCFullYear(), 0, 1));
  return Math.ceil((((d.getTime() - yearStart.getTime()) / 86400000) + 1) / 7);
}

export function findActiveScheduleForDate(
  date: Date, 
  activeSchedules: ActiveSchedule[]
): ActiveSchedule | undefined {
  const dateStr = formatDateYYYYMMDD(date);
  
  return activeSchedules.find(schedule => {
    const startDate = schedule.start_date;
    const endDate = schedule.end_date;
    return dateStr >= startDate && dateStr <= endDate;
  });
}

export function createCalendarDate(
  date: Date, 
  activeSchedules: ActiveSchedule[]
): CalendarDate {
  const weekDay = getDayOfWeek(date);
  const formattedDate = formatDateForDisplay(date);
  const activeSchedule = findActiveScheduleForDate(date, activeSchedules);
  
  return {
    date,
    weekDay,
    formattedDate,
    isWithinActiveSchedule: !!activeSchedule,
    activeScheduleId: activeSchedule?.schedule_id
  };
}

export function getWeekDates(baseDate: Date, activeSchedules: ActiveSchedule[]): CalendarDate[] {
  const dates: CalendarDate[] = [];
  

  const monday = new Date(baseDate);
  const jsDay = getJSDayOfWeek(baseDate);
  const diff = jsDay === 0 ? -6 : 1 - jsDay; 
  monday.setDate(baseDate.getDate() + diff);
  
  for (let i = 0; i < 7; i++) {
    const date = addDays(monday, i);
    dates.push(createCalendarDate(date, activeSchedules));
  }
  
  return dates;
}

export function formatMonthAndYear(date: Date): string {
  return date.toLocaleDateString('en-US', { 
    month: 'long',
    year: 'numeric'
  });
}

export function getCurrentMonthDate(): Date {
  return new Date();
}

export function navigateMonth(date: Date, direction: 'prev' | 'next'): Date {
  const newDate = new Date(date);
  newDate.setMonth(date.getMonth() + (direction === 'prev' ? -1 : 1));
  return newDate;
}

export function getFormattedMonth(date: Date): string {
  return formatMonthAndYear(date);
}
