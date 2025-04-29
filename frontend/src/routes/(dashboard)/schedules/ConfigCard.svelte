<script lang="ts">
    import { Card, Toggle, GradientButton,  } from 'flowbite-svelte';
    import { WandMagicSparklesOutline} from 'flowbite-svelte-icons';

</script>
  
<Card size="xl" class="mb-4 h-[24rem] w-full p-4 2xl:col-span-2 flex flex-col">
    <h3 class="text-l font-medium text-gray-900 dark:text-white mb-4">
        Model settings
    </h3>
    <Toggle color=purple checked={true} class="mb-6">Fair weekdays</Toggle>

    <Toggle color=purple disabled checked={false}>Shared fields</Toggle>

    <GradientButton outline color="purpleToBlue" class="mt-auto">
        <WandMagicSparklesOutline class="mr-2 h-5 w-5" />
        Generate
    </GradientButton>

</Card>