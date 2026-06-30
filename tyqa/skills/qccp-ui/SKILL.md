---
name: qccp-ui
description: "Guides the strict TianYan Quantum Computing Cloud Platform UI design specification for qccp/cloud showcase pages. Use when designing or implementing qccp-style pages, choosing colors/fonts/spacing/radius, reviewing visual consistency, generating platform UI components, or enforcing no-emoji, token, and top-to-bottom layout rules before qccp-frontend work. Do NOT use for backend/API work, cqlib algorithm implementation, or final delivery readiness decisions."
allowed-tools: "write_file edit_file read_file think_tool"
metadata:
  author: TYQA
  version: '1.0.0'
  tags: [frontend, qccp, ui, design, cloud-showcase]
---

# UI Design Spec

This skill defines the visual discipline for TianYan Quantum Computing Cloud Platform-style pages in the `qccp_web_page` delivery profile. For qccp-web implementation, use this as the visual reference before `qccp-frontend`; qccp-web uses Vue SFC + scoped SCSS + Element Plus, not Tailwind.

## When to Use

- User needs qccp/cloud showcase visual rules before generating Vue page artifacts.
- User asks for colors, typography, spacing, radius, component states, bilingual layout fit, or visual consistency review.
- User is preparing a quantum application page and needs design constraints before `qccp-frontend`.
- `application-pipeline` Stage 3 needs visual consistency evidence for application packaging.

## When NOT to Use

- **Vue SFC, route, i18n, or integration output** -> use `qccp-frontend` after applying this spec.
- **Backend/API/service/deployment artifacts** -> use `qccp-service`.
- **Cqlib algorithm implementation** -> use `cqlib-sdk`.
- **Final staged verification** -> use `application-pipeline`.

## Top rules

1. Use the exact token values below. Do not approximate colors, font sizes, spacing, or radius.
2. Prefer theme variables or SCSS variables instead of scattered hardcoded style values.
3. Reuse page-local atomic components for buttons, inputs, tabs, tags, panels, and metric blocks.
4. Do not introduce unrequested gradients, shadows, animation, decorative graphics, special fonts, or non-standard icons.
5. Do not use emoji anywhere in UI copy, labels, placeholders, comments intended for UI display, or generated assets.
6. Page layout should be mainly vertical: top banner, then stacked content sections. Avoid a primary left-right split layout unless explicitly required.
7. Keep Chinese/English text length differences in mind; layouts must not break when switched to English.

## Locked layout values

| Token | Value | Use |
| --- | --- | --- |
| canvas | 1920px | desktop design base |
| containerX | 140px | left/right page margin in strict spec mockups |
| containerTop | 60px | top margin / header-aware offset |
| containerBottom | 140px | bottom page margin |
| base20 | 20px | grid gap |
| base30 | 30px | grid gap |
| radiusBtn | 4px | buttons |
| radiusTag | 6px | tags |
| radiusModal | 8px | cards, panels, modals |

When implementing in qccp-web, `.wrapper` may provide the 1440px centered project container. Do not alter global `.wrapper`.

## Color tokens

| Token | HEX | Use |
| --- | --- | --- |
| primary | `#1664FF` | main brand blue |
| primaryDeep | `#4F9DF7` | auxiliary blue |
| linkBlue | `#1F84FC` | links |
| danger | `#FB4214` | errors and warning dots |
| cyan | `#00C7E7` | cyan accent |
| textTitle | `#020814` | titles |
| textSub | `#41464F` | secondary text |
| textBody | `#939AAB` | body/help text |
| pageBg | `#F4F7FC` | page background |
| cardBg | `#FFFFFF` | white card background |
| cardBgBlue | `#F3F7FF` | light blue panel background |
| borderLine | `#DCE0EB` | borders/dividers |
| extend2 | `#BB79E1` | limited accent |
| extend3 | `#A58DF8` | limited accent |
| extend4 | `#4A86FF` | limited accent |

Use the `#ECF2FF` to `#B5BFFF` range only when the design explicitly calls for that extension background. Do not add arbitrary gradients.

## Typography tokens

| Token | Size | Weight | Use |
| --- | --- | --- | --- |
| textBanner | 60px | Bold | banner title only |
| textH1 | 40px | Bold | page title |
| textH2 | 30px | Regular | section title, data value |
| textH3 | 24px | Regular | block title |
| textSubHead | 20px | Regular | subtitle |
| textContent | 18px | Regular | body paragraphs |
| textMinor | 16px | Regular | secondary text |
| textTip | 14px | Regular | tables, notes, helper text |

Do not bold text that the spec marks as Regular.

## Component rules

Buttons:

- `PrimaryBtn`: filled primary button.
- `LineBtn`: border button.
- `TextBtn`: text/link button.
- `DisabledBtn`: disabled gray button.

Tabs:

- Active: primary background and white text.
- Inactive: card background and `textBody`.

Inputs:

- Default border: `borderLine`.
- Focus border: `primary`.
- Readonly background: `pageBg`.

Icons:

- Use 1.5px linear outline style.
- Default color is `primary`.
- Status dot uses `danger`.
- No solid, colorful, thick, emoji, or decorative icons.

Tags:

- Radius: `radiusTag` 6px.
- Padding: 4px vertical, 8px horizontal.
- State color must come from the token list.

## Prohibited

- Emoji.
- Non-token color values.
- Non-token radius values.
- Decorative gradients, shadows, bokeh/orbs, or animation beyond necessary hover feedback.
- Primary layout built as a left-right marketing split when a vertical structure works.
- Random web images or invented asset URLs.
- Hardcoded one-language UI text in bilingual qccp pages.

## Output checklist

- [ ] Layout is primarily top-to-bottom.
- [ ] No emoji appears in UI or generated assets.
- [ ] Colors come from token list.
- [ ] Typography size and weight match token mapping.
- [ ] Spacing uses the allowed grid values or project container conventions.
- [ ] Radius uses 4px, 6px, or 8px according to component type.
- [ ] Components are reused rather than hand-styled repeatedly.
- [ ] Chinese and English text both fit without overlap.

When `application_manifest.json` is in scope, record or request a `qccp_web` UI evidence entry that identifies the SFC path, token/color/radius/font checks, bilingual-fit status, and any visual limitations. This is evidence for validation, not final delivery approval.

## Handoff

Use this skill to constrain visual decisions and record visual consistency evidence. Use `qccp-frontend` for Vue SFC structure, route snippets, i18n entries, API integration, output folders, and `INTEGRATE.md`.
