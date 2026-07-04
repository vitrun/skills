# Reference Site to DESIGN.md

Use this branch when the user provides a reference URL, screenshot, or named site as the main taste signal for a new landing page, portfolio, or marketing/front-facing website.

## Goal

Convert the reference into an implementation-ready `DESIGN.md` before writing page code. The output should capture reusable visual grammar, not clone the source site.

## Workflow

1. Capture evidence from the real reference.
   - Prefer live browser inspection and computed styles over memory.
   - If a vetted website-to-`DESIGN.md` extractor is already installed or the user explicitly asks for one, use it.
   - Do not install or vendor a third-party extractor silently.
2. Write or update `DESIGN.md` with:
   - page type, audience, and intended vibe;
   - visual tokens: color roles, type scale, spacing, radii, shadows, borders;
   - layout grammar: grid, section rhythm, hero composition, image ratios, nav/footer treatment;
   - motion and interaction cues, including reduced-motion fallback;
   - asset requirements: exact slots, aspect ratios, and source policy;
   - substitutions: what must be replaced for the user's own product, brand, and copy.
3. State the copyright and brand boundary before implementation:
   - Do not copy logos, trademarks, proprietary photos, illustrations, icons, text, testimonials, pricing, or customer names.
   - Borrow only abstract structure: density, hierarchy, rhythm, contrast, interaction style, and component relationships.
   - Replace all content and assets with the user's real materials, generated assets, or clearly marked placeholders.
4. Implement from `DESIGN.md`, not directly from the reference tab.
5. During pre-flight, compare the page against `DESIGN.md` and the reference boundary:
   - close enough in design language;
   - distinct in brand/content/assets;
   - no copied proprietary surface.

## Stop Rules

- If the reference site is unavailable, proceed only from user-provided screenshots or ask for one screenshot if no visual evidence exists.
- If the user explicitly asks to clone a real brand or copy its assets, refuse that part and offer a same-vibe original design.
- If the project already has a design system or brand guide, use the reference only as secondary inspiration.
