---
name: find-topic
description: |
  Turn a rough research idea or topic into a tailored, copy-ready prompt for a
  ChatGPT or Claude deep-research task. Use when the user wants help scoping a
  research direction, deciding what a literature survey should investigate, or
  preparing a prompt that will produce a detailed survey report. First gather
  missing context such as the relevant subfield, research goal, prior knowledge,
  time horizon, and resource budget; then generate the prompt. Do not perform the
  literature survey or deep research yourself.
---

# Find Topic

Help the user turn an initial research idea into one self-contained prompt they can
copy into ChatGPT or Claude's deep-research mode.

## Workflow

### 1. Clarify the request

Read the user's initial message and retain every constraint it already answers. Ask
only for information that would materially change the deep-research task. Usually ask
one concise message containing 3–6 questions selected from:

- Which subfield, application, or interpretation of the topic interests them most.
- What outcome they want: field orientation, related work, a thesis direction, an
  experiment plan, an engineering decision, or another goal.
- What they already know, have read, or have tried.
- Whether to cover the field's history, emphasize a recent time window, or both.
- Whether they prefer broad coverage or depth on a narrow question.
- What constraints define a viable direction: available time, team size, compute,
  data access, equipment, and monetary budget.
- Which methods, applications, venues, regions, languages, or sources to include or
  exclude.
- What report format or level of technical detail they need.

When the topic is ambiguous, offer a short list of concrete interpretations to make
the question easy to answer. Use plain-text chat questions so the workflow is portable
across agents. Stop and wait for the reply. If the reply still leaves a consequential
ambiguity, ask one focused follow-up; otherwise proceed.

Do not browse, search for papers, evaluate the idea, or begin writing the survey during
this step.

### 2. Generate the deep-research prompt

Produce exactly one prompt in a single fenced code block. Make it ready to paste as-is:
do not leave placeholders, alternatives, or instructions for the user to edit.

Tailor the prompt to the user's answers and include:

1. The research topic, central question, intended use, and explicit scope boundaries.
2. The user's background and practical constraints, including their resource budget.
3. A request for a rigorous literature search using current primary sources and recent
   surveys, with bibliographic details and direct links or persistent identifiers.
4. A report structure appropriate to the topic. Unless the user asks otherwise, request
   an executive summary, scope and methodology, taxonomy of approaches, key-paper
   comparison, datasets and evaluation practices, current state of the art, disagreements
   or limitations, open questions, and a conclusion tied to the user's goal.
5. Instructions to distinguish sourced findings from synthesis, verify citations, avoid
   invented references, state coverage limitations, and report the search cutoff date.
6. Any requested depth, date range, exclusions, tables, length, or output format.

If the user's goal is to identify a feasible research direction, ask the deep-research
system to assess open questions against the user's constraints. Require it to separate
evidence-backed gaps from speculative opportunities and to explain why each promising
direction is feasible within the stated budget.

Do not answer the generated prompt, add a survey of your own, or write repository files.
After the code block, add at most one short sentence stating that the prompt is ready to
paste into a deep-research chat.
