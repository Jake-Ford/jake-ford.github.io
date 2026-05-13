---
title: "Are Court-Ordered Districts More Fair?"
description: "A look at redistricting outcomes when judges, not legislatures, draw the maps."
---

Deja-vu! The North Carolina Supreme Court rejected the maps that I previously analyzed, instead opting to use [maps](https://www.ncleg.gov/Redistricting) drawn by outside experts. Wowza! Let's, hopefully one last time, see how these maps compare to the 2010–2019 maps, the initially suggested redistricting by the General Assembly, the February update post the initial legal challenge, and now the court-ordered drafted lines.

The state house and state senate maps are final — only the congressional maps are being altered. I didn't know that until I added the new maps (February in click option) to the below. If you don't believe me, just find out for yourself.

## Summary Stats

We'll make the same summary stats to start. Notice how the February updated lines seem to be a large improvement in racial parity — Blacks were nearly twice as likely to be represented by a Democrat with the 2010–2019 congressional lines; in the February update it's almost even. This process requires tagging each of the nearly quarter million census blocks in North Carolina to the congressional district represented.

## Logistic Regression Curve

Let's see if the new lines hold up with the logistic model, determining how likely a particular demographic is to be represented by a Democrat (note: 1 on the y-axis = probability Republican). Black and Asian populations are more likely to be represented by Republicans in large numbers in the February update. Note how at the very end of the logistic curve, in those census blocks with 90–95% racial homogeneity, the likelihood of being represented by a Democrat is far less likely compared to the 2010–2019 or 2021 proposed districts. This only holds for Black populations as you can see below.

## Model Fits

The logistic model fit in the 2010–19 districts was a paltry 71.1%, drastically improved upon by the 2021 struck-down lines — up to 88.3%. The February lines are in the middle, at 82.6%; meaning this simple logistic model, fed with nearly a quarter million census block values, developed into a machine learning algorithm that could predict with 82.6% accuracy the political representation of a district based solely on racial makeup.

## Random Forest

Finally, let's see the predictive fit for all four.

## Conclusion
