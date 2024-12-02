<script lang="ts">
    import '../app.css';
    import type { LayoutData } from './$types';
    export let data: LayoutData;
</script>

<nav>
    <div class="left">
        <a href="/">Home</a>
        {#if data.user}
            <a href="/dashboard">Dashboard</a>
        {/if}
    </div>
    <div class="right">
        {#if data.user}
            <form action="/logout" method="POST">
                <button type="submit">Logout</button>
            </form>
        {:else}
            <a href="/login">Login</a>
            <a href="/register">Register</a>
        {/if}
    </div>
</nav>

<slot />