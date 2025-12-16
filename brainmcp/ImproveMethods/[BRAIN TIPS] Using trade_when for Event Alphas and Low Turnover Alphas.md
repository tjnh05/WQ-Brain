[BRAIN TIPS] Using trade_when for Event Alphas and Low Turnover Alphas
Followed by 50 people

KA64574
3 years ago
You can use the following targeting to create event-driven alphas and low turnover alphas.

Concept:
If (event) {
Assign alpha values;
} else {
Hold alpha values;
}
Expression:

trade_when(Event_condition, Alpha_expression, -1)

Pros:

Good alpha coverage
Flexible in determining events
Can be used to enhance signals by trading at the right time
Low turnover and low cost alpha

 

Cons:

Not easy to get high Sharpe alpha
Not easy to get high return alpha

Approach:
Define events: Any spike in returns, data values and technical indicators can be used to define events.
Alpha assignment: Look for signals that are aligned with the abnormality of an event — that is, alphas that need to be executed when such events happen.

Note:
Hold alpha can be replaced by decaying alpha linearly or exponentially.
Check alpha coverage to make sure events are not so rare.