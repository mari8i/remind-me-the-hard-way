# remind-me-the-hard-way

Automatically opens video conferences based on a google calendar.

## Setup on MAC.OS

Add the `credentials.json` file in the project folder, ask to AM or LR for it.

Change `CALENDAR_ID` constant in main.py:24 with your calendar ID.

Then:
- start `Automator.app`
- select `Application`
- navigate to `library/Utilities` and add `Run shell script`, otherwise search for it
- copy & paste your script into the window

_something like this_

```
#!/bin/bash
(
   cd /Users/rivareus24/PycharmProjects/remind-me-the-hard-way
   source ./venv/bin/activate
   python3 main.py
)
```

- test it
- save somewhere (for example you can make an Applications folder in your HOME, you will get an your_name.app)
- go to `System Preferences` -> `Users & Groups` -> `Login items` (or System Preferences -> Accounts -> Login items / depending of your MacOS version)
- add this app
- test & done ;)
---
