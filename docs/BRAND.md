# Raidian brand book · 버건디 한 방울, 명료함 한 스푼 ♥

## Idea

**Raidian / 레이디안** is a small, helpful workbench for Git—not a full IDE. The UI communicates what will happen *before* it changes history. Feeling: **soft but deliberate**, cheerful without hiding risks.

## Character

**Ruby · 루비** is a smiling branch graph. Each node is a commit, the junction is a feature branch, and the blush stands for a calm workflow. Ruby never decorates irreversible operations with reassuring false promises.

- Banner: [`assets/brand/raidian-hero.svg`](../assets/brand/raidian-hero.svg), wide with accessible `<title>` and `<desc>`.
- Symbol: [`assets/brand/raidian-mark.svg`](../assets/brand/raidian-mark.svg), square mark for small spaces.
- Windows ICO: generated from [`scripts/make_icon.py`](../scripts/make_icon.py) with Pillow at build time.

## Design tokens

| Token | Value | Use |
| --- | --- | --- |
| Burgundy | `#551128` | Primary brand surface, dark titles |
| Crimson | `#A72146` | Primary button, commit and push |
| Rosy | `#C42B54` | Hover, attention |
| Blush | `#FCECEF` | Card accent, button secondary |
| Paper | `#FFFFFF` | Content canvas |
| Warm Canvas | `#F8F5F5` | App backdrop |
| Dark Ink | `#302329` | Body text |
| Muted Ink | `#776B70` | Secondary text |

Do not use color alone to represent a Git action. Show its name (`커밋`, `푸시`, `병합`) visibly. Keep red action colors distinct from errors: errors should also explain what happened in text.

## Typography and fonts

Font stack in GUI: Wanted Sans → Pretendard → Malgun Gothic/맑은 고딕 → Noto Sans CJK KR → platform alternatives. Only fonts that are licensed for embedding and redistribution may be packaged. **The requested attached font was not available to the session that assembled these sources, so no original font data has been embedded.** The font loader searches `assets/fonts/*.ttf` and registers these privately on Windows; font family detection depends on the font's internal metadata.

See [`assets/README.md`](../assets/README.md). There is no bundled proprietary font binary in source or binary outputs by default.

## Shape and motion

- Primary CTAs are pill-ish and visibly keyboard focusable, with rounded corners.
- Secondary controls use warm blush with clear text labels.
- Cards are clean rectangles with comfortable padding; keep content density low.
- Prefer no animation to avoid distracting agents or users.
- Responsive UI turns side-by-side tables into vertical tables at narrower widths.
- Provide keyboard shortcuts and explicit confirmation on merges and reverts.

## Contribution rules

Every brand asset must remain editable SVG or reproducibly generated code, contain accessible metadata, be tracked in Git, and respect upstream licenses. Avoid font CDN dependencies in the desktop UI; this app should work offline.
