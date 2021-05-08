import threading
import multiprocessing
import functools
from time import perf_counter, perf_counter_ns, sleep
from random import randint

"""                                        PROGRAM CHALLENGE
Threads vs. Concurrent Processes

The challenge is to write a Python script to do some Benchmarking. You'll need to use some form of time to grab the time at the start of a code block and the end of the code block. Then, the difference between the two times shows us the speed of execution of this block.

The goal is to measure and compare two methodologies of spawning code to execute from the current script.

In the first block, have your code spawn four threads and measure their parallel execution.  You can measure from start (before first thread started) to finish (after last thread is done).  Each thread should only need to print something out, no need to get too crazy.

In the second block, use a different methodology to run four concurrent processes.  These will be actual processes, so you have to learn about how to make the system call.  Again, these processes should do the exact same thing as the four threads you created in block one.   Again, measure start-to-finish of the four, and report the time.

Finally, print out the comparison of time used.

Questions:   Let me know.
Consult the Internet.  Consult books.   Please do not consult people.   The idea is to assess where you are with Python.
"""


# Wrapper function created to comply with DRY (Do not repeat yourself) principle
def benchmark(functionCallback):
    """ Calculates the execution time of a given function in seconds
    :param functionCallback: The function will measure the execution time of functionCallback and print it to the console
    :return: returns a tuple of the execution time and the value returned by functionCallback
    """

    @functools.wraps(functionCallback)
    def wrapArround(*args, **kwargs):
        countStart = perf_counter()
        ret = functionCallback(*args, **kwargs)
        countEnd = perf_counter()
        execTime = countEnd - countStart
        print("Execution time in seconds: {:f} s".format(execTime))
        return execTime, ret

    return wrapArround


def func_to_test(type, index, iterationsOrDelay, lock, mockTime: bool = False):
    """ This function will compute 900 random integers or mock a delay between 1 and 5 seconds
    :param type: Process || Thread
    :param index: Index of current thread or process
    :param iterationsOrDelay: Number of iterations or value of the random delay value to simulate heavy processing
    :param lock: Lock for printing each line without other thread interruptions
    :param mockTime: Defines if the function will use a random delay or compute <iterationsOrDelay> random integers
    :return: None
    """
    if mockTime:
        sleep(iterationsOrDelay)
        with lock:  # Use lock to ensure that each print is in a new line
            print("Thread {}:  random delay of {}".format(index, iterationsOrDelay))
    else:
        for i in range(iterationsOrDelay):
            randomInteger = randint(1, 999999)
            with lock:  # Use lock to ensure that each print is in a new line
                print("{} {}: {}".format(type, index, randomInteger))


@benchmark
def firstBlock(mockExecutionTime: bool = False):
    """ Creates 4 threads that execute "func_to_test" in parallel and returns the string "Return Some Value"
    :param mockExecutionTime: if true will create a random small delay for each thread to simulate processing time
    :return: Returns "Return Some Value"
    :rtype: str
    """
    listOfThreads = []
    # Create a lock so that the print statement cannot be interrupted during context switches
    printLock = threading.Lock()
    # If mock value is false it will compute 900 random integers
    iterations = 0 if mockExecutionTime else 900
    # Creates 4 threads, start them  and save them into a list of threads.
    for i in range(4):
        # If mock value is true computes a random time delay for each thread
        delay = randint(1, 5) if mockExecutionTime else 0
        thread = threading.Thread(target=func_to_test,
                                  args=("Thread", i, delay | iterations, printLock),
                                  kwargs={'mockTime': mockExecutionTime})
        thread.start()
        listOfThreads.append(thread)

    # Waits until all threads finish
    for thread in listOfThreads:
        thread.join()

    # Returns the following string just to demonstrate that the the wrapper function can handle return values
    return "Returned Some Value"


@benchmark
def secondBlock(mockExecutionTime: bool = False):
    """ Creates 4 subprocesses that execute "func_to_test" in parallel
    :param mockExecutionTime:
    :return: None
    """
    listOfProcesses = []
    iterations = 0 if mockExecutionTime else 900
    printLock = multiprocessing.Lock()
    for i in range(4):
        delay = randint(1, 5) if mockExecutionTime else 0
        process = multiprocessing.Process(target=func_to_test,
                                          args=("Process", i, delay | iterations, printLock),
                                          kwargs={'mockTime': mockExecutionTime})
        process.start()
        listOfProcesses.append(process)

    for process in listOfProcesses:
        process.join()

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # This code creates 4 threads that print values to the console and then prints the total execution time
    # If you pass True as a parameter each thread will have a delay between 1 and 5 seconds.
    #       In this case, the execution time should be similar to the thread with the largest delay.
    firstBlockExecTime, ret = firstBlock()
    # Proof that we still have access to the return value of the firstBlock function
    print(ret)

    secondBlockExecTime, _ = secondBlock()

    print("-------------------------------------------\n"
          "Threads execution time in seconds: {:f} \n"
          "Processes execution time in seconds: {:f}".format(firstBlockExecTime, secondBlockExecTime))
