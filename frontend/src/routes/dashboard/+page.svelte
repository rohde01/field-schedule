<script lang="ts">
    import type { PageData } from './$types';
    import Dnd from '$lib/components/dnd.svelte';
    export let data: PageData;
</script>

<h1>Welcome, {data.firstName}!</h1>

<div>

</div>
<div>
    <Dnd />
</div>