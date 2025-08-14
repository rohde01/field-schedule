import type { ProcessedScheduleEntry } from './calendarUtils';


// Function to get CSS class based on category
export function getCategoryClass(entry: ProcessedScheduleEntry): string {
  const category = entry.categories && entry.categories.length > 0 ? entry.categories[0] : 'Training';
  switch (category) {
    case 'Match':
      return 'category-match';
    case 'Event':
      return 'category-event';
    case 'Training':
    default:
      return 'category-training';
  }
}