from typing import Optional
from utils.common import abbr_to_jid, states, sessions_with_bills


def yield_state_sessions(state: str, session: Optional[str]):
    """
    parse provided options to get a list of sessions to process
    """
    if state == "all" or state == "all_sessions":
        scrape_state = state
        for state in states:
            sessions = sorted(
                s.identifier for s in sessions_with_bills(abbr_to_jid(state.abbr))
            )
            if len(sessions) > 0:
                state = state.abbr.lower()
                if scrape_state == "all_sessions":
                    for session in sessions:
                        yield state, session
                else:
                    session = sessions[-1]
                    yield state, session
    elif session:
        # state and session, yield once
        yield state, session
    else:
        # single state
        sessions = sorted(s.identifier for s in sessions_with_bills(abbr_to_jid(state)))
        for session in sessions:
            yield state, session
