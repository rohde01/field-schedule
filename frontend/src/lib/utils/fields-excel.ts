import type { Field } from '$lib/schemas/field';

export async function exportFieldsToExcel(fields: Field[], facilityName?: string) {
    try {
        // Dynamic import to avoid build issues
        const XLSX = await import('xlsx');
        
        // Prepare data for Excel export
        const exportData = fields.map(field => ({
            'Name': field.name,
            'Size': field.size,
            'Field Type': field.field_type,
            'Half Fields': (field.half_subfields ?? []).map(h => h.name).join(', '),
            'Quarter Fields': [
                ...(field.quarter_subfields ?? []),
                ...((field.half_subfields?.flatMap(h => h.quarter_subfields ?? [])) ?? [])
            ].map(q => q.name).join(', '),
            'Status': field.is_active ? 'Active' : 'Inactive',
            'Facility': facilityName ?? 'Unknown'
        }));

        // Create workbook and worksheet
        const wb = XLSX.utils.book_new();
        const ws = XLSX.utils.json_to_sheet(exportData);

        // Set column widths for better formatting
        const colWidths = [
            { wch: 20 }, // Name
            { wch: 12 }, // Size
            { wch: 15 }, // Field Type
            { wch: 25 }, // Half Fields
            { wch: 30 }, // Quarter Fields
            { wch: 12 }, // Status
            { wch: 20 }  // Facility
        ];
        ws['!cols'] = colWidths;

        // Add worksheet to workbook
        XLSX.utils.book_append_sheet(wb, ws, 'Fields');

        // Generate filename with current date and facility name
        const today = new Date();
        const dateStr = today.toISOString().split('T')[0];
        const cleanFacilityName = facilityName?.replace(/[^a-zA-Z0-9]/g, '-') ?? 'all-facilities';
        const filename = `fields-export-${cleanFacilityName}-${dateStr}.xlsx`;

        // Save the file
        XLSX.writeFile(wb, filename);
    } catch (error) {
        console.error('Error exporting fields:', error);
    }
}