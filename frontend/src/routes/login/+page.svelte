<script lang="ts">
    import { enhance } from '$app/forms';
    import { goto } from '$app/navigation';
    import type { ActionData } from './$types';
    
    export let form: ActionData;
</script>

{#if form?.error}
    <p class="error">{form.error}</p>
{/if}

<form 
    method="POST" 
    use:enhance={({ formElement, formData, action, cancel }) => {
        return async ({ result }) => {
            if (result.type === 'redirect') {
                goto(result.location);
            }
        };
    }}
>
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
