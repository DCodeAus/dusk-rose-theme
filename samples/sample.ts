// Preview file: TypeScript / JavaScript
interface Lap { number: number; time: number; pit?: boolean }

export class Tracker<T extends Lap> {
  private readonly laps: T[] = [];
  constructor(public readonly name: string) {}

  add(lap: T): this {
    this.laps.push(lap);
    return this;
  }

  get best(): number {
    return Math.min(...this.laps.map((l) => l.time));
  }
}

const t = new Tracker<Lap>("Bathurst").add({ number: 1, time: 128.4, pit: false });
console.log(`best: ${t.best.toFixed(2)}s`, /^\d+$/.test("42"), null, undefined);
