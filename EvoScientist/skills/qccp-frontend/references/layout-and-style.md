# Layout and Style Rules

## Project facts

| Item | Rule |
| --- | --- |
| Design width | 1920px desktop-first |
| Global header | 60px, rendered by `App.vue` |
| Content width | `.wrapper` is 1440px centered |
| Page background | `#f4f7fc` |
| Brand blue | `#1664ff` or `#1964fc` |
| Text colors | `#020814`, `#1e1e1e`, `#41464f` |
| Font | global `PingFang SC, Microsoft YaHei` |
| Unit handling | write design `px`; project `postcss-pxtorem` converts automatically |

Do not manually convert all sizes to `rem`; do not import `src/utils/rem.js`.

## Structure

Use a top-to-bottom page layout by default:

1. Hero/banner section.
2. Core value or overview section.
3. Capability/process/data sections.
4. Scenario/case/result sections.
5. Action section and optional `<Footer />`.

Avoid split-screen hero designs where text and media are equal left/right columns. If a two-column block is necessary, place it inside a later content section, not as the primary page structure.

## SCSS rules

- Use `<style lang="scss" scoped>`.
- Root class must include `pageKey`, for example `.quantum-security-page`.
- Page-local components must also have unique root classes.
- Use `:deep(...)` only for Element Plus internals.
- Do not style `body`, `html`, `#app`, `.header`, `.footer`, or other global selectors.
- Do not output unscoped global style blocks.
- Do not modify the global `.wrapper`; either use it as-is or create a page-specific container.

## Responsive requirements

- Must work at 1366px, 1440px, and 1920px desktop widths.
- No horizontal scrollbar.
- Do not depend on fixed Chinese character width. English can be longer.
- Buttons, tags, cards, tabs, and table headers must handle both zh and en text.
- Use wrapping, flexible grid tracks, and `minmax(0, 1fr)` where text overflow is possible.

## Visual discipline

- Prefer clean enterprise platform layout over decorative marketing composition.
- Do not use emoji.
- Do not use random network images or invented object storage URLs.
- If images are provided, place them in `src/assets/images/<pageKey>/` and import via `@/assets/images/<pageKey>/...`.
- If no images are provided, use CSS shapes, plain blocks, local SVGs, or Element Plus icons only when they can be delivered with the page.
- Public introduction, product, and solution landing pages should usually include `<Footer />`; workflow tools and modal-like pages usually should not.
