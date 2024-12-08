<script lang="ts">
    import { createEventDispatcher } from 'svelte';
    import type { FieldAvailability as CreateFieldAvailability } from '$lib/types/field';

    export let availabilities: CreateFieldAvailability[] = [];
    const dispatch = createEventDispatcher<{ availabilitiesChange: CreateFieldAvailability[] }>();

    const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'] as const;

    function addAvailability() {
        availabilities = [...availabilities, {
            day_of_week: 'Mon',
            start_time: '16:00',
            end_time: '22:00'
        }];
        dispatch('availabilitiesChange', availabilities);
    }

    function removeAvailability(index: number) {
        availabilities = availabilities.filter((_, i) => i !== index);
        dispatch('availabilitiesChange', availabilities);
    }

    function handleAvailabilityChange() {
        dispatch('availabilitiesChange', availabilities);
    }
</script>

<div class="field-section">
    <h3 class="field-subtitle">Field Availability</h3>
    <div class="space-y-4">
        {#each availabilities as availability, i}
            <div class="flex gap-2 items-center">
                <select
                    bind:value={availability.day_of_week}
                    class="form-input-sm bg-white [&>option:hover]:bg-mint-100 [&>option:checked]:bg-mint-500 [&>option:checked]:text-white"
                    on:change={handleAvailabilityChange}
                >
                    {#each days as day}
                        <option value={day}>{day}</option>
                    {/each}
                </select>

                <input
                    type="time"
                    bind:value={availability.start_time}
                    class="form-input-sm [&::-webkit-calendar-picker-indicator]:filter-mint"
                    on:change={handleAvailabilityChange}
                />

                <input
                    type="time"
                    bind:value={availability.end_time}
                    class="form-input-sm [&::-webkit-calendar-picker-indicator]:filter-mint"
                    on:change={handleAvailabilityChange}
                />

                <button
                    type="button"
                    class="text-sage-500 hover:text-sage-700 transition-colors duration-200"
                    on:click={() => removeAvailability(i)}
                    aria-label="Remove availability"
                >
                    <!-- Remove icon -->
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-5 h-5">
                        <path d="M6.28 5.22a.75.75 0 00-1.06 1.06L8.94 10l-3.72 3.72a.75.75 0 101.06 1.06L10 11.06l3.72 3.72a.75.75 0 101.06-1.06L11.06 10l3.72-3.72a.75.75 0 00-1.06-1.06L10 8.94 6.28 5.22z" />
                    </svg>
                </button>
            </div>
        {/each}
        
        <button
            type="button"
            class="text-xs px-2 py-1 bg-white text-mint-600 rounded-lg hover:bg-mint-50 transition-colors border border-mint-200"
            on:click={addAvailability}
        >
            Add Availability
        </button>
    </div>
</div>
