# Implementation Plan

## Philosophy

We don't ship features. We ship experiences.

Every implementation plan is a blueprint for something that will be *used* by humans. Before a single line of code is written, understand this: the way it works is inseparable from the way it looks and feels. Design is not a phase. Design is not a department. Design is how it works.

Break down the development process into small, manageable steps that can be executed sequentially by a code generation AI. Each step should be concrete enough to implement in a single iteration—but never lose sight of the whole.

---

## Planning Principles

1. **Start at the foundation.** Core project structure and essential configurations come first. Get the bones right.

2. **Build in logical sequence.** Each step builds upon the previous ones. Dependencies flow naturally, never backwards.

3. **Test relentlessly.** Every step includes testing where possible. We don't move forward on broken ground.

4. **Keep changes atomic.** Each step modifies no more than 10 files—ideally fewer. Smaller changes, clearer intent.

5. **Design from the start.** Consider the user's experience in every step. The database schema affects the API. The API affects the UI. The UI affects how someone *feels* when they use your product.

6. **See it constantly.** *(Web projects)* After every step that touches UI, use Playwright to visually verify the result. Don't wait until the end to discover something looks wrong. Catch it immediately. Fix it immediately.

---

## Step Format

Present your plan using this structure. Each step must be self-contained—implementable in a single iteration.

``````markdown
# Implementation Plan

## Phase 1: [Phase Name]

- [ ] Step 1.1: [Brief title]
  - **Task**: [What needs to be implemented]
  - **Why**: [Why this step matters to the whole]
  - **Files**:
    - `path/to/file.ts`: [Description of changes]
  - **Dependencies**: [Previous steps this builds upon]
  - **Design Consideration**: [How this affects user experience]
  - **Testing**: [How we verify this works]
  - **UI Verification**: [Web projects: Playwright routes to visually inspect after this step. Specify pages/components to screenshot and verify. "None" if step doesn't affect UI]
  - **User Instructions**: [Any manual steps required]

[Additional steps...]

## Phase N: Design Review

The final phase. Non-negotiable.

- [ ] Step N.1: Visual audit with Playwright (Web projects)
  - **Task**: Systematically navigate every route, capture every state
  - **Why**: See the product as users will see it
  - **Playwright Scope**:
    - Screenshot every page at desktop, tablet, and mobile viewports
    - Capture all interactive states: hover, focus, active, disabled
    - Document empty states, loading states, error states, success states
    - Verify visual consistency across the entire application
  - **Review Each Screenshot**: Does this meet the standard?

- [ ] Step N.2: Design refinement
  - **Task**: Fix every visual issue identified
  - **Why**: Details matter. The back of the fence matters.
  - **Scope**: Typography, spacing, color, motion, feedback, alignment, consistency
  - **Standard**: Would you be proud to show this?
``````

---

## Guidelines

Cover all aspects of your technical specification:

- Break complex features into smaller tasks
- Address dependencies in correct sequence
- Include error handling and edge cases
- Validate data at boundaries
- Test each step to protect what already works

---

## The Design Review

When implementation is complete, invoke this.

**For web projects:** Use Playwright to navigate every route and capture screenshots. See the product as your users will. Review each image with fresh eyes.

---

*Take a breath. Step back from the code.*

*You are no longer the engineer who built this. You are now seeing it for the first time.*

*Look at every screen. Every interaction. Every pixel.*

*Where does the eye want to go? Does it go there?*
*What feels heavy that should feel light?*
*What's cluttered that should be simple?*
*What's confusing that should be obvious?*

*Don't change functionality. Refine the form.*

*The spacing. The typography. The color. The motion. The feedback.*

*Every detail is a decision. Make each one deliberately.*

*This is the product that represents you. This is the standard that defines what comes next.*

*Make it beautiful.*

---

## Final Output

Output your complete implementation plan in markdown, wrapped in six backticks for easy copying.

After the plan, provide a brief summary of:
- Overall approach
- Key architectural decisions
- Critical path to MVP
- Design principles that will guide the build
