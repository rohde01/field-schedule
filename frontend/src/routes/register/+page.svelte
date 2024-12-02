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
        Email
        <input 
            name="email" 
            type="email" 
            value={form?.email ?? ''} 
            required
        >

    <label>
        Password
        <input 
            name="password" 
            type="password" 
            required
        >
    </label>
        First Name
        <input 
            name="first_name" 
            type="text" 
            value={form?.firstName ?? ''} 
            required
        >
    <label>
        Last Name
        <input 
            name="last_name" 
            type="text" 
            value={form?.lastName ?? ''} 
            required
        >
    </label>
    <button type="submit">Register</button>
    
</form>

<style>
    .error {
        color: red;
        margin-bottom: 1rem;
    }
</style>