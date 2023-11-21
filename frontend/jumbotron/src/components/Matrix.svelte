<script lang="ts">
    import { onMount } from 'svelte';
    import { jumbotronInstance, Jumbotron } from '../classes/Jumbotron';
    import { EditMode } from '../classes/EditMode';
    import FaPencilAlt from 'svelte-icons/fa/FaPencilAlt.svelte';
    import FaArrowsAltH from 'svelte-icons/fa/FaArrowsAltH.svelte';
    import FaArrowsAltV from 'svelte-icons/fa/FaArrowsAltV.svelte';
    import FaBorderAll from 'svelte-icons/fa/FaBorderAll.svelte';
    import FaEraser from 'svelte-icons/fa/FaEraser.svelte';
    import type { Pixel } from '../classes/Pixel';
    import SaveLauncher from './SaveLauncher.svelte';

    let jumbotronState: Jumbotron;

    jumbotronInstance.subscribe(state => {
        jumbotronState = state;
    });

    // States
    let editMode: EditMode = EditMode.PIXEL;
    let brightness = 0;
    let color = '#000000';
    let file = null as File | null;
    let showDebug = true;

    onMount(async () => {
        brightness = await jumbotronInstance.getBrightness();
    });

    function processToolInput(pixel: Pixel, event: KeyboardEvent | MouseEvent) {
        // Svelte requires keyboard events to be handles with a click handler, but I don't care
        if (event instanceof KeyboardEvent) return;
        switch (editMode) {
            case EditMode.PIXEL:
                jumbotronInstance.updatePixel(pixel, color);
                break;
            case EditMode.ROW:
                jumbotronInstance.updateRow(pixel, color);
                break;
            case EditMode.COLUMN:
                jumbotronInstance.updateColumn(pixel, color);
                break;
            case EditMode.ALL:
                jumbotronInstance.updateAll(pixel, color);
                break;
            case EditMode.ERASER:
                jumbotronInstance.erasePixel(pixel);
                break;
        }
    }

    function eraseAllHandler() {
        if (!confirm('Are you sure you want to erase all pixels?')) return;
        jumbotronInstance.eraseAll(jumbotronInstance.pixels[0][0]);
    }

    function onFileChange(event: Event) {
        const target = event.target as HTMLInputElement;
        if (target && target.files && target.files.length > 0) {
            file = target.files[0];
        }
    }

    function handleFileUpload() {
        if (!file) return;
        jumbotronInstance.uploadImage(file, brightness);
    }

    function saveLauncherHandler() {
        const saveLauncher = document.getElementById('saveLauncher');
        if (saveLauncher) {
            try {
                // Typescript being typescript :)
                (saveLauncher as unknown as SaveLauncher).showModal();
            } catch (e) {
                console.error(e);
            }
        }
    }

    async function saveCurrentHandler() {
        let name = prompt('Enter a name for this matrix');
        if (!name) return;
        if (await jumbotronInstance.saveCurrent(name)) {
            alert('Saved!');
        } else {
            alert('Failed to save!');
        }
    }
</script>

{#if !jumbotronState.isInitialized}
    <p>Loading...</p>
{:else if jumbotronState.isInitialized && Array.isArray(jumbotronState.pixels)}
    <div class="absolute card m-4 left-0 top-[14vh] bg-base-300" >
        <h2 class="text-2xl">Edit Jumbotron</h2>
        <h2>Edit Directly</h2>
        <div class="join join-horizontal mt-4 text-sm shadow-md">
            <button class={`btn tooltip join-item ${editMode == EditMode.PIXEL && 'btn-primary'}`} data-tip="Pencil" on:click={() => editMode = EditMode.PIXEL} style="borderRadius: 'revert'"><FaPencilAlt /></button>
            <button class={`btn tooltip join-item ${editMode == EditMode.ROW && 'btn-primary'}`} data-tip="Row" on:click={() => editMode = EditMode.ROW} style="borderRadius: 'revert'"><FaArrowsAltH /></button>
            <button class={`btn tooltip join-item ${editMode == EditMode.COLUMN && 'btn-primary'}`} data-tip="Column" on:click={() => editMode = EditMode.COLUMN} style="borderRadius: 'revert'"><FaArrowsAltV /></button>
            <button class={`btn tooltip join-item ${editMode == EditMode.ALL && 'btn-primary'}`} data-tip="All" on:click={() => editMode = EditMode.ALL} style="borderRadius: 'revert'"><FaBorderAll /></button>
            <button class={`btn tooltip join-item ${editMode == EditMode.ERASER && 'btn-primary'}`} data-tip="Erase" on:click={() => editMode = EditMode.ERASER} style="borderRadius: 'revert'"><FaEraser /></button>
        </div>
        <div class="flex justify-between mt-8">
            <h2>Color</h2>
            <input type="color" bind:value={color}  />
        </div>
        <div class="flex justify-between mt-2">
            <h2>Brightness</h2>
            <div class="flex">
                <p>0</p>
                <div class="tooltip" data-tip={brightness}>
                    <input type="range" min={0} max="40" bind:value={brightness} on:change={e => jumbotronInstance.updateBrightness(brightness)} class="range w-32 mx-2" />
                </div>
                <p>40</p>
            </div>
        </div> 
        <div class="divider">OR</div>
        <div class="my-4">
            <h2>Upload Image/Video</h2>
            <div class="flex flex-col gap-2 justify-center place-items-center">
                <input 
                    type="file" 
                    accept="image/*, video/*"
                    class="file-input file-input-bordered file-input-xs w-full max-w-xs text-sm my-3"
                    on:change={onFileChange}
                />
                <button class="btn btn-outline btn-info" on:click={handleFileUpload}>Send</button>
            </div>
        </div>
        <div class="divider">OR</div>
        <div class="flex justify-around">
            <div>
                <h2 class="text-warning">Save</h2>
                <div>
                    <button class="btn btn-outline btn-warning mt-2" on:click={saveCurrentHandler}>Save</button>
                </div>
            </div>
            <div>
                <h2 class="text-success">Previous</h2>
                <div>
                    <button class="btn btn-outline btn-success mt-2" on:click={saveLauncherHandler}>View Previous</button>
                    <dialog id="saveLauncher" class="modal modal-bottom sm:modal-middle">
                        <SaveLauncher />
                    </dialog>
                </div>
            </div>
        </div>
    </div>
    <div class="grid gap-1 w-[60vw] ms-72" style={`grid-template-columns: repeat(${jumbotronState.columns}, minmax(0, 1fr)); grid-template-rows: repeat(${jumbotronState.rows}, minmax(0, 1fr));`}>
        {#each jumbotronState.pixels as row, rowIndex}
            {#each row as pixel, columnIndex}
            <div class="tooltip tooltip-top" data-tip={pixel.brightness}>
                <div class="w-2 h-2 border-red-500" on:click={e => processToolInput(pixel, e)} on:keydown={e => processToolInput(pixel, e)} role="button" tabindex={rowIndex * columnIndex} style={`background-color: rgb(${pixel.r}, ${pixel.g}, ${pixel.b}); opacity: ${pixel.brightness / 40}`}></div>
            </div>
            {/each}
        {/each}
    </div>
    <div class="absolute top-2 left-[65vw] h-[6vh] flex gap-4 place-items-center">
        <div class="flex gap-2">
            <p>Debug Info</p>
            <input type="checkbox" class="toggle" bind:checked={showDebug} />
        </div>
        {#if showDebug}
        <div>
            <div class="flex gap-2">
                <p>Latency: </p>
                <p>{jumbotronState.latency.toFixed(0)}ms</p>
            </div>
            <div class="flex gap-2">
                <p>FPS: </p>
                <p>{jumbotronState.fps}</p>
            </div>
        </div>
        {/if}
    </div>
    
{/if}

<style>

</style>