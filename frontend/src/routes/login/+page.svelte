<script lang="ts">
    import { enhance } from '$app/forms';
    import { goto } from '$app/navigation';
    import type { ActionData } from './$types';
    import { auth } from '$stores/auth';
    import type { SubmitFunction } from '@sveltejs/kit';
    
    export let form: ActionData;

    const handleSubmit: SubmitFunction = ({ formElement, formData }) => {
        return async ({ result, update }) => {
            if (result.type === 'success' && result.data?.userData) {
                auth.setUser(result.data.userData);
                await goto('/dashboard');
            }
            update();
        };
    }
</script>

{#if form?.error}
    <p class="error">{form.error}</p>
{/if}

<form method="POST" use:enhance={handleSubmit}>
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
