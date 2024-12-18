<script>
    import Calendar from '@event-calendar/core';
    import TimeGrid from '@event-calendar/resource-time-grid';
    import { fields } from '../../stores/fields';
    

    let plugins = [TimeGrid];

    // Example events (can remain as is, or adjust as needed)
    let events = [
        {
            id: '1',
            resourceIds: ['1'],
            title: 'Team A Practice',
            start: '2024-12-18T10:00:00',
            end: '2024-12-18T12:00:00',
            backgroundColor: '#FF0000'
        },
        // ... more events ...
    ];

    let options = {
        view: 'resourceTimeGridDay',
        height: '100%',
        nowIndicator: true,
        slotMinWidth: 100,
        resources: [], // Will be filled in dynamically
        events: events,
    };

    // Subscribe to fields and rebuild resources whenever they change
    const unsubscribe = fields.subscribe($fields => {
        // Build the resources structure from $fields
        const newResources = buildResources($fields);

        // Update the options object
        options = {
            ...options,
            resources: newResources
        };
    });

    // Utility function to build the hierarchical resources
    function buildResources(allFields) {
        // Filter fields by facility_id first
        const facilityFields = allFields.filter(field => field.facility_id === 1);
        
        // Then filter top-level fields from the facility-filtered set
        const topLevelFields = facilityFields.filter(field => field.parent_field_id === null);

        // Convert each top-level field into a resource object
        return topLevelFields.map(field => toResource(field));
    }

    // Convert a single Field object into the hierarchical resource structure
    function toResource(field) {
        // half_subfields and quarter_subfields are arrays of subFieldSchema, which represent child fields
        const halfChildren = field.half_subfields.map(half => ({
            id: half.field_id.toString(),
            title: half.name,
            parentId: half.parent_field_id?.toString() ?? null,
            children: [] // half_subfields are leaves in this model
        }));

        const quarterChildren = field.quarter_subfields.map(quarter => ({
            id: quarter.field_id.toString(),
            title: quarter.name,
            parentId: quarter.parent_field_id?.toString() ?? null,
            children: [] // quarter_subfields are also leaves
        }));

        return {
            id: field.field_id.toString(),
            title: field.name,
            parentId: field.parent_field_id?.toString() ?? null,
            children: [...halfChildren, ...quarterChildren]
        };
    }
</script>

<div style="height: 900px;">
    <Calendar {plugins} {options} />
</div>
