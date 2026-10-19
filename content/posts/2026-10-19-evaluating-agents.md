---
title: "Agentic Evaluation is more manual than I thought"
description: "Golden datasets, oracles, and the unglamorous work of deciding what a right answer looks like."
---

For most of this year I've been helping build a team of LLM agents: a supervisor that routes questions to a handful of specialist sub-agents, each with its own tools for querying databases, searching documents, and so on. Going in, I assumed evaluation would be the part we could mostly automate. There's no shortage of eval frameworks, and the LLM-as-judge pattern makes it sound like you can just point one model at another and get a score.

That's half true. The scoring is automated. Deciding what *correct* means, case by case, is not, and that turned out to be most of the work.

## The golden dataset

The backbone of our setup is a **golden dataset** per agent: a JSON file of realistic questions, each one pinned to what a good response looks like. A single case carries:

- **The prompt**, plus any context the agent would normally have (who's asking, what they're allowed to see, prior conversation turns).
- **The expected tool** the agent should reach for, and sometimes the parameters it should pass.
- **A few must-have strings** the answer has to contain: a name, a value, an identifier.
- **A reference answer** to compare against.
- **Which judge criteria apply**: correctness, faithfulness to the tool output, instruction following, conciseness, or whether it should refuse the request entirely.

Every one of those fields is a judgment call somebody has to make by hand. Which questions are worth asking? What's the minimum set of facts that makes an answer right, versus things that are just nice to include? Should an ambiguous question get a clarifying question back, or a best guess? Is this a question the agent should refuse? None of that comes out of a framework; it comes out of someone who knows the domain sitting down and writing it.

We ended up with two flavors of cases. **Production-derived** ones come from real questions people asked, cleaned up and turned into test cases; these keep us honest about what users actually do. **Synthetic** ones are edge cases we invented on purpose (malformed inputs, out-of-scope asks, users without permission to see something) because real traffic rarely hits them until it does.

## The oracle problem

In software testing, the *oracle* is whatever tells you the right answer. For a calculator, it's arithmetic. For an agent, it's... a person, mostly.

The first thing I learned here is that you can't shortcut the oracle. Early on, some of our reference answers were generated from a template: "Based on a search for X, here is the relevant information, key items: A, B, C." It looks like a reference answer, it fills the field, and it's close to useless. The embedding similarity check happily compares the agent's response to a paragraph that doesn't actually say anything, and you get a score that measures phrasing, not correctness. A real reference answer means someone actually ran the query or read the document and wrote down what the answer *is*. In practice, a lot of our cases still skip the similarity check entirely because nobody has written that answer yet. It's the most tedious field to fill in, so it's the one that lags.

The second thing: for agents that query live data, the oracle goes stale. "How many X happened last week" has a different correct answer every week. You either pin the test to a fixed historical window, lean on the must-have strings for things that don't change (the right table, the right units, the right entity), or accept that the reference answer needs maintenance like any other code. We do some of each, and I'm not convinced we've found the right balance yet.

The third thing is that the LLM judge is only as good as what you show it. We originally told the judge which tool the agent was *supposed* to use, even on cases where we only asked it to grade helpfulness. The judge would then try to infer from the prose whether the agent had used the tool, guess wrong, and fail perfectly good answers. Detailed, well-grounded answers ended up scoring *worse* than hedgy ones. The fix was to only mention tools when a tool criterion is actually being scored, and to pass the judge the real list of tools the agent called instead of letting it guess. The judge needs its own oracle, basically.

## Four checks, cheapest first

With a golden dataset in hand, each case gets scored four ways:

1. **Tool selection**: did the agent call the expected tool? Deterministic and free, and it catches the most common regression, which is a prompt tweak that quietly breaks routing.
2. **Must-have strings**: are the non-negotiable facts in the answer? Dumb and brittle (it doesn't know "five" and "5" are the same thing), but a great tripwire for a beautifully formatted answer that never actually looked anything up.
3. **Embedding similarity**: is the response semantically close to the reference answer? Handles rewording, but only as good as the reference.
4. **LLM-as-judge**: would a careful reviewer sign off on it, against the criteria chosen for that case?

Each one covers a blind spot in the others, and when something fails, the combination usually points at *what* broke: routing, retrieval, or reasoning. These run on a git pre-push hook for whichever agents you touched, and again after each deploy to our dev environment.

## So what's actually manual?

Almost everything upstream of the score. Writing the questions, deciding the expected tool, picking the must-have facts, writing (and re-writing) the reference answers, choosing which criteria apply, and then, when a case fails, figuring out whether the agent got worse or the test was wrong. That last one happens more than I expected; a fair share of "failures" have been the golden dataset being too strict or out of date.

I don't think that's a flaw in the approach. The golden dataset is where your team's definition of "good" actually lives, and it's worth the time precisely because nobody else can write it for you. If I were starting over I'd build it on day one, and budget for it like a feature instead of a chore.

If you've found a better way to build or maintain oracles for agents, especially ones sitting on top of live data, I'd love to hear about it.
