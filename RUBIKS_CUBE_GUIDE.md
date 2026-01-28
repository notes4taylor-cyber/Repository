# The Ultimate Idiot-Proof Rubik's Cube Guide

## Table of Contents
1. [Understanding Your Cube](#understanding-your-cube)
2. [The Notation System](#the-notation-system)
3. [Step 1: White Cross](#step-1-white-cross)
4. [Step 2: White Corners](#step-2-white-corners)
5. [Step 3: Middle Layer](#step-3-middle-layer)
6. [Step 4: Yellow Cross](#step-4-yellow-cross)
7. [Step 5: Yellow Edges](#step-5-yellow-edges)
8. [Step 6: Position Yellow Corners](#step-6-position-yellow-corners)
9. [Step 7: Orient Yellow Corners](#step-7-orient-yellow-corners)
10. [Troubleshooting](#troubleshooting)

---

## Understanding Your Cube

### The Cube Has 3 Types of Pieces

```
    CENTERS (6 pieces)           EDGES (12 pieces)          CORNERS (8 pieces)
    They NEVER move!             Have 2 colors              Have 3 colors

        ┌───┐                       ┌───┐                     ┌───────┐
        │ ● │                       │▀▀▀│                     │▀▀▀▀▀▀▀│
        └───┘                       └───┘                     │▀▀   ▀▀│
    Fixed reference point      Can flip 2 ways            Can twist 3 ways
```

### How to Hold Your Cube
```
                    ┌──────────────┐
                    │              │
                    │   YELLOW     │   ← TOP (U = Up)
                    │   (target)   │
                    │              │
     ┌──────────────┼──────────────┼──────────────┬──────────────┐
     │              │              │              │              │
     │    ORANGE    │    GREEN     │     RED      │    BLUE      │
     │    (Left)    │   (Front)    │   (Right)    │    (Back)    │
     │              │              │              │              │
     └──────────────┼──────────────┼──────────────┴──────────────┘
                    │              │
                    │    WHITE     │   ← BOTTOM (D = Down)
                    │   (start)    │
                    │              │
                    └──────────────┘

Standard Color Scheme:
• White opposite Yellow
• Green opposite Blue
• Red opposite Orange
```

---

## The Notation System

### The 6 Basic Moves

Each letter means "turn that face 90° CLOCKWISE (as if you're looking at it)"

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  MOVE  │  MEANING              │  VISUAL                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│   R    │  Right face clockwise │     ┌───┐         Turn the right          │
│        │                       │     │ ↻ │ ←──     face CLOCKWISE           │
│        │                       │     └───┘                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│   R'   │  Right COUNTER-clock  │     ┌───┐         The ' means              │
│        │  (R-prime)            │     │ ↺ │ ←──     COUNTER-clockwise        │
│        │                       │     └───┘                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│   L    │  Left face clockwise  │  ──→ ┌───┐        Looking AT the           │
│        │                       │      │ ↻ │        left face                │
│        │                       │      └───┘                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│   U    │  Top (Up) clockwise   │      ┌───┐ ↻      Looking DOWN             │
│        │                       │      │   │        at top                   │
│        │                       │      └───┘                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│   D    │  Bottom clockwise     │      ┌───┐        Looking UP               │
│        │                       │      │   │ ↻      at bottom                │
│        │                       │      └───┘                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│   F    │  Front face clockwise │      ┌───┐        The face                 │
│        │                       │      │ ↻ │        facing YOU               │
│        │                       │      └───┘                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│   B    │  Back face clockwise  │      ┌───┐        The face                 │
│        │                       │      │ ↻ │        AWAY from you            │
│        │                       │      └───┘                                 │
└─────────────────────────────────────────────────────────────────────────────┘

SPECIAL NOTATION:
• R2 = Turn R twice (180°) - same result either direction
• x, y, z = Rotate the ENTIRE cube (not used in this guide)
```

### Practice Exercise
Before starting, practice these moves 10 times each:
1. Do R, then R' - cube should look the same
2. Do U, U, U, U - cube should look the same (full rotation)
3. Do R2, R2 - cube should look the same

---

## Step 1: White Cross

**GOAL:** Make a white cross on the bottom with edges matching center colors

```
        WHAT YOU'RE BUILDING:

             ┌───┬───┬───┐
             │   │ G │   │   ← Green edge matches
             ├───┼───┼───┤      green center
             │ O │ W │ R │   ← Orange and Red edges match
             ├───┼───┼───┤      their centers
             │   │ B │   │   ← Blue edge matches
             └───┴───┴───┘      blue center

        This goes on the BOTTOM, but work with WHITE facing UP first!
```

### The Strategy: Work with white on TOP, then flip the cube

#### Case 1: White edge on top layer (easiest!)
```
If you see this:              Do this:
    ┌───┬───┬───┐
    │   │ W │   │             Just turn U until the OTHER color
    ├───┼───┼───┤             matches the center below it, then
    │   │ Y │   │             turn that face twice (F2, R2, etc.)
    └───┴───┴───┘
         ↓
    ┌───┬───┬───┐
    │   │ G │   │   ← Green matches green center
    ├───┼───┼───┤
    │   │ G │   │
    └───┴───┴───┘
    Then do: F2 (to put it on bottom)
```

#### Case 2: White edge in middle layer
```
If you see this:              Do this:
         ┌───┐
    ─────│ W │────            Turn that face once to bring
         │ G │                the white to the top layer,
         └───┘                then solve like Case 1

    Example: If white-green edge is on the right side,
    do R to bring white to top, then solve normally.
```

#### Case 3: White edge on bottom (wrong spot or flipped)
```
If white edge is on bottom but wrong:

    Turn that face twice to bring it to top,
    then solve like Case 1

    Example: F2 brings front-bottom edge to front-top
```

### Checklist Before Moving On:
```
    ✓ White cross on bottom
    ✓ Looking at GREEN side: green edge next to green center
    ✓ Looking at RED side: red edge next to red center
    ✓ Looking at BLUE side: blue edge next to blue center
    ✓ Looking at ORANGE side: orange edge next to orange center

              GREEN
               ↓
         ┌───┬───┬───┐
         │   │ G │   │
    O ←  ├───┼───┼───┤  → R
         │   │ W │   │
         └───┴───┴───┘
               ↑
              BLUE
```

---

## Step 2: White Corners

**GOAL:** Complete the white face with all corners in correct positions

```
        WHAT YOU'RE BUILDING:

             ┌───┬───┬───┐
             │ W │ W │ W │
             ├───┼───┼───┤
             │ W │ W │ W │
             ├───┼───┼───┤
             │ W │ W │ W │
             └───┴───┴───┘

        With matching colors on the sides!
```

### The Magic Algorithm: R U R' U'

**This is called "Sexy Move" - memorize it!**

```
    R    U    R'   U'
    ↓    ↓    ↓    ↓
   Right Up  Right' Up'
   clock clock counter counter
```

### How to Use It:

#### Step A: Find a white corner in the top layer
```
Look for corners with white on them in the top layer:

    ┌───┬───┬───┐
    │ ? │   │ ? │  ← Check these 4 corners
    ├───┼───┼───┤     for white stickers
    │   │   │   │
    ├───┼───┼───┤
    │ ? │   │ ? │
    └───┴───┴───┘
```

#### Step B: Position it above its home
```
The corner with WHITE, GREEN, and RED belongs here:

              ┌─── This corner (where green, red, and white meet)
              ↓
         ┌───┬───┬───┐
         │   │   │ ◆ │
         ├───┼───┼───┤     GREEN FACE
         │   │ G │   │        │
         ├───┼───┼───┤        ▼
         │   │   │   │     ┌───┐
         └───┴───┴───┘     │ R │ ← RED FACE
                           └───┘

Turn U until the corner is directly above where it belongs.
```

#### Step C: Apply algorithm based on where white is facing

```
CASE 1: White facing RIGHT          CASE 2: White facing FRONT
        ┌───┐                               ┌───┐
        │   │                               │   │
    ┌───┼───┤                           ┌───┼───┤
    │   │░W░│ ← White here              │░W░│   │ ← White here
    └───┴───┘                           └───┴───┘

    Do: R U R' U'                       Do: F' U' F U
    (1 time might not be enough,        (or just do R U R' U'
     repeat up to 5 times!)              multiple times - it works!)


CASE 3: White facing UP
        ┌───┐
        │░W░│ ← White on top
    ┌───┼───┤
    │   │   │
    └───┴───┘

    Do: R U R' U' (repeat until solved - takes 3-5 times)
```

### THE FOOLPROOF METHOD:
**Just keep doing R U R' U' until the corner is solved!**
(Maximum 5 times needed)

### What if the corner is in the bottom layer but wrong?
```
Put that corner in the front-right position, then do:
R U R' U'

This will pop it out to the top layer.
Then solve it normally!
```

### Checklist Before Moving On:
```
    ✓ Entire white face complete
    ✓ First layer colors all match:

    Looking at front:    Looking at right:    Looking at back:
    ┌───┬───┬───┐       ┌───┬───┬───┐       ┌───┬───┬───┐
    │ G │   │   │       │ R │   │   │       │ B │   │   │
    ├───┼───┼───┤       ├───┼───┼───┤       ├───┼───┼───┤
    │ G │ G │   │       │ R │ R │   │       │ B │ B │   │
    ├───┼───┼───┤       ├───┼───┼───┤       ├───┼───┼───┤
    │ G │ G │ G │       │ R │ R │ R │       │ B │ B │ B │
    └───┴───┴───┘       └───┴───┴───┘       └───┴───┴───┘
```

---

## Step 3: Middle Layer

**GOAL:** Solve the middle layer edges

```
    BEFORE:                          AFTER:
    ┌───┬───┬───┐                   ┌───┬───┬───┐
    │   │   │   │ Top layer         │   │   │   │
    ├───┼───┼───┤                   ├───┼───┼───┤
    │   │   │   │ Middle ← SOLVE    │ G │ G │ G │ ← All matching!
    ├───┼───┼───┤          THIS     ├───┼───┼───┤
    │ G │ G │ G │ Bottom (done)     │ G │ G │ G │
    └───┴───┴───┘                   └───┴───┴───┘
```

### Find an Edge in the Top Layer (without yellow!)
```
Look for edges in the top layer that DON'T have yellow:

         ┌───┬───┬───┐
         │   │ ? │   │  ← Check these 4 edges
         ├───┼───┼───┤
         │ ? │   │ ? │
         ├───┼───┼───┤
         │   │ ? │   │
         └───┴───┴───┘

If the edge has yellow, skip it - it belongs in the last layer.
```

### The Two Algorithms

#### LEFT Algorithm: U' L' U L U F U' F'
**"Go LEFT"** - Use when edge needs to go LEFT

```
When edge needs to go to the LEFT:

         ┌───┐
         │ R │ ← This needs to go LEFT to red center
    ┌────┼───┤
    │ O  │ G │ ← This G is on the green center ✓
    └────┴───┘

    ALGORITHM (say it out loud):
    "Up-prime, Left-prime, Up, Left, Up, Front, Up-prime, Front-prime"

     U'    L'    U    L    U    F    U'   F'
```

#### RIGHT Algorithm: U R U' R' U' F' U F
**"Go RIGHT"** - Use when edge needs to go RIGHT

```
When edge needs to go to the RIGHT:

         ┌───┐
         │ O │ ← This needs to go RIGHT to orange center
    ┌────┼───┼────┐
    │    │ G │ R  │ ← This G is on the green center ✓
    └────┴───┴────┘

    ALGORITHM (say it out loud):
    "Up, Right, Up-prime, Right-prime, Up-prime, Front-prime, Up, Front"

     U    R    U'   R'   U'   F'   U    F
```

### Step-by-Step Process:

```
1. FLIP YOUR CUBE so yellow is on TOP (white on bottom)

2. Find a non-yellow edge in the top layer

3. Turn U until that edge's FRONT color matches the center

   Example:
         ┌───┐
         │ R │ ← Red on top of edge
    ┌────┼───┤
    │    │ G │ ← GREEN matches GREEN center ✓
    └────┴───┘

4. Look at the TOP color of that edge:
   • If it matches LEFT center → do LEFT algorithm
   • If it matches RIGHT center → do RIGHT algorithm

5. Repeat for all 4 middle edges
```

### What if an edge is in the middle layer but wrong?

```
Just put any top-layer edge (with yellow if needed) into
that spot using either algorithm.

The wrong edge will pop out to the top layer,
then you can solve it correctly!
```

### Memory Trick for the Algorithms:
```
LEFT algorithm:  U' L' U L  | U F U' F'
                 └────┬───┘   └────┬───┘
                 "Lefty"      "Finish"

RIGHT algorithm: U R U' R'  | U' F' U F
                 └────┬───┘   └────┬───┘
                 "Righty"     "Finish"
```

---

## Step 4: Yellow Cross

**GOAL:** Make a yellow cross on top (ignore corners for now)

```
    BEFORE (one of these):          AFTER:

    Dot:         L-shape:      Line:         CROSS:
    ┌───┬───┬───┐ ┌───┬───┬───┐ ┌───┬───┬───┐ ┌───┬───┬───┐
    │   │   │   │ │   │ Y │   │ │   │ Y │   │ │   │ Y │   │
    ├───┼───┼───┤ ├───┼───┼───┤ ├───┼───┼───┤ ├───┼───┼───┤
    │   │ Y │   │ │ Y │ Y │   │ │ Y │ Y │ Y │ │ Y │ Y │ Y │
    ├───┼───┼───┤ ├───┼───┼───┤ ├───┼───┼───┤ ├───┼───┼───┤
    │   │   │   │ │   │   │   │ │   │   │   │ │   │ Y │   │
    └───┴───┴───┘ └───┴───┴───┘ └───┴───┴───┘ └───┴───┴───┘
```

### The Algorithm: F R U R' U' F'

```
    F    R    U    R'   U'   F'

    Say: "Front, Right, Up, Right-prime, Up-prime, Front-prime"

    Or: "Fru Ruf" (sounds like "froo roof")
```

### How Many Times to Apply:

```
┌─────────────────────────────────────────────────────────────────────────┐
│  STARTING PATTERN      │  HOLD IT LIKE THIS     │  TIMES TO APPLY      │
├─────────────────────────────────────────────────────────────────────────┤
│                        │                        │                      │
│  DOT (no edges)        │  Any orientation       │  Apply 3 times       │
│      ┌───┐             │                        │                      │
│      │ Y │             │                        │                      │
│      └───┘             │                        │                      │
│                        │                        │                      │
├─────────────────────────────────────────────────────────────────────────┤
│                        │                        │                      │
│  L-SHAPE               │  L in BACK-LEFT:       │  Apply 2 times       │
│    ┌───┐               │    ┌───┬───┬───┐       │                      │
│    │ Y │               │    │   │ Y │   │       │                      │
│  ┌─┴───┘               │    ├───┼───┼───┤       │                      │
│  │ Y │ Y │             │    │ Y │ Y │   │       │                      │
│  └───┘                 │    └───┴───┴───┘       │                      │
│                        │   (9 o'clock position) │                      │
│                        │                        │                      │
├─────────────────────────────────────────────────────────────────────────┤
│                        │                        │                      │
│  LINE (horizontal)     │  Line HORIZONTAL:      │  Apply 1 time        │
│                        │    ┌───┬───┬───┐       │                      │
│  ───Y─Y─Y───           │    │   │   │   │       │                      │
│                        │    ├───┼───┼───┤       │                      │
│                        │    │ Y │ Y │ Y │       │                      │
│                        │    ├───┼───┼───┤       │                      │
│                        │    │   │   │   │       │                      │
│                        │    └───┴───┴───┘       │                      │
│                        │                        │                      │
└─────────────────────────────────────────────────────────────────────────┘
```

### Visual Pattern Progression:
```
    DOT ──algorithm──→ L-SHAPE ──algorithm──→ LINE ──algorithm──→ CROSS

    (Make sure to orient L-shape and LINE correctly before applying!)
```

---

## Step 5: Yellow Edges

**GOAL:** Get yellow edges to match their center colors

```
    BEFORE:                         AFTER:
    Yellow cross done,              Yellow cross with
    but edges don't match           all edges matching!

        ┌───┐                           ┌───┐
        │ B │ (wrong!)                  │ G │ ← Matches green!
    ┌───┼───┼───┐                   ┌───┼───┼───┐
    │ G │ Y │ O │                   │ O │ Y │ R │
    └───┼───┼───┘                   └───┼───┼───┘
        │ R │                           │ B │ ← Matches blue!
        └───┘                           └───┘
```

### The Algorithm: R U R' U R U2 R'

```
    R    U    R'   U    R    U2   R'

    Say: "Right, Up, Right-prime, Up, Right, Up-two, Right-prime"
```

### The Process:

```
1. Turn U until AT LEAST ONE edge matches its center
   (You might get lucky and get 2 or even all 4!)

2. Check how many edges match:
```

#### If ALL 4 match: You're done with this step!

#### If 2 ADJACENT edges match (next to each other):
```
                    ┌───┐
                    │ ✓ │ ← matches
                ┌───┼───┼───┐
   matches → ✓  │   │ Y │   │  ✗ ← doesn't match
                └───┼───┼───┘
                    │ ✗ │ ← doesn't match
                    └───┘

    Hold cube so SOLVED edges are in BACK and LEFT
    (unsolved edges face FRONT and RIGHT)

    Then apply: R U R' U R U2 R'
```

#### If 2 OPPOSITE edges match (across from each other):
```
                    ┌───┐
                    │ ✓ │ ← matches
                ┌───┼───┼───┐
   doesn't  →   │ ✗ │ Y │ ✗ │  ← doesn't match
   match        └───┼───┼───┘
                    │ ✓ │ ← matches
                    └───┘

    Hold cube so one SOLVED edge is in BACK

    Apply algorithm TWICE:
    R U R' U R U2 R'
    (then U to align)
    R U R' U R U2 R'
```

---

## Step 6: Position Yellow Corners

**GOAL:** Get all yellow corners in correct positions (colors might be wrong orientation)

```
    A corner is in the CORRECT POSITION if it has
    the right 3 colors, even if they're not oriented right.

    Example: This corner has Yellow, Green, Red
             so it belongs where Y, G, R centers meet.

             ┌───┐───         Even if yellow isn't
             │ R │ G │        facing up, it's in the
             ├───┼───         right POSITION!
             │ Y │
             └───┘
```

### The Algorithm: U R U' L' U R' U' L

```
    U    R    U'   L'   U    R'   U'   L

    Say: "Up, Right, Up-prime, Left-prime, Up, Right-prime, Up-prime, Left"

    Tip: Think "U R U'" then "L' U R' U'" then "L"
```

### The Process:

```
1. Check each corner - is it in the right position?
   (Has the 3 colors that meet at that corner)

2. Count how many are correct:
```

#### If ALL 4 are in correct positions: Skip to Step 7!

#### If 1 corner is correct:
```
    Hold the cube with the CORRECT corner in FRONT-RIGHT

         ┌───┬───┬───┐
         │ ? │   │ ✓ │ ← Correct corner in front-right
         ├───┼───┼───┤
         │   │ Y │   │
         ├───┼───┼───┤
         │ ? │   │ ? │
         └───┴───┴───┘

    Apply: U R U' L' U R' U' L

    Check again - might need to repeat!
```

#### If 0 corners are correct:
```
    Just apply the algorithm from any position:
    U R U' L' U R' U' L

    Now at least 1 should be correct.
    Then solve as above.
```

### Important Note:
The algorithm CYCLES 3 corners while keeping 1 fixed:
```
    ┌───┐   ←───   ┌───┐
    │ A │         │ B │
    └───┘         └───┘
      │             ↑
      │             │
      ↓             │
    ┌───┐   ───→   ┌───┐
    │ D │ (stays)  │ C │
    └───┘         └───┘

    D stays fixed, A→B→C→A
```

---

## Step 7: Orient Yellow Corners

**GOAL:** Twist each corner so yellow faces up

```
    BEFORE:                        AFTER (SOLVED!):
    ┌───┬───┬───┐                 ┌───┬───┬───┐
    │ R │ Y │ G │                 │ Y │ Y │ Y │
    ├───┼───┼───┤                 ├───┼───┼───┤
    │ Y │ Y │ Y │     ───→        │ Y │ Y │ Y │
    ├───┼───┼───┤                 ├───┼───┼───┤
    │ B │ Y │ O │                 │ Y │ Y │ Y │
    └───┴───┴───┘                 └───┴───┴───┘
```

### The Algorithm: R U R' U' (yes, "Sexy Move" again!)

**But used differently here!**

### The Process:

```
1. Hold cube with an UNSOLVED corner in FRONT-RIGHT position
   (a corner where yellow is NOT facing up)

2. Do R U R' U' repeatedly (2, 4, or 6 times) until
   that corner has yellow facing UP

3. WITHOUT ROTATING THE CUBE, turn only the U face
   to bring another unsolved corner to front-right

4. Repeat steps 2-3 until all corners are solved

⚠️ CRITICAL: DO NOT ROTATE THE CUBE during this step!
             ONLY use U moves between corners!
```

### Detailed Walkthrough:

```
Step 1: Put unsolved corner at FRONT-RIGHT
        ┌───┬───┬───┐
        │   │   │ R │ ← Yellow on side, not top!
        ├───┼───┼───┤
        │   │ Y │   │
        └───┴───┴───┘

Step 2: Do R U R' U' - repeat 2, 4, or 6 times
        Keep going until yellow faces UP on this corner

        ⚠️ THE CUBE WILL LOOK MESSED UP - THIS IS NORMAL!

Step 3: Turn ONLY U (not the whole cube!) to bring
        next unsolved corner to front-right

Step 4: Repeat R U R' U' until that corner is solved

Step 5: Continue until all 4 corners show yellow on top

Step 6: Turn U to align the final layer

        🎉 CUBE SOLVED! 🎉
```

### WHY IT LOOKS BROKEN (DON'T PANIC!):

```
During this step, the cube looks like this:

        ┌───┬───┬───┐
        │ Y │ O │ G │   ← Looks totally messed up!
        ├───┼───┼───┤
        │ B │ Y │ R │
        ├───┼───┼───┤
        │ W │ G │ O │   ← Bottom layers look destroyed!
        └───┴───┴───┘

    THIS IS NORMAL! Trust the process!

    Each complete "corner solve" (2, 4, or 6 sexy moves)
    returns the bottom two layers to their correct state.

    Just DON'T rotate the cube and you'll be fine!
```

---

## Troubleshooting

### Common Problems and Solutions

#### Problem 1: "I finished but one piece is wrong!"
```
IMPOSSIBLE SITUATION - Cube was assembled wrong!

These cannot happen on a properly assembled cube:
• One corner twisted wrong
• One edge flipped wrong
• Two pieces swapped

SOLUTION: Take out the pieces and reassemble correctly
          (or peel off stickers - we won't judge)
```

#### Problem 2: "Step 7 isn't working, everything is messed up!"
```
You probably rotated the cube when you shouldn't have.

WHAT TO DO:
1. Keep doing R U R' U' on current corner until yellow is up
2. Do U until next unsolved corner is at front-right
3. NEVER turn the whole cube
4. Keep going - it will work!

If hopelessly lost: Re-solve from Step 4
```

#### Problem 3: "Can't find where a corner belongs"
```
Look at the THREE colors on the corner.
Find where those three centers meet.
That's where it belongs!

Example: Corner with White, Blue, Red
         → Goes where W, B, R centers meet
         → Front-right corner of white face
           (when blue is front, red is right)
```

#### Problem 4: "Middle layer edge is flipped in place"
```
        ┌───┐
        │ G │ ← Green where red should be
    ┌───┼───┼───┐
    │   │ R │   │ ← Red where green should be
    └───┴───┴───┘

SOLUTION:
1. Put any different edge there using R or L algorithm
2. The flipped edge goes to top
3. Now insert it correctly
```

#### Problem 5: "Yellow cross edges need to swap opposite"
```
Just apply the edge algorithm twice:
R U R' U R U2 R' (adjust with U) R U R' U R U2 R'
```

---

## Quick Reference Card

### All Algorithms in One Place:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP │ ALGORITHM                    │ WHEN TO USE                          │
├─────────────────────────────────────────────────────────────────────────────┤
│  2   │ R U R' U'                    │ Insert white corners (repeat 1-5x)   │
├─────────────────────────────────────────────────────────────────────────────┤
│  3   │ U' L' U L U F U' F'          │ Edge goes LEFT                       │
│      │ U R U' R' U' F' U F          │ Edge goes RIGHT                      │
├─────────────────────────────────────────────────────────────────────────────┤
│  4   │ F R U R' U' F'               │ Yellow cross (1-3 times)             │
├─────────────────────────────────────────────────────────────────────────────┤
│  5   │ R U R' U R U2 R'             │ Position yellow edges                │
├─────────────────────────────────────────────────────────────────────────────┤
│  6   │ U R U' L' U R' U' L          │ Position yellow corners              │
├─────────────────────────────────────────────────────────────────────────────┤
│  7   │ R U R' U' (repeat)           │ Orient yellow corners                │
│      │ (2, 4, or 6 times per corner)│ (DON'T rotate cube!)                 │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Finger Tricks for Speed:

```
R U R' U' (Sexy Move):
- Use right index finger to push R
- Use right thumb on back to pull R'
- Use left index finger to push U
- Use right index finger to push U' (from the back)

Practice until it flows smoothly!
```

---

## You Did It!

```
        ┌──────────────────────────────────────────┐
        │                                          │
        │     🎉 CONGRATULATIONS! 🎉              │
        │                                          │
        │     You can now solve a Rubik's Cube!    │
        │                                          │
        │     Average beginner time: 2-5 minutes   │
        │     With practice: under 1 minute        │
        │                                          │
        │     Next challenges:                     │
        │     • Try solving without looking        │
        │       at the guide                       │
        │     • Learn CFOP method for speed        │
        │     • Time yourself!                     │
        │                                          │
        └──────────────────────────────────────────┘

              ┌───┬───┬───┐
              │ Y │ Y │ Y │
              ├───┼───┼───┤
              │ Y │ Y │ Y │
              ├───┼───┼───┤
              │ Y │ Y │ Y │
    ┌───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┐
    │ O │ O │ O │ G │ G │ G │ R │ R │ R │ B │ B │ B │
    ├───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┤
    │ O │ O │ O │ G │ G │ G │ R │ R │ R │ B │ B │ B │
    ├───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┤
    │ O │ O │ O │ G │ G │ G │ R │ R │ R │ B │ B │ B │
    └───┴───┴───┼───┼───┼───┴───┴───┴───┴───┴───┴───┘
              │ W │ W │ W │
              ├───┼───┼───┤
              │ W │ W │ W │
              ├───┼───┼───┤
              │ W │ W │ W │
              └───┴───┴───┘
```

---

*Guide created with care. Now go impress everyone!*
