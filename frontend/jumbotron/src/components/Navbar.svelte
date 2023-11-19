<script lang="ts">
    import { jumbotronInstance, Jumbotron } from '../classes/Jumbotron';

    let jumbotronState: Jumbotron;

    jumbotronInstance.subscribe((state) => {
        jumbotronState = state;
    });

    async function disconnect() {
        await jumbotronInstance.disconnect();
    }
</script>

<nav class="absolute w-full left-0 top-0">
    {#if jumbotronState}
        <div class="navbar bg-base-100">
            <div class="navbar-start">
                <p>{jumbotronState.rows} Rows X {jumbotronState.columns} Columns</p>
            </div>
            <div class="navbar-center flex">
                <h2>{jumbotronState.hostname}:{jumbotronState.port}</h2>
            </div>
            <div class="navbar-end">
                <button on:click={disconnect}>Disconnect</button>
            </div>
        </div>
    {/if}
</nav>

<style>
</style>