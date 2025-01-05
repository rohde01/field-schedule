<script lang="ts">
    import type { PageData } from './$types';

    export let data: PageData;
    
    const { user } = data;
</script>

<h1>Welcome, {user.first_name ?? 'User'}!</h1>