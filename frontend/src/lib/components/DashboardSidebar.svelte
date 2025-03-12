<script lang="ts">
    import { createEventDispatcher } from 'svelte';
    import { currentView } from '$stores/dashboardNav';
    const dispatch = createEventDispatcher();

    const sidebarItems = [
        {
            group: "Schedule Views",
            items: [
                { name: "Active Schedules", id: "active" },
                { name: "Monthly Calendar", id: "monthly" },
                { name: "Team Schedule", id: "team" }
            ]
        },
        {
            group: "Management",
            items: [
                { name: "Field Settings", id: "fields" },
                { name: "Team Settings", id: "teams" },
                { name: "Time Slots", id: "slots" }
            ]
        }
    ];

    function selectItem(id: string) {
        $currentView = id;
        dispatch('navigationChange', { view: id });
    }
</script>

<div class="sidebar">
    <div class="sidebar-content">
        <div class="bg-white rounded-2xl shadow-xl border border-mint-100 overflow-hidden">
            <div class="flex items-center">
                <div class="flex-1">
                    <h2 class="text-sm font-medium text-sage-700 p-4">Dashboard Navigation</h2>
                </div>
            </div>
            <div class="border-t border-mint-100">
                <div class="p-1 space-y-3">
                    {#each sidebarItems as { group, items }}
                        <div class="space-y-1">
                            <h3 class="text-xs font-medium text-sage-600 px-2">{group}</h3>
                            {#each items as item}
                                <button
                                    class="dropdown-item {$currentView === item.id ? 'dropdown-item-selected' : ''}"
                                    on:click={() => selectItem(item.id)}
                                >
                                    <span class="font-medium">{item.name}</span>
                                </button>
                            {/each}
                        </div>
                    {/each}
                </div>
            </div>
        </div>
    </div>
</div>