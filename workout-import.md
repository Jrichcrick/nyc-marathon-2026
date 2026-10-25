# How the native workouts were added

Both **NYC 3:57** and **3 mi Watch Rehearsal** were added successfully on Oct 25. Fitness displayed **Workout Added to Watch** after each import. Do not import them again unless you need to restore them.

## Repeat the iPhone import

1. Open the appropriate link in Safari on your iPhone:
   - [NYC 3:57](https://jrichcrick.github.io/nyc-marathon-2026/workouts/NYC-3-57.workout)
   - [3 mi Watch Rehearsal](https://jrichcrick.github.io/nyc-marathon-2026/workouts/3-mi-Watch-Rehearsal.workout)
2. Tap **Download** when Safari asks.
3. Tap Safari's page menu beside the address bar, then **Downloads**.
4. Tap the downloaded `.workout` file. The Fitness icon should appear beside it.
5. Fitness opens a preview headed **Add NYC 3:57** or **Add 3 mi Watch Rehearsal**. Check the steps, then tap **Add to Apple Watch**.
6. Wait for **Workout Added to Watch**, then tap **Done**.
7. On the Watch, find the workout under **Workout → Outdoor Run → Goals → Custom**, or in its Outdoor Run workout list. Do not start a run merely to import the file.

Keep the Watch unlocked near the paired iPhone during import. Wearing it is fine. Adding a plan does not start a workout or delete run history. Re-importing the same file may report an existing workout or create a duplicate; check before importing again.

## What was generated

**NYC 3:57:** Outdoor Run, 26 one-mile Work steps plus an Open finish, no warmup/cooldown and no per-step target alerts. Every mile name contains its pace guide and the cumulative BY time at the end of that mile. The final budget is 3:58:28 on the real course, including a 10:00 Queensboro mile. This is not an alert-only guarantee.

**3 mi Watch Rehearsal:** three one-mile Work steps, all easy, no targets or warmup/cooldown. Test the transition cue, readable names and metric screen on Tuesday Oct 27. End at three miles.

The BY time belongs to the end of the **named mile**. A transition can display the upcoming step; check its mile number. Watch miles may not match official flags. The workout does not automatically forecast your finish or alert on cumulative lateness.

## How the files were built on the Mac

The Mac's installed Apple WorkoutKit framework was used directly; no third-party encoder or iPhone app was installed. Swift created `WorkoutStep`, `IntervalStep`, `IntervalBlock`, `CustomWorkout` and `WorkoutPlan` objects, wrote `WorkoutPlan.dataRepresentation`, then read the bytes with `WorkoutPlan(from:)` and compared all settings. Both round trips passed. The step names and distances were also visible in Fitness's native import previews.

The source is `build_workout.swift`. Run it on a compatible Mac with Apple's Swift tools and WorkoutKit:

```sh
swift -module-cache-path ./swift-cache build_workout.swift ./generated
```

It creates both `.workout` files and a JSON specification. The files were committed to the marathon repo and downloaded from GitHub Pages. A local Mac file can also be transferred to your iPhone and opened in Fitness; only the Safari Downloads route was verified in this session.

Apple references: [WorkoutPlan](https://developer.apple.com/documentation/workoutkit/workoutplan), [CustomWorkout](https://developer.apple.com/documentation/workoutkit/customworkout), [Up Next workout view](https://support.apple.com/guide/watch/create-a-custom-workout-apd66fcd5c5c/watchos).
