<script lang="ts">
    import Navbar from "./Navbar.svelte";

    import { jumbotronInstance, Jumbotron } from '../classes/Jumbotron';
    import Matrix from "./Matrix.svelte";

    let jumbotronState: Jumbotron;

    jumbotronInstance.subscribe(state => {
        jumbotronState = state;
    });
</script>

<div>
    <Navbar />
    <div class="w-full flex justify-center">
        <Matrix />
    </div>
</div>

<style>

</style>