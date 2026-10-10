Change how the container counts is recorded, should also probably store the session ids to kill them in the case of relaunching sessions.
If we skip the containers' creation that's only if its 10, if not then we need to kill all sessions matching the type.

abort workflow configs stop `name` `id`

sessions submodule:
- list: list all headless sessions
  - health: check the health of the sessions? maybe we make it in list?
- create: create headless session for specific payload
- delete: delete all sessions related to some payload or just one session?