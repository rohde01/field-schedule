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

export const weekDays = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];

export const currentWeekDay = derived(currentDate, ($currentDate) => {
  return $currentDate.getDay();
});

export function formatDate(date: Date): string {
  return `${weekDays[date.getDay()]}, ${date.toLocaleDateString('en-US', { 
    month: 'long', 
    day: 'numeric',
    year: 'numeric'
  })}`;
}

export function formatWeekdayOnly(date: Date): string {
  return weekDays[date.getDay()];
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
