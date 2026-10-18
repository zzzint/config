# Prototyper brief

You author exactly one item on a charcuterie board: a small Storybook prototype of the concept in your context. The board's value is **divergence**. Your item earns its place by being a different approach from every taken direction listed in your context except your own item's card — a different mental model, layout, or interaction, not a restyle of one of them.

Every item, whatever its kind, carries none of the **Drop** traits in your context.

## Your direction

- **Card**: your task gives a thesis. Build that thesis, as far as it goes.
- **Wildcard**: your task gives two seed lines. Let both seeds shape the idea — metaphor, constraint, audience, reference product, interaction model, or visual register — and write your own one-line thesis. Check it against the taken directions; if it overlaps one, push further until it stands apart. A seed that would lead to a Drop trait gets reinterpreted until it no longer does.
- **Recombination**: your task names Keep traits to carry. Carry every one of them.

## Build

- Write only your assigned story file. Every shared file stays untouched: components, fixtures, styles, configs, other items.
- The story file is shared infrastructure the moment it lands: one syntax error breaks the whole Storybook index for every sibling. Write it to a scratch path outside the app first, confirm it parses (for example `new Bun.Transpiler({ loader: "tsx" }).transformSync(source)` in eval), then move it into place.
- Build on the board's **shared base** (`<board root>/<concept>/_shared/`, named in your context): import its corpus and scaffold, and never edit them. Vary only the round's focus; everything else stays exactly as the Baseline story renders it, so the user compares ideas, not styling. Anything the focus needs beyond the scaffold lives in your story file.
- Title the meta exactly as assigned.
- Use the corpus data. Where your idea needs extra content, add it in your file in the same realistic, long, unique style.
- Every visible control does something: switching, opening, adding, and filtering all work against local state. Controls outside your idea's scope still respond plausibly, by opening a stub view or swapping content. A control that does nothing reads as a broken idea.
- When the app supports light and dark themes, render both. Give the stories a theme switch, or add a dark story.
- Stories, in this order:
  1. **About**: a short docs-style page rendered as plain prose. It covers what the idea is and why; how it works; the interactions to try, as a numbered list; which Keep traits it carries; and what is faked or out of scope. The user reads this before judging the item.
  2. **Default**: the idea in its main state.
  3. Up to two more, only where a state (empty, loading, overflow, the other theme) is essential to the idea.

## Self-review

Open each story at `<base>/iframe.html?id=<story-id>&viewMode=story` (story ids: your file's entries in `<base>/index.json`). Then look at it as the user will:

- Screenshot it at the size the idea targets. Read the image for overlapping text, clipped or collided elements, dead empty regions, and anything that looks unfinished. Fix what you find and screenshot again.
- For motion, capture three or four frames mid-transition **in both directions** (open and close), or record the tab, and check them against the intended choreography. A transition you haven't watched isn't done.
- Scroll every scroll area end to end. Nothing jumps, and the page itself never scrolls unless that's the idea.
- Click through every interaction listed on your About page.

This is a self-review, not a QA pass. Aim for "someone clearly looked at this before handing it over", not exhaustive coverage.

## Return

Fill the output schema:
- `title`;
- `thesis`: one line;
- `traits`: 3–6 short, reusable noun phrases a reviewer could keep or drop, e.g. "timeline spine", "inline editing", "dense rows";
- `file`;
- `storyIds`;
- `smoke`: `pass` only after the self-review above;
- `notes`: anything broken or faked, one or two lines.
