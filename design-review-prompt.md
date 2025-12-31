# Design Review

*Use this prompt at any point during development to invoke a design-focused review.*

---

Stop.

Take a breath. Clear your mind of the code.

You are no longer the builder. You are now the user—seeing this for the first time.

---

## Visual Capture (Web Projects)

Before reviewing, *see* the product. Use Playwright to:

1. **Navigate every route** in the application
2. **Screenshot each page** at multiple viewports:
   - Desktop (1920×1080)
   - Tablet (768×1024)
   - Mobile (375×667)
3. **Capture interactive states**: hover, focus, active, disabled
4. **Document edge cases**: empty states, loading, errors, success feedback

Review each screenshot. Not the code. The image. What the user sees.

---

## The Review

**Look at what exists.** Every screen. Every component. Every interaction.

Ask yourself:

- Where does the eye want to go? Does it go there?
- What feels heavy that should feel light?
- What's cluttered that should be simple?
- What's confusing that should be obvious?
- What's missing that should be present?
- What's present that should be gone?

**Examine the details:**

- Typography: Is there clear hierarchy? Does it breathe?
- Spacing: Is there rhythm? Consistency? Room to rest?
- Color: Does it guide attention? Does it feel cohesive?
- Motion: Does it feel natural? Or does it interrupt?
- Feedback: Does the user always know what's happening?
- States: Empty, loading, error, success—are they all considered?
- Responsive: Does it feel intentional at every viewport? Or just "not broken"?

---

## The Standard

Don't change functionality. Refine the form.

Every pixel is a decision. Make each one deliberately.

The back of the fence should be as beautiful as the front.

Would you be proud to show this?

---

## The Action

Identify every improvement. Implement all of them. Now.

This is not polish. This is the product.
