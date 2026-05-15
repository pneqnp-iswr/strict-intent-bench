# Case Quality Checklist

Use this checklist before adding or publishing new benchmark cases.

The goal is to keep `strict-intent-bench` focused on wrong intent inference rather than vague conversational quality.

## 1. Intent clarity

A case should have one primary expected action.

Check:

- Is the intended action recoverable from the visible messages?
- Is the expected action label justified by context?
- Would two reasonable annotators likely agree on the action type?

Reject or rewrite the case if the intended action depends on hidden author intent.

## 2. Category fit

Each case should clearly fit one main category:

- `quoted_reply`
- `short_fragment`
- `acknowledgment_or_correction`
- `clear_direct`

Check:

- Is the category the main source of difficulty?
- Is the case testing intent selection rather than factual knowledge?
- Would the case still make sense without external context?

## 3. Failure mode isolation

A good case isolates a conversational action error.

Check whether the likely failure is one of:

- wrong intent inference;
- unnecessary clarification;
- needed clarification missing;
- correction mishandled;
- pending task missed.

Avoid cases where the main failure would be broad reasoning, factual lookup, or subjective style quality.

## 4. Success criteria

The success criteria should be specific enough to grade.

Good success criteria:

- state what action the assistant should take;
- state what it should avoid;
- do not require hidden assumptions;
- do not overfit to one exact wording.

Bad success criteria:

- "answer well";
- "be helpful";
- "understand the user";
- "do the right thing" without defining the right action.

## 5. Acceptable actions

`acceptable_actions` should not be too broad.

Check:

- Does each acceptable action correspond to a genuinely valid response?
- Would allowing this action hide a wrong-intent error?
- Is clarification allowed only when intent is genuinely underdetermined?

## 6. Ambiguity metadata

For v0.3+ cases, check:

- `ambiguity_level` is `low`, `medium`, or `high`;
- `pending_context_strength` is `none`, `weak`, or `strong`;
- `expected_action` matches the visible conversation;
- `operation_required` is consistent with the case.

Rule of thumb:

- strong pending context + clear user selection usually means `continue_pending_task`;
- no pending context + isolated fragment usually means `ask_clarification`;
- correction language usually means `acknowledge_correction`.

## 7. Language track check

For translated or mirrored cases:

- preserve the same intended action;
- avoid literal translations that sound unnatural;
- keep ambiguity level comparable;
- document if the mirror is not fully equivalent.

## 8. Red flags

Rewrite or remove cases with:

- multiple unrelated user intents;
- hidden context;
- unnatural puzzle-like phrasing;
- expected behavior that depends on author preference;
- success criteria that reward verbosity instead of action correctness;
- ambiguity that cannot be resolved even by a human reader.

## 9. Final review question

Before accepting a case, ask:

> If the model gives a fluent answer to the wrong implied request, will this case catch it?

If not, the case is probably not testing wrong intent inference strongly enough.
