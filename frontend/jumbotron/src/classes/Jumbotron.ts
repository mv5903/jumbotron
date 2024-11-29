import { get, writable } from 'svelte/store';
import { Pixel } from './Pixel';

export class Jumbotron {
    rows: number = 0;
    columns: number = 0;
    hostname: string = '';
    port: number = 5000;
    isInitialized: boolean = false;
    pixels: Pixel[][] = [[]];
    latency: number = 0;
    fps: number = 0;

    private socket: WebSocket | null = null;
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
                this._state.set({
                    hostname,
                    port,
                    rows: json.rows,
                    columns: json.columns,
                    isInitialized: true,
                } as Jumbotron);
                await this.setupPixels();
                this.initializeWebSocket(hostname, port);
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
        if (this.socket) {
            this.socket.close();
        }
    }

    initializeWebSocket(hostname: string, port: number) {
        if (this.socket) {
            this.socket.close();
        }

        const wsUrl = `ws://${hostname}:${port + 1}/jumbotron`;
        this.socket = new WebSocket(wsUrl);

        this.socket.onopen = () => {
            console.log('WebSocket connected');
        };

        this.socket.onmessage = (event) => {
            const response = JSON.parse(event.data);
            this.handleWebSocketMessage(response);
        };

        this.socket.onclose = () => {
            console.log('WebSocket disconnected');
        };

        this.socket.onerror = (error) => {
            console.error('WebSocket error:', error);
        };
    }

    handleWebSocketMessage(response: { data: Pixel[][], timestamp: number }) {
        this.updatesCounter++;
        // Fill in the row and column values for each pixel for easier access in other methods later
        response.data.forEach((row, rowIndex) => row.forEach((pixel, columnIndex) => {
            Object.assign(pixel, { row: rowIndex, column: columnIndex });
        }));

        const newLatency = Math.abs((Date.now() - (response.timestamp / 1000000)));
        const newPixels = response.data;

        const old = get(this._state);

        // Check if the new data or latency is different from the old state before setting it
        if (JSON.stringify(old.pixels) !== JSON.stringify(newPixels) || old.latency !== newLatency) {
            this._state.set({
                ...old,
                pixels: newPixels,
                latency: newLatency
            } as Jumbotron);
        }
    }

    async setupPixels() {
        this.pixels = [];
        for (let i = 0; i < this.rows; i++) {
            this.pixels[i] = [];
            for (let j = 0; j < this.columns; j++) {
                this.pixels[i][j] = new Pixel(0, 0, 0, 0, i, j);
            }
        }
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

    async uploadImage(file: any, brightness: number, progressCallback: (progress: number) => void) {
        if (!file) return;
        let data = get(this._state);
    
        const formData = new FormData();
        formData.append("file", file);
    
        // Create a new XMLHttpRequest object
        const xhr = new XMLHttpRequest();
    
        // Add an event listener to track progress and pass the progress outside
        xhr.upload.addEventListener("progress", (event) => {
            if (event.lengthComputable) {
                const percentComplete = (event.loaded / event.total) * 100;
                // Call the provided callback with the progress value
                progressCallback(percentComplete);
            }
        });
    
        // Handle upload complete or error
        xhr.onreadystatechange = function () {
            if (xhr.readyState === XMLHttpRequest.DONE) {
                if (xhr.status === 200) {
                    console.log("Upload complete!");
                    // Call the progress callback with 100% when done
                    progressCallback(100);
                } else {
                    console.error("Error uploading file:", xhr.responseText);
                    // Handle error, you can also notify the callback if needed
                }
            }
        };
    
        // Determine the correct URL based on the file type
        const isVideo = file.type.startsWith("video");
        const url = isVideo
            ? `http://${data.hostname}:${data.port}/jumbotron/playvideo/${brightness}`
            : `http://${data.hostname}:${data.port}/jumbotron/upload/${brightness}`;
    
        // Open the connection
        xhr.open("POST", url);
    
        // Send the form data
        xhr.send(formData);
    }

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
        await fetch(`http://${data.hostname}:${data.port}/jumbotron/delete_saved_matrix/${name}`, { method: 'POST' });
    }
    
    // Other methods unchanged...

    destroy() {
        if (this.fpsTimer) {
            window.clearInterval(this.fpsTimer);
        }
        if (this.socket) {
            this.socket.close();
        }
    }
}

export const jumbotronInstance = Jumbotron.getInstance();
