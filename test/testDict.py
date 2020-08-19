class State(object):
    REJECTED = 0  # Order has been rejected.
    PENDING = 1  # Initial state.
    SENT = 2  # Order has been submitted.
    ACCEPTED = 3  # Order has been acknowledged by the broker.
    CANCELED = 4  # Order has been canceled.
    PARTIALLY_FILLED = 5  # Order has been partially filled.
    FILLED = 6  # Order has been completely filled.


VALID_TRANSITIONS = {
    State.PENDING: [State.SENT, State.CANCELED],
    # Add filled transition
    State.SENT: [State.ACCEPTED, State.CANCELED, State.FILLED],
    State.ACCEPTED: [State.PARTIALLY_FILLED, State.FILLED, State.CANCELED],
    State.PARTIALLY_FILLED: [State.PARTIALLY_FILLED, State.FILLED, State.CANCELED],
}
validTransitions = VALID_TRANSITIONS.get(State.PENDING)
print(validTransitions)