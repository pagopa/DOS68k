# Chatbot Evaluate API

The entry point for measuring answer quality. It records user feedback on
answers and accepts requests to run automatic quality evaluation.

For the big picture, see [Overview](../../docs/overview.md). For settings, see
[Configuration](../../docs/configuration.md#evaluation--api).

## Role in the platform

This service does two things:

- **Feedback.** Records a simple thumbs-up / thumbs-down on a given answer. Any
  User can rate their own answers.
- **Evaluation.** Accepts a request to evaluate one answer, or a batch of
  answers in a Session, and places jobs on the evaluation queue. The actual
  scoring is done in the background by the
  [evaluate worker](../worker/README.md); this service returns immediately.
  Evaluation is **Admin-only**.

Both feedback and evaluation results are stored on the Query records (in the
same `queries` table the chatbot writes), so they show up alongside the answer.

## What to watch

- A batch "evaluate all" request is capped at `EVALUATE_UPPER_LIMIT` queries,
  prioritising answers that already have user feedback.
- Evaluation runs on its **own queue**, separate from document indexing — see
  [Configuration: queue separation](../../docs/configuration.md#queue-separation).
</content>
