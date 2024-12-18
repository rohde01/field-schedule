<script lang="ts">
    import { schedules } from '$stores/schedules';
    import { dropdownState, toggleDropdown, selectSchedule } from '$stores/ScheduleDropdownState';
    import type { Schedule } from '$lib/schemas/schedule';

    let dropdownContainer: HTMLDivElement;

    function handleSelect(schedule: Schedule) {
        selectSchedule(schedule);
        dropdownState.update(state => ({ ...state, isOpen: false }));
    }

    function handleCreateClick() {
        alert('Schedule creation not implemented yet');
    }
</script>

<div class="fixed bottom-12 left-[max(1rem,calc((100%-80rem)/2+1rem))] z-[9999]" bind:this={dropdownContainer}>
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
            <div class="dropdown-panel absolute z-[9999] w-full bg-white shadow-lg rounded-lg mt-2 py-2 border border-gray-200">
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
                
                <div class="dropdown-divider">
                    <button
                        type="button"
                        class="dropdown-action-button"
                        onclick={(e) => {
                            e.stopPropagation();
                            handleCreateClick();
                        }}
                    >
                        <svg
                            class="w-4 h-4 mr-2"
                            xmlns="http://www.w3.org/2000/svg"
                            viewBox="0 0 20 20"
                            fill="currentColor"
                        >
                            <path fill-rule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clip-rule="evenodd" />
                        </svg>
                        Create New Schedule
                    </button>
                </div>
            </div>
        {/if}
    </div>
</div>