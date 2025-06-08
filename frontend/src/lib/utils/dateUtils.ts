import { writable, derived } from 'svelte/store';

const today = new Date();
export const currentDate = writable(new Date(Date.UTC(today.getFullYear(), today.getMonth(), today.getDate())));
export const currentTime = writable(new Date());
export let timeTrackingEnabled = false;

export function updateCurrentTime() {
  currentTime.set(new Date());
  if (isToday()){
    timeTrackingEnabled = true;
  } else {
    timeTrackingEnabled = false;
  }
  return timeTrackingEnabled;
}

export function getCurrentTimePosition(): number {
  const now = new Date();
  const hours = now.getHours();
  const minutes = now.getMinutes();
  const totalMinutes = hours * 60 + minutes;
  return (totalMinutes / (24 * 60)) * 100;
}

export function isToday(): boolean {
  let now = new Date();
  let curDate: Date | undefined;
  
  currentDate.subscribe(val => {
    curDate = val;
  })();
  
  if (!curDate) return false;
  
  return curDate.getDate() === now.getDate() &&
         curDate.getMonth() === now.getMonth() &&
         curDate.getFullYear() === now.getFullYear();
}

export function formatTimeForDisplay(date: Date): string {
  const hours = date.getHours().toString().padStart(2, '0');
  const minutes = date.getMinutes().toString().padStart(2, '0');
  return `${hours}.${minutes}`;
}

export function shouldHideHourLabel(time: string): boolean {
  if (!timeTrackingEnabled || !isHourMark(time)) return false;
  
  const now = new Date();
  const currentHour = now.getHours();
  const currentMinutes = now.getMinutes();
  const timeHour = parseInt(time.split(':')[0]);
  
  return currentHour === timeHour && 
         (currentMinutes >= 50 || currentMinutes <= 10);
}

export function isHourMark(time: string): boolean {
  return time.endsWith(':00') && time !== '00:00' && time !== '24:00';
}

export const weekDays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];

export const currentWeekDay = derived(currentDate, ($currentDate) => {
  return $currentDate.getDay();
});

export function isSameDay(date1: Date, date2: Date): boolean {
  return date1.getUTCFullYear() === date2.getUTCFullYear() &&
         date1.getUTCMonth() === date2.getUTCMonth() &&
         date1.getUTCDate() === date2.getUTCDate();
}

export function formatDate(date: Date): string {
  return date.toLocaleDateString('da-DK', { day: 'numeric', month: 'long', year: 'numeric' });
}

export function formatWeekdayOnly(date: Date): string {
  return date.toLocaleDateString('da-DK', { weekday: 'long' });
}

export function nextDay() {
  currentDate.update(date => {
    const newDate = new Date(date);
    newDate.setUTCDate(date.getUTCDate() + 1);
    return newDate;
  });
}

export function previousDay() {
  currentDate.update(date => {
    const newDate = new Date(date);
    newDate.setUTCDate(date.getUTCDate() - 1);
    return newDate;
  });
}

export function createUTCDate(dateInput: string | Date): Date {
  return new Date(dateInput);
}

export function getTimeFromDate(date: Date | string): string {
  const d = typeof date === 'string' ? new Date(date) : date;
  const hours = d.getUTCHours().toString().padStart(2, '0');
  const minutes = d.getUTCMinutes().toString().padStart(2, '0');
  return `${hours}:${minutes}`;
}

export function normalizeTime(time: string): string {
  return time.slice(0, 5);
}

// Format date to DD/MM/YYYY-HH:MM (UTC)
export function formatDateTimeUTC(date: Date | string): string {
  const d = typeof date === 'string' ? new Date(date) : date;
  
  const day = d.getUTCDate().toString().padStart(2, '0');
  const month = (d.getUTCMonth() + 1).toString().padStart(2, '0');
  const year = d.getUTCFullYear();
  const hours = d.getUTCHours().toString().padStart(2, '0');
  const minutes = d.getUTCMinutes().toString().padStart(2, '0');
  
  return `${day}/${month}/${year}-${hours}:${minutes}`;
}

// Add helper to combine date and time into a single UTC Date
export function combineDateAndTime(dateInput: Date | string, time: string): Date {
  const baseDate = new Date(dateInput);
  const [h, m] = time.split(':').map(Number);
  baseDate.setUTCHours(h, m, 0, 0);
  return baseDate;
}

export function formatDateAsYYYYMMDD(date: Date): string {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

// Compute new Date from base date and HH:mm string
export function computeDateUTC(baseDate: Date, time: string): Date {
  const [year, month, day] = formatDateAsYYYYMMDD(baseDate).split('-').map(Number);
  const [h, m] = time.split(':').map(Number);
  return new Date(Date.UTC(year, month - 1, day, h, m));
}

// Utility to get weekday number (0-6) from a date
export function getWeekdayNumber(date: Date | string): number {
  const d = typeof date === 'string' ? new Date(date) : date;
  // Convert JavaScript's day (0=Sunday, 1=Monday) to our backend format (0=Monday, 1=Tuesday)
  const jsDay = d.getDay();
  return jsDay === 0 ? 6 : jsDay - 1; // Sunday becomes 6, everything else shifts down by 1
}