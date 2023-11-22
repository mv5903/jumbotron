// Jumbotron.ts
import { writable, get } from 'svelte/store';
import { Pixel } from './Pixel';
import io from 'socket.io-client';
export class Jumbotron {
    rows: number = 0;
    columns: number = 0;
    hostname: string = '';
    port: number = 5000;
    isInitialized: boolean = false;
    pixels: Pixel[][] = [[]];
    latency: number = 0;
    fps: number = 0;

    private socket: any;
    private updatesCounter: number = 0;
    private fpsTimer: number | undefined;
    // Create a Svelte store for Jumbotron's state
    private _state = writable({
        rows: 0,
        columns: 0,
        hostname: '',
        port: 5000,
        isInitialized: false,
    } as Jumbotron);

    constructor() {
        this.startFPSCalculation();
    }

    private async startFPSCalculation() {
        this.fpsTimer = window.setInterval(() => {
            this._state.set({
                ...get(this._state),
                fps: this.updatesCounter,
            } as Jumbotron);
            this.updatesCounter = 0;
        }, 1000);
    }

    private static instance: Jumbotron;
    subscribe = this._state.subscribe;

    public static getInstance(): Jumbotron {
        if (!this.instance) {
            this.instance = new Jumbotron();
        }
        return this.instance;
    }

    async attemptConnection(hostname: string, port: number) {
        try {
            const response = await fetch(`http://${hostname}:${port}/jumbotron`);
            const json = await response.json();
            if (json) {
                console.log(json);
                this._state.set({
                    hostname,
                    port,
                    rows: json.rows,
                    columns: json.columns,
                    isInitialized: true,
                } as Jumbotron);
                await this.setupPixels();
            }
            return json !== undefined;
        } catch (e) {
            alert(`Error connecting to Jumbotron: ${e}`);
            return false;
        }
    }

    async disconnect() {
        this._state.set({
            rows: 0,
            columns: 0,
            hostname: '',
            port: 5000,
            isInitialized: false,
        } as Jumbotron);
        this.socket.disconnect();
    }

    async setupPixels() {
        this.pixels = [];
        for (let i = 0; i < this.rows; i++) {
            this.pixels[i] = [];
            for (let j = 0; j < this.columns; j++) {
                this.pixels[i][j] = new Pixel(0, 0, 0, 0, i, j);
            }
        }
        this.updatePixels();
    }

    async updatePixels() {
        let data = get(this._state);
        this.socket = io(`http://${data.hostname}:${data.port}/jumbotron`, { reconnectionAttempts: 5 });

        this.socket.on('array_update', (response: { data: Pixel[][], timestamp: number }) => {
            this.updatesCounter++;
            // Fill in the row and column values for each pixel for easier access in other methods later
            response.data.forEach((row, rowIndex) => row.forEach((pixel, columnIndex) => Object.assign(pixel, { row: rowIndex, column: columnIndex })));
            this.latency = Math.abs((Date.now() - (response.timestamp / 1000000)));
            this.pixels = response.data;
            let old = get(this._state);
            this._state.set({
                ...old,
                pixels: this.pixels, 
                latency: this.latency 
            } as Jumbotron);
        });
    }

    async updateBrightness(brightness: number) {
        let data = get(this._state);
        fetch(`http://${data.hostname}:${data.port}/jumbotron/brightness/${brightness}`, { method: 'POST', headers: { 'Content-Type': 'application/json' } });
    }

    async getBrightness() {
        let data = get(this._state);
        const response = await fetch(`http://${data.hostname}:${data.port}/jumbotron/brightness`);
        const json = await response.json();
        return json.brightness;
    }

    async eraseAll(pixel: Pixel) {
        this.updateAll(pixel, '#000000');
    }
    async erasePixel(pixel: Pixel) {
        let data = get(this._state);
        fetch(`http://${data.hostname}:${data.port}/jumbotron/pixel/${pixel.row}/${pixel.column}/0/0/0/255`);
    }
    async updateAll(pixel: Pixel, color: string) {
        let data = get(this._state);
        let { r, g, b } = Pixel.hexToRgb(color);
        fetch(`http://${data.hostname}:${data.port}/jumbotron/all/${r}/${g}/${b}/${pixel.brightness}`);
    }
    async updateColumn(pixel: Pixel, color: string) {
        let data = get(this._state);
        let { r, g, b } = Pixel.hexToRgb(color);
        fetch(`http://${data.hostname}:${data.port}/jumbotron/column/${pixel.column}/${r}/${g}/${b}/${pixel.brightness}`);
    }
    async updateRow(pixel: Pixel, color: string) {
        let data = get(this._state);
        let { r, g, b } = Pixel.hexToRgb(color);
        fetch(`http://${data.hostname}:${data.port}/jumbotron/row/${pixel.row}/${r}/${g}/${b}/${pixel.brightness}`);
    }
    async updatePixel(pixel: Pixel, color: string) {
        let data = get(this._state);
        let { r, g, b } = Pixel.hexToRgb(color);
        fetch(`http://${data.hostname}:${data.port}/jumbotron/pixel/${pixel.row}/${pixel.column}/${r}/${g}/${b}/${pixel.brightness}`);
    }

    async uploadImage(file: any, brightness: number) {
        if (!file) return;
        let data = get(this._state);

        const formData = new FormData();
        formData.append("file", file);

        // Check if file is video or image
        const isVideo = file.type.startsWith("video");
        if (isVideo) {
            try {
                await fetch(`http://${data.hostname}:${data.port}/jumbotron/playvideo/${brightness}`, {
                    method: "POST",
                    body: formData
                })
            } catch (error) {
                console.error("Error uploading video:", error);
            }
        } else {
            try {
                await fetch(`http://${data.hostname}:${data.port}/jumbotron/upload/${brightness}`, {
                    method: "POST",
                    body: formData
                });
            } catch (error) {
                console.error("Error uploading image:", error);
            }
        }
    };

    async getSavedItems() {
        let data = get(this._state);
        const response = await fetch(`http://${data.hostname}:${data.port}/jumbotron/get_saved_matrices`);
        const json = await response.json();
        return json;
    }

    async getSavedItemPreview(name: string) {
        let data = get(this._state);
        const response = await fetch(`http://${data.hostname}:${data.port}/jumbotron/get_saved_matrix_image/${name}`);
        const blob = await response.blob();
        return URL.createObjectURL(blob);
    }

    async saveCurrent(name: string) {
        let data = get(this._state);
        const response = await fetch(`http://${data.hostname}:${data.port}/jumbotron/save_current_matrix/${name}`, { method: 'POST' });
        return response.ok;
    }

    async activateSavedItem(name: string) {
        let data = get(this._state);
        await fetch(`http://${data.hostname}:${data.port}/jumbotron/activate_saved_matrix/${name}`, { method: 'POST' });
    }

    async deleteSavedItem(name: string) {
        let data = get(this._state);
        await fetch(`http://${data.hostname}:${data.port}/jumbotron/delete_saved_matrix/${name}`, { method: 'DELETE' });
    }

    destroy() {
        if (this.fpsTimer) {
            window.clearInterval(this.fpsTimer);
        }
    }
}

export const jumbotronInstance = Jumbotron.getInstance();