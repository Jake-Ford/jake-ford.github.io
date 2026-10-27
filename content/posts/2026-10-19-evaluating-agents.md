---
title: "Agentic Evaluation is more manual than I thought"
description: "Notes from a year of building LLM agents at work, and figuring out what a right answer even is."
---

For most of this year my team at FlexGen has been building LLM agents - a supervisor that hands questions off to a few specialist agents, each with its own tools for pulling data and searching docs. Going in, I figured evaluation would be the easy part. There are a million eval frameworks out there, and LLM-as-judge makes it sound like you just point one model at another and get a score back. There are even [built in](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/built-in-evaluators-overview.html) and FREE evaluators within AWS AgentCore.

The scoring is automated, sure. Deciding what *correct* actually means, one question at a time, is not, and that ended up being most of the work.

Our setup is pretty standard: a "golden dataset" per agent (realistic questions, the tool it should reach for, a few facts the answer has to include, and a reference answer), then a stack of checks run cheapest first - right tool? facts in there? close to the reference? would an LLM judge sign off? A few things surprised me:

1. **You can't fake the reference answer.** Early on some of ours were basically templates - "based on a search for X, here's what I found: A, B, C." It fills the field, but the similarity check ends up scoring phrasing instead of correctness. A real reference means somebody actually ran the query and wrote down the answer, which is tedious, so it's always the field that lags.

2. **The right answer goes stale.** "How many X happened last week" has a different answer every week. We pin some tests to fixed time windows and lean on facts that don't move for others; I'm honestly not sure we've found the right balance yet.

3. **The judge needs context too.** We used to tell the judge which tool the agent was *supposed* to use, even when it was only grading helpfulness. It would try to guess from the prose whether the tool got called, guess wrong, and fail perfectly good answers - so detailed answers were scoring worse than hedgy ones. The fix was to only mention tools when we're grading tools, and hand the judge the actual list of what got called.

4. **A lot of failures are the test's fault.** When something fails, half the job is figuring out whether the agent got worse or the golden dataset is too strict or out of date. More often than I'd like, it's the dataset.

None of this feels like a flaw in the approach - the golden dataset is where your team's definition of "good" actually lives, and nobody else can write it for you. If I were starting over I'd build it on day one and budget time for it like any other feature.

If you've found a better way to do this, especially for agents sitting on top of live data, I'd love to hear it.
