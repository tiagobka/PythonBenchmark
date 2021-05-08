# Program Challenge

[![Language](https://img.shields.io/badge/Language-Python-blue)](http://doge.mit-license.org)

## Threads vs. Concurrent Processes

The challenge is to write a Python script to do some Benchmarking. You'll need to use some form of time to grab the time at the start of a code block and the end of the code block. Then, the difference between the two times shows us the speed of execution of this block.

The goal is to measure and compare two methodologies of spawning code to execute from the current script.

In the first block, have your code spawn four threads and measure their parallel execution.  You can measure from start (before first thread started) to finish (after last thread is done).  Each thread should only need to print something out, no need to get too crazy.

In the second block, use a different methodology to run four concurrent processes.  These will be actual processes, so you have to learn about how to make the system call.  Again, these processes should do the exact same thing as the four threads you created in block one.   Again, measure start-to-finish of the four, and report the time.

Finally, print out the comparison of time used.

Questions:   Let me know.
Consult the Internet.  Consult books.   Please do not consult people.   The idea is to assess where you are with Python.

### Prerequisites
- Python 3.7

### Packages
    This script does not require any aditional package installation
**Packages used:**
- threading
- functools
- time
- random