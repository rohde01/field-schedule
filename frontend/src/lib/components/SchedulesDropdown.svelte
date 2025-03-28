<script lang="ts">
    import { schedules } from '$stores/schedules';
    import { dropdownState, toggleDropdown, selectSchedule } from '$stores/ScheduleDropdownState';
    import type { Schedule } from '$lib/schemas/schedule';
    import type { SubmitFunction } from '@sveltejs/kit';
    import { invalidateAll } from '$app/navigation';

    let isDeleting = $state(false);

    const handleDelete: SubmitFunction = () => {
        isDeleting = true;
        return async ({ result }) => {
            if (result.type === 'success') {
                await invalidateAll();
            }
            isDeleting = false;
        };
    };

    function handleSelect(schedule: Schedule) {
        selectSchedule(schedule);
        dropdownState.update(state => ({ ...state, isOpen: false }));
    }
    
    function confirmDelete(scheduleId: number, scheduleName: string) {
        if (confirm(`Are you sure you want to delete the schedule "${scheduleName}"? This action cannot be undone.`)) {
            const form = document.createElement('form');
            form.method = 'POST';
            form.action = '?/deleteSchedule';
            
            const input = document.createElement('input');
            input.type = 'hidden';
            input.name = 'schedule_id';
            input.value = scheduleId.toString();
            
            form.appendChild(input);
            document.body.appendChild(form);
            form.submit();
        }
    }
</script>

<div class="facilities-dropdown">
    <div 
        class="relative"
        class:w-72={$dropdownState.isOpen}
        class:w-56={!$dropdownState.isOpen}
    >
        <button
            onclick={(e) => {
                e.stopPropagation();
                toggleDropdown('isOpen');
            }}
            class="dropdown-trigger"
            aria-label="Toggle schedule dropdown"
        >
            <span class="text-sm font-medium truncate">
                {$dropdownState.selectedSchedule?.name || 'Select Schedule'}
            </span>
            <svg
                class="w-5 h-5 transition-transform duration-200"
                class:rotate-180={$dropdownState.isOpen}
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 20 20"
                fill="currentColor"
            >
                <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
            </svg>
        </button>

        {#if $dropdownState.isOpen}
            <div class="dropdown-panel">
                <div class="dropdown-content">
                    {#if $schedules.length === 0}
                        <div class="p-4 text-sage-500 text-center text-sm">
                            <p>No schedules to display</p>
                            <p class="mt-1 text-xs">Schedules you create will appear here</p>
                        </div>
                    {:else}
                        {#each $schedules as schedule}
                            <div class="relative">
                                <button
                                    onclick={(e) => {
                                        e.stopPropagation();
                                        handleSelect(schedule);
                                    }}
                                    class="dropdown-item {$dropdownState.selectedSchedule?.schedule_id === schedule.schedule_id ? 'dropdown-item-selected' : ''}"
                                >
                                    <span class="font-medium">{schedule.name}</span>
                                </button>
                                <button
                                    class="btn-trash"
                                    onclick={(e) => {
                                        e.stopPropagation();
                                        confirmDelete(schedule.schedule_id, schedule.name);
                                    }}
                                    aria-label={`Delete schedule ${schedule.name}`}
                                >
                                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                                    </svg>
                                </button>
                            </div>
                        {/each}
                    {/if}
                </div>
            </div>
        {/if}
    </div>
</div>

