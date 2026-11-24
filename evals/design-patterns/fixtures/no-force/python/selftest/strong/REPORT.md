I'd hold off on both. `Invoice` has three required fields and is built in exactly one place, `create_invoice`, with a plain constructor. A factory would only wrap that call, and a builder solves many optional fields or step-by-step construction, which this doesn't have. Neither has a force here, so each would add a class to maintain with no benefit.

What would justify them later: a builder if Invoice gains several optional fields (discounts, tax lines, notes); a factory if there are different kinds of invoice to choose between at runtime, or construction moves to more than one place. If you have one of those coming, tell me and I'll add the lightest version for it.

No code changed.
