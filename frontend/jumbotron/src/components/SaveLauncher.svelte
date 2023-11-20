<script lang="ts">
    import { onMount } from 'svelte';
    import { jumbotronInstance, Jumbotron } from '../classes/Jumbotron';

    let jumbotronState: Jumbotron;

    jumbotronInstance.subscribe(state => {
        jumbotronState = state;
    });

    let savedMatrixes: any[] = [];
    let currentPreviewURL: string = "";

    async function getSavedItems() {
        savedMatrixes = await jumbotronInstance.getSavedItems();
    }

    async function showPreviewHandler(name: string) {
        currentPreviewURL = await jumbotronInstance.getSavedItemPreview(name);
    }

    onMount(async () => {
        await getSavedItems();
        console.log(savedMatrixes);
    });
</script>


<div class="modal-box">
    {#if !currentPreviewURL}
    <h3 class="font-bold text-lg">Previous Items</h3>
    <p class="py-4">Choose an item to activate:</p>
    <div class="grid">
        {#each savedMatrixes as matrix}
            <button class="btn btn-ghost" on:click={() => showPreviewHandler(matrix.filename)}>
                {matrix.filename}
            </button>
        {/each}
    </div>
    <div class="modal-action">
        <form method="dialog">
            <button class="btn">Close</button>
        </form>
    </div>
    {:else}
    <div class="flex flex-col">
        <p>Activate this?</p>
        <img class="m-8" src={currentPreviewURL} alt="Preview"/>
        <div class="modal-action">
            <form method="dialog">
                <button class="btn">Yes</button>
                <button class="btn btn-ghost" on:click={() => currentPreviewURL = ''}>No</button>
            </form>
        </div>
    </div>
    {/if}
</div>

<style>

</style>
