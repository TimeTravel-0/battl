# battl
read /proc and /sys/class/power_supply to generate some stats and charts

there are various tools (htop, top, ps, powertop, xfce power applet, ...) that allow insight of the load and battery state on a linux laptop. Gnome-Battery-Bench allows benchmarking of the battery under various loads.

This script(s) read the available raw data from the /proc and /sys directories and handle the available data directly.

Data readout works ok-ish, stats (and estimations/extrapolations) are todo.
