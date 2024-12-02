<script lang="ts">
    import type { ActionData } from './$types';
    
    export let form: ActionData;
</script>

{#if form?.error}
    <p class="error">{form.error}</p>
{/if}

<form method="POST">
    <label>
        Username
        <input 
            name="username" 
            type="text" 
            value={form?.username ?? ''} 
            required
        >
    </label>
    
    <label>
        Password
        <input 
            name="password" 
            type="password" 
            required
        >
    </label>
    <button type="submit">Log in</button>
</form>

<style>
    .error {
        color: red;
        margin-bottom: 1rem;
    }
</style>
