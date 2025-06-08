import type { Team } from '$lib/schemas/team';

export function formatFieldSize(size: number): string {
    switch (size) {
        case 1000:
            return '11v11';
        case 500:
            return '8v8, Half 11v11';
        case 250:
            return '5v5, Half 8v8, Quarter 11v11';
        case 125:
            return '3v3, Half 5v5, Quarter 8v8';
        default:
            return `${size}`;
    }
}

export async function exportTeamsToExcel(teams: Team[]) {
    try {
        // Dynamic import to avoid build issues
        const XLSX = await import('xlsx');
        
        // Prepare data for Excel export
        const exportData = teams.map(team => ({
            'Name': team.name,
            'Year': team.year,
            'Gender': team.gender,
            'Academy': team.is_academy ? 'Yes' : 'No',
            'Level': team.level,
            'Field Size': formatFieldSize(team.minimum_field_size),
            'Weekly Trainings': team.weekly_trainings,
            'Status': team.is_active ? 'Active' : 'Inactive'
        }));

        // Create workbook and worksheet
        const wb = XLSX.utils.book_new();
        const ws = XLSX.utils.json_to_sheet(exportData);

        // Set column widths for better formatting
        const colWidths = [
            { wch: 20 }, // Name
            { wch: 10 }, // Year
            { wch: 10 }, // Gender
            { wch: 10 }, // Academy
            { wch: 15 }, // Level
            { wch: 25 }, // Field Size
            { wch: 18 }, // Weekly Trainings
            { wch: 12 }  // Status
        ];
        ws['!cols'] = colWidths;

        // Add worksheet to workbook
        XLSX.utils.book_append_sheet(wb, ws, 'Teams');

        // Generate filename with current date
        const today = new Date();
        const dateStr = today.toISOString().split('T')[0];
        const filename = `teams-export-${dateStr}.xlsx`;

        // Save the file
        XLSX.writeFile(wb, filename);
    } catch (error) {
        console.error('Error exporting teams:', error);
    }
}