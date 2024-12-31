<script lang="ts">
    import { schedules } from '$stores/schedules';
    import { dropdownState, toggleDropdown, selectSchedule } from '$stores/ScheduleDropdownState';
    import type { Schedule } from '$lib/schemas/schedule';

    let dropdownContainer: HTMLDivElement;

    function handleSelect(schedule: Schedule) {
        selectSchedule(schedule);
        dropdownState.update(state => ({ ...state, isOpen: false }));
    }

</script>

<div class="schedules-dropdown">
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
        >
            <span class="text-sm font-medium truncate">
                {$dropdownState.selectedSchedule?.name || 'Select Schedule'}
            </span>
            <svg
                class="w-5 h-5 transition-transform duration-200 ml-3"
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
                    {#each $schedules as schedule}
                        <button
                            onclick={(e) => {
                                e.stopPropagation();
                                handleSelect(schedule);
                            }}
                            class="dropdown-item {$dropdownState.selectedSchedule?.schedule_id === schedule.schedule_id ? 'dropdown-item-selected' : ''}"
                        >
                            <span class="font-medium">{schedule.name}</span>
                        </button>
                    {/each}
                </div>
            </div>
        {/if}
    </div>
</div>