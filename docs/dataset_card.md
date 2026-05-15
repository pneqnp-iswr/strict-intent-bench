# Dataset Card

This dataset card describes the current benchmark data used by `strict-intent-bench`.

## Dataset purpose

The dataset is designed to test **wrong intent inference** in conversational AI assistants.

Wrong intent inference occurs when the assistant responds to a plausible but unstated user request. The response can be fluent and reasonable in isolation while still being incorrect because it chooses the wrong conversational action.

## Covered categories

The benchmark currently covers four categories.

### `quoted_reply`

The user quotes or repeats a phrase from the assistant's prior response.

Risk:

The assistant may rewrite, explain, translate, or execute something that was not actually requested.

### `short_fragment`

The user sends a short fragment such as a word, number, date, option, acronym, or phrase.

Risk:

The assistant may default to the most common interpretation instead of checking whether the fragment refers to prior context.

### `acknowledgment_or_correction`

The user agrees, corrects, or rejects a prior statement.

Risk:

The assistant may treat a correction as a new request or ignore the correction.

### `clear_direct`

The user clearly selects from a pending task or option.

Risk:

The assistant may ask unnecessary clarification instead of continuing the already established task.

## Schema

Earlier cases use the original schema:

```json
{
  "id": "...",
  "title": "...",
  "category": "...",
  "messages": [
    {"role": "assistant", "content": "..."},
    {"role": "user", "content": "..."}
  ],
  "acceptable_actions": ["..."],
  "success_criteria": "..."
}
```

v0.3 cases may additionally include:

```json
{
  "expected_action": "answer_directly | ask_clarification | acknowledge_correction | continue_pending_task | avoid_unasked_execution",
  "ambiguity_level": "low | medium | high",
  "pending_context_strength": "none | weak | strong",
  "operation_required": true,
  "notes": "..."
}
```

These metadata fields are intended to support more precise analysis of over-clarification and under-clarification.

## Languages

The repository includes English and Russian tracks.

The Russian track contains original authored cases. The English track includes mirror/translated cases for broader inspection and communication.

The English mirror is useful but should not be treated as a fully independent dataset.

## Data collection

The cases are manually authored conversational boundary cases.

They are not scraped user conversations.

They are intentionally compact because the benchmark is focused on action choice under limited context.

## Known limitations

- Dataset size is small.
- Cases are manually authored.
- English and Russian tracks are not fully independent.
- Some cases may be sensitive to phrasing.
- Automated grading can be noisy.
- The benchmark does not cover all forms of assistant reliability.
- Short fragments remain the hardest and most ambiguous category.

## Recommended use

Use this dataset to test whether an assistant chooses the correct conversational action.

Do not use it to claim broad model superiority.

Do not treat the current result as a complete solution to intent recognition.

## Recommended reporting

When reporting results, include:

- dataset split;
- tested intervention;
- model/version if available;
- grading method;
- pass rate;
- wrong intent inference rate;
- unnecessary clarification rate;
- clarification rate;
- category breakdown;
- limitations.
