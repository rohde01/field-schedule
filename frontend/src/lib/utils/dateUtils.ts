import { writable, derived } from 'svelte/store';
import { browser } from '$app/environment';

const today = new Date();
export const currentDate = writable(new Date(Date.UTC(today.getFullYear(), today.getMonth(), today.getDate())));

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
  return new Date(dateInput + 'Z');
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