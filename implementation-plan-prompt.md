# Implementation Plan Prompt

Break down the development process into small, manageable steps that can be executed sequentially by a code generation AI.

Each step should focus on a specific aspect of the application and should be concrete enough for the AI to implement in a single iteration.

When creating your plan, follow these guidelines:

1. Start with the core project structure and essential configurations.
2. Include steps for writing tests and implementing the specified testing strategy.
3. Ensure that each step builds upon the previous ones in a logical manner.

Present your plan using the following markdown-based format. This format is specifically designed to integrate with the subsequent code generation phase, where an AI will systematically implement each step and mark it as complete. Each step must be atomic and self-contained enough to be implemented in a single code generation iteration, and should modify no more than 10 files at once (ideally less) to ensure manageable changes.

``````markdown
# Implementation Plan

## [Section Name]

- [ ] Step 1: [Brief title]
  - **Task**: [Detailed explanation of what needs to be implemented]
  - **Description**: [Detailed description of why this step is important]
  - **Files**: [Maximum of 10 files, ideally less]
    - `path/to/file1.ts`: [Description of changes]
  - **Step Dependencies**: [Step Dependencies]
  - **User Instructions**: [Instructions for User]

[Additional steps...]
``````

After presenting your plan, provide a brief summary of the overall approach and any key considerations for the implementation process.

## Guidelines

Remember to:

- Ensure that your plan covers all aspects of the technical specification.
- Break down complex features into smaller, manageable tasks.
- Consider the logical order of implementation, ensuring that dependencies are addressed in the correct sequence.
- Include steps for error handling, data validation, and edge case management.
- Always include testing for each step where possible. Testing is critical to ensure expected behavior as well as make sure you don't break existing functionality.

## Final Output

Output the implementation plan all together in markdown wrapped in six backticks so that it can easily be copied.
