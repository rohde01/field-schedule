<script>
    import Calendar from '@event-calendar/core';
    import TimeGrid from '@event-calendar/resource-time-grid';

    let plugins = [TimeGrid];

    // Example resources with quarter fields
    let originalResources = [
        { 
            id: 'k1',
            title: 'Kunst 1',
            children: [
                { 
                    id: 'k1-a', 
                    title: 'K1-A', 
                    parentId: 'k1',
                    children: [
                        { id: 'k1-1', title: 'K1-1', parentId: 'k1-a' },
                        { id: 'k1-2', title: 'K1-2', parentId: 'k1-a' }
                    ]
                },
                { 
                    id: 'k1-b', 
                    title: 'K1-B', 
                    parentId: 'k1',
                    children: [
                        { id: 'k1-3', title: 'K1-3', parentId: 'k1-b' },
                        { id: 'k1-4', title: 'K1-4', parentId: 'k1-b' }
                    ]
                }
            ]
        },
        { 
            id: 'k2',
            title: 'Kunst 2',
            children: [
                { 
                    id: 'k2-a', 
                    title: 'K2-A', 
                    parentId: 'k2',
                    children: [
                        { id: 'k2-1', title: 'K2-1', parentId: 'k2-a' },
                        { id: 'k2-2', title: 'K2-2', parentId: 'k2-a' }
                    ]
                },
                { 
                    id: 'k2-b', 
                    title: 'K2-B', 
                    parentId: 'k2',
                    children: [
                        { id: 'k2-3', title: 'K2-3', parentId: 'k2-b' },
                        { id: 'k2-4', title: 'K2-4', parentId: 'k2-b' }
                    ]
                }
            ]
        }

    ];

    let events = [
        {
            id: '1',
            resourceId: 'k1',
            title: 'Team A Practice',
            start: '2024-12-18T10:00:00',
            end: '2024-12-18T12:00:00',
            backgroundColor: '#FF0000' // Bright Red
        },
        {
            id: '2',
            resourceId: 'k1-a',
            title: 'Team B Game',
            start: '2024-12-18T12:00:00',
            end: '2024-12-18T16:00:00',
            backgroundColor: '#00BFFF' // Bright Blue
        },
        {
            id: '3',
            resourceId: 'k1-b',
            title: 'Team C Game',
            start: '2024-12-18T12:00:00',
            end: '2024-12-18T16:00:00',
            backgroundColor: '#32CD32' // Bright Green
        },
        {
            id: '4',
            resourceId: 'k1-1',
            title: 'Team D Practice',
            start: '2024-12-18T16:00:00',
            end: '2024-12-18T18:00:00',
            backgroundColor: '#FFD700' // Bright Yellow
        },
        {
            id: '5',
            resourceId: 'k1-2',
            title: 'Team E Practice',
            start: '2024-12-18T16:00:00',
            end: '2024-12-18T18:00:00',
            backgroundColor: '#FF69B4' // Bright Pink
        },
        {
            id: '6',
            resourceId: 'k1-3',
            title: 'Team F Practice',
            start: '2024-12-18T16:00:00',
            end: '2024-12-18T18:00:00',
            backgroundColor: '#8A2BE2' // Blue Violet
        },
        {
            id: '7',
            resourceId: 'k1-4',
            title: 'Team G Practice',
            start: '2024-12-18T16:00:00',
            end: '2024-12-18T18:00:00',
            backgroundColor: '#FF4500' // Orange Red
        },
        {
            id: '8',
            resourceId: 'k2',
            title: 'Team H Practice',
            start: '2024-12-18T10:00:00',
            end: '2024-12-18T12:00:00',
            backgroundColor: '#FF0000' // Bright Red
        }
    ];

    // Normalize events to ensure we have resourceIds array for easier processing
    events = events.map(e => {
        let ids = [];
        if (e.resourceIds) {
            ids = e.resourceIds;
        } else if (e.resourceId) {
            ids = Array.isArray(e.resourceId) ? e.resourceId : [e.resourceId];
        }
        return { ...e, resourceIds: ids };
    });

    const usedResourceIds = new Set(events.flatMap(e => e.resourceIds));

    /**
     * Recursively process resources:
     * - If a parent is used and children are also used, replicate parent's events to all its children and only show the children.
     * - If children are not used but parent is used, show parent.
     * - If no usage, omit the resource.
     */
    function processResources(resources, updatedEvents) {
        let filtered = [];

        for (const resource of resources) {
            const parentId = resource.id;
            const children = resource.children || [];
            
            // Process children first (recursive call)
            let childResults = [];
            let newEvents = updatedEvents;
            if (children.length > 0) {
                const { filteredResources: processedChildren, events: childEvents } = processResources(children, updatedEvents);
                childResults = processedChildren;
                newEvents = childEvents;
            }

            const parentUsed = newEvents.some(e => e.resourceIds.includes(parentId));
            const childrenUsed = childResults.length > 0;

            if (childrenUsed) {
                // Children are used, so if parent is used, replicate parent's events to children
                if (parentUsed) {
                    newEvents = newEvents.map(e => {
                        if (e.resourceIds.includes(parentId)) {
                            // Remove parent reference and add all children (grandchildren, etc.)
                            const newResourceIds = new Set(
                                e.resourceIds.filter(rid => rid !== parentId)
                                    .concat(childResults.map(c => c.id))
                            );
                            return { ...e, resourceIds: Array.from(newResourceIds) };
                        }
                        return e;
                    });
                }
                // Show only children columns
                filtered.push(...childResults);
                updatedEvents = newEvents;
            } else {
                // No children used
                if (parentUsed) {
                    // Only parent is used, show parent alone
                    filtered.push({
                        id: parentId,
                        title: resource.title,
                        parentId: resource.parentId
                    });
                    updatedEvents = newEvents; 
                } else {
                    // Parent not used and no children used - omit entirely
                    updatedEvents = newEvents; 
                }
            }
        }

        return { filteredResources: filtered, events: updatedEvents };
    }

    let { filteredResources, events: updatedEvents } = processResources(originalResources, events);

    // Final cleanup: remove events with no matching resources
    const finalResourceIds = new Set(filteredResources.map(r => r.id));
    updatedEvents = updatedEvents.map(e => {
        const newIds = e.resourceIds.filter(id => finalResourceIds.has(id));
        return { ...e, resourceIds: newIds };
    }).filter(e => e.resourceIds.length > 0);

    let options = {
        view: 'resourceTimeGridDay',
        height: '100%',
        nowIndicator: true,
        slotMinWidth: 100,
        resources: filteredResources,
        events: updatedEvents
    };
</script>

<div style="height: 500px;">
    <Calendar {plugins} {options} />
</div>

<style>
    .calendar-container {
        min-height: 500px;
    }

    :global(.ec-resource-tree) {
        margin-left: 0.5em;
    }
</style>
