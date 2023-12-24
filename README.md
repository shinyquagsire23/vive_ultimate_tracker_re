# vive_ultimate_tracker_re

Current status:

- Figured out how to trigger "PCVR" mode and get 3DoF (rotation) tracking via USB HID (connected directly to trackers)
- Figured out how to pair multiple trackers to the Dongle
- Receiving "ack" messages from multple trackers at once

TODO:

- Figure out how to activate "PCVR" mode for the RF protocol
- Figure out how to get 6DoF/SLAM-active tracking for either direct USB or RF

## Files

- `hid_test.py` - Testing the USB HID protocol connected directly to the tracker, no RF/wireless
- `rf_hid_test.py` - Testing the USB HID protocol for the wireless dongle itself, and hopefully wireless comms w/ the trackers.