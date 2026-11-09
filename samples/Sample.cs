// Preview file: C#
using System;
using System.Collections.Generic;
using System.Linq;

namespace Preview;

public enum Flag { Green, Yellow, Red }

public record Lap(int Number, double Time);

public class Tracker
{
    private readonly List<Lap> _laps = new();
    public const int MaxLaps = 161;

    public void Add(Lap lap) => _laps.Add(lap);

    public double Best() => _laps.Count == 0 ? 0 : _laps.Min(l => l.Time);

    [Obsolete("Use Best()")]
    public double Fastest() => Best();

    public static void Main()
    {
        var t = new Tracker();
        t.Add(new Lap(1, 128.4));
        Console.WriteLine($"Best: {t.Best():F2}s, flag: {Flag.Green}");
    }
}
