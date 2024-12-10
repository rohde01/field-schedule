<script lang="ts">
    import '../app.css';
    import type { LayoutData } from './$types';
    export let data: LayoutData;
</script>

<div class="min-h-screen bg-sage-50 relative">
    <nav class="bg-white border-b border-sage-200 relative z-10">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex justify-between h-16">
                <div class="flex items-center space-x-4">
                    <a href="/" class="nav-link">Home</a>
                    {#if data.user}
                        <a href="/dashboard" class="nav-link">Dashboard</a>
                        <a href="/club" class="nav-link">My Club</a>
                        <a href="/teams" class="nav-link">Teams</a>
                        <a href="/facilities" class="nav-link">Facilities</a>
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