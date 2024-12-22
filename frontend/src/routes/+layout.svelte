<script lang="ts">
    import '../app.css';
    import { setFacilities } from '$stores/facilities';
    import { setFields } from '$stores/fields';

    let { data } = $props();

    $effect(() => {
        if (data.facilities) {
            setFacilities(data.facilities);
        }
    });

    $effect(() => {
        if (data.fields) {
            setFields(data.fields);
        }
    });
</script>

<div class="min-h-screen bg-sage-50 relative">
    <nav class="bg-white border-b border-sage-200 relative z-10">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex justify-between h-16">
                <div class="flex items-center space-x-4">
                    <a href="/" class="nav-link">Home</a>
                    {#if data.user}
                        <a href="/dashboard" class="nav-link">Dashboard</a>
                        <a href="/schedules" class="nav-link">Schedules</a>
                        <a href="/teams" class="nav-link">Teams</a>
                        <a href="/fields" class="nav-link">Fields</a>
                    {/if}
                </div>
                <div class="flex items-center space-x-4">
                    {#if data.user}
                        <form action="/logout" method="POST">
                            <button type="submit" class="btn-secondary">Logout</button>
                        </form>
                    {:else}
                        <a href="/login" class="nav-link">Login</a>
                        <a href="/register" class="btn-primary">Register</a>
                    {/if}
                </div>
            </div>
        </div>
    </nav>

    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 relative">
        <slot />
    </main>
</div>