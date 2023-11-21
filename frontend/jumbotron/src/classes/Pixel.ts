export class Pixel {
    public r: number;
    public g: number;
    public b: number;
    public brightness: number;
    public row: number;
    public column: number;

    constructor(r: number, g: number, b: number, brightness: number, row: number, column: number) {
        this.r = r;
        this.g = g;
        this.b = b;
        this.brightness = brightness;
        this.row = row;
        this.column = column;
    }

    public static hexToRgb(hex: string) {
        let r = parseInt(hex.substring(1, 3), 16);
        let g = parseInt(hex.substring(3, 5), 16);
        let b = parseInt(hex.substring(5, 7), 16);
        return { r, g, b };
    }
}