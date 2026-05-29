# YGO Core Rulebook Summary (RAG)

## SEGOC — Simultaneous Effects Go On Chain

When multiple Spell Speed 1 effects (such as Trigger Effects) activate at the same time, they are placed on a special Chain in this **fixed order**:

1. **Chain Link 1+ (Category 1):** Turn Player's **mandatory** effects — if multiple, the Turn Player chooses their order.
2. **Next links (Category 2):** Opponent's **mandatory** effects — if multiple, the Opponent chooses their order.
3. **Next links (Category 3):** Turn Player's **optional** effects — if multiple, the Turn Player chooses their order.
4. **Last links (Category 4):** Opponent's **optional** effects — if multiple, the Opponent chooses their order.

**Chain Blocking rule:** Players **cannot** swap effects between these four categories. Reordering is only allowed among effects in the **same** category (e.g. two optional effects of the Turn Player).

Example mapping: Turn Player mandatory = Category 1, Opponent mandatory = Category 2, Turn Player optional = Category 3, Opponent optional = Category 4.

## PSCT — Colon and Semicolon

Card effects use a colon (`:`) and/or semicolon (`;`) to separate parts of the text:

- **Before the first semicolon:** What you do when the effect is **activated** (often the **activation cost** and/or **targeting at activation**). Costs are paid **immediately when you declare the activation**.
- **After all colons and semicolons:** What happens at **resolution**.

**Cost rule:** If an effect's activation is **negated**, costs already paid (e.g. banishing a card before the first `;`) are **NOT** returned.

**Targeting rule:** Targets chosen before a semicolon at activation are **locked** — you cannot change targets during resolution, even if the effect is later negated or interrupted.

## Continuous Spell Field Presence

Continuous Spell Cards, Continuous Trap Cards, Field Spells, and Equip Spells must remain **face-up on the field** to resolve their activated effects. If the card is destroyed or leaves the field before that Chain Link resolves, the effect **resolves without effect** — even if conjunction text (e.g. "and also") would otherwise make later steps independent.

Destroying an activated card does **not** negate an effect that already activated, **except** when the card type requires field presence to resolve.

## Continuous Effects vs Activated Effects

A **Continuous Effect** (no colon `:` and no semicolon `;` in the effect text) applies automatically while the monster is on the field. It does **not** create a Chain Link or an **activation** to negate.

Effects that **negate the activation** of a monster effect cannot stop a Continuous Effect, because there is no activation to negate.

## Continuous Effect Blocking Trigger Activation

If a Continuous Effect states that opponent's monsters **cannot activate their effects on the field**, that restriction applies **continuously** while the source monster is face-up — it does not activate or start a Chain.

An optional **Trigger Effect** on Summon (e.g. "When this card is Summoned: You can destroy 1 card") still requires the player to **activate** it. That activation is an **activated effect on the field**.

If the Continuous Effect already forbids activating effects, the player **CANNOT** activate the Trigger Effect and **CANNOT** place it on a Chain — even immediately after a successful Summon. The summon condition being met does not override an active activation restriction.

**Timing:** The Continuous Effect is already applying when the summoned monster hits the field; the restriction is checked **before** the Trigger activation can be declared.
