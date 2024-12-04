<script lang="ts">
    import { enhance } from '$app/forms';
    import type { ActionData } from './$types';
    export let form: ActionData;
    
    let submitting = false;
</script>

<h1>Give your club a name to get started! </h1>

<form 
    method="POST" 
    use:enhance={() => {
        submitting = true;
        return async ({ update }) => {
            await update();
            submitting = false;
        };
    }}
>
    <div>
        <label for="name">Club Name:</label>
        <input type="text" id="name" name="name" required disabled={submitting} />
        {#if form?.error}
            <p class="error">{form.error}</p>
        {/if}
    </div>
    <button type="submit" disabled={submitting}>
        {submitting ? 'Creating...' : "Let's do it"}
    </button>
</form>

<style>
    .error {
        color: red;
    }
</style>
