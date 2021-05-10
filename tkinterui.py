import threading
import multiprocessing
import functools
import time
from time import perf_counter
from random import randint
import tkinter as tk
from collections import defaultdict


def benchmark(functionCallback):
    """ Returns the start and end time of a function block in addition to its return value
    :param functionCallback: The function will measure the execution time of functionCallback and print it to the console
    :return: returns a tuple of the start and end time of a function block and the value returned by functionCallback
    """

    @functools.wraps(functionCallback)
    def wrapArround(*args, **kwargs):
        start = perf_counter()
        ret = functionCallback(*args, **kwargs)
        end = perf_counter()
        return (start, end), ret

    return wrapArround


@benchmark
def commonTask():
    """ This is the task that will be executed to compare the execution time of 4 threads vs 4 processes
        The function computes 900 random integers
    :return: None
    """
    iterations = 900
    for i in range(iterations):
        print(randint(1, 999999999999999999999))


class UserInterfaceCoparison(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Process vs Thread Comparison")
        self.width = 600
        self.height = 500
        self.geometry("{}x{}".format(self.width, self.height))
        self.create_layout()
        self.mainloop()

    def toggleGraphing(self, event):
        """ Toggles the graphing area in the UI
        :param event: event created by binding the click function to the togglebutton (discarded)
        :return: None
        """
        if not self.toggle1.state:
            self.graphPanel.pack(fill=tk.BOTH, expand=tk.YES)
        else:
            self.graphPanel.pack_forget()

    def create_layout(self):
        """ Creates the UI layout using tkinter
        :return: None
        """
        controlPanel = tk.LabelFrame(self, text='Small Controll Pannel', name="cp")
        controlPanel.pack(fill=tk.X)
        self.toggle1 = ToggleButton(controlPanel)
        self.toggle1.pack(side=tk.RIGHT)
        self.toggle1.bind("<Button-1>", self.toggleGraphing)
        tk.Label(controlPanel, text="Toggle graph visualization:").pack(side=tk.RIGHT)
        tk.Button(controlPanel, name="calltoAction",
                  text="Compare execution time",
                  fg='white', bg='#0052cc',
                  command=self.comparisonFunction).pack(side=tk.LEFT)
        tk.Button(controlPanel, text="Quit", command=self.destroy, fg='red').pack(side=tk.LEFT)

        self.resultsPanel = tk.LabelFrame(self, text='Results', height=100)
        self.resultsPanel.pack(fill=tk.X)

        self.graphPanel = tk.LabelFrame(self, text='Graph')
        # self.graphPanel.pack(fill=tk.BOTH, expand=tk.YES)
        self.canvas = tk.Canvas(self.graphPanel)
        self.canvas.pack(fill=tk.BOTH, expand=tk.YES)

    @benchmark
    def threadExecution(self):
        """ Execute the function commonTask using 4 threads

        :return: Dictionary containing the start and end time of every thread.  [key] = thread identifier
        """
        # Dictionary to store start and end time of each individual thread
        thread_executionTime = defaultdict(tuple)

        # Create 4 threads
        threads = [CustomThread(target=commonTask) for _ in range(4)]
        # Start the 4 threads
        for thread in threads:
            thread.start()
        # Wait for the execution of all 4 threads and get their start and end time
        for thread in threads:
            thread_executionTime[thread.ident] = thread.join()[0]
        return thread_executionTime

    @benchmark
    def processExecution(self):
        """ Execute the function commonTask using 4 processes

        :return: Dictionary containing the start and end time of every process.  [key] = pid
        """
        # Dictionary to store start and end time of each individual process
        process_executionTime = defaultdict(tuple)
        # Create 4 processes
        processess = [CustomProcess(target=commonTask) for _ in range(4)]
        # Start 4 processes
        for process in processess:
            process.start()
        # Wait for the execution of all 4 processes and get their start and end time
        for process in processess:
            process_executionTime[process.pid] = process.join()
        return process_executionTime

    def convertRange(self, value, largestStart, lowerStart):
        """ Synchronize the start time of 2 functions with different starting times
            Returns the value of a given event as if the 2 functions started at the same time
        example:    0 1 2 3 4 5 6 7 8 9
        range1:     * - - - e - - *
        range2:             * - - - - *

        Align:      * - - - e - - *
                    * - - - - *
        would return value 4

        :param value: Value to be converted to the different range
        :param largestStart: Start time of a function with the latest start time
        :param lowerStart: Start time of a function with the earliest start time
        :return: Value of an event as if both functions started at the same time
        """
        return float(value) - (float(largestStart) - float(lowerStart))

    def mapRanges(self, value, timeStart, timeEnd, windStart, windEnd):
        """ Maps a value in one range to a second range

        :param value: Value to be converted
        :param timeStart: input lower bound
        :param timeEnd: input upper bound
        :param windStart: output lower bound
        :param windEnd: output upper bound
        :return: Value converted to the output's range
        """
        return (float(value - timeStart) / float(timeEnd - timeStart)) * float(windEnd - windStart) + windStart

    def comparisonFunction(self):
        # Disables Call To Action Button
        ctaButton = self.nametowidget('cp.calltoAction')
        ctaButton.configure(state=tk.DISABLED)

        # Run commonTask with 4 threads
        threadResults, thrSubTimes = self.threadExecution()
        # Run commonTask with 4 processes
        processResults, procSubTimes = self.processExecution()

        # Get the execution times for the whole execution block
        threadExecutionTime = threadResults[1] - threadResults[0]
        processExecutionTime = processResults[1] - processResults[0]

        # Format execution time to a nice and readable string
        threadResultToString = "Threads execution time: {:f} s".format(threadExecutionTime)
        processResultToString = "Processes execution time: {:f} s".format(processExecutionTime)

        # Create or Update the result labels
        if self.resultsPanel:
            children = self.resultsPanel.winfo_children()
            if len(children) >= 2:
                threadLabel = self.resultsPanel.nametowidget("threadResults")
                processLabel = self.resultsPanel.nametowidget("processResults")

                threadLabel.configure(text=threadResultToString)
                processLabel.configure(text=processResultToString)
            else:
                tk.Label(self.resultsPanel, text=threadResultToString, name="threadResults").pack(anchor=tk.W)
                tk.Label(self.resultsPanel, text=processResultToString, name="processResults").pack(anchor=tk.W)

        isThreadFaster = processExecutionTime > threadExecutionTime
        # Get the start and end time of the slowest code block
        largestRange = processResults if isThreadFaster else threadResults
        if isThreadFaster:
            largestRange = (self.convertRange(largestRange[0], processResults[0], threadResults[0]),
                            self.convertRange(largestRange[1], processResults[0], threadResults[0]))

        # Get the end time of the fastest code block
        timeOfFastestEnd = threadResults[1] if isThreadFaster else\
            self.convertRange(processResults[1], processResults[0], threadResults[0])

        # Responsible for painting the graph and comparing the threaded code block as if it started at the same
        # time as the process code block.
        if self.toggle1.state:
            self.canvas.delete(tk.ALL)  # Erases the canvas
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()

            graph_width = canvas_width - 90
            graph_height = canvas_height - 50

            bar_height = graph_height / 8
            # Creates the graphing area
            self.canvas.create_rectangle(80, 10, canvas_width - 10, canvas_height - 40)
            # Creates the labels for threads and processes
            for i in range(8):
                labelType = "Process" if i > 3 else "Thread"
                self.canvas.create_text(40,
                                        bar_height * i + bar_height / 2 + 10,
                                        text="{} {}".format(labelType, i - 4 if i > 3 else i))

            # Draw the bars for each thread
            for i, threadIdentifier in enumerate(list(thrSubTimes.keys())):

                startYpos = bar_height * i + 10
                endYpos = startYpos + bar_height
                startXpos = self.mapRanges(thrSubTimes[threadIdentifier][0], largestRange[0], largestRange[1], 80, graph_width + 80)
                endXpos = self.mapRanges(thrSubTimes[threadIdentifier][1], largestRange[0], largestRange[1], 80, graph_width + 80)
                self.canvas.create_rectangle(startXpos, startYpos, endXpos, endYpos, fill='red')

            # Draw the bars for each process
            for i, pid in enumerate(list(procSubTimes.keys())):
                convertedStartTime = self.convertRange(procSubTimes[pid][0], processResults[0], threadResults[0])
                convertedEndTime = self.convertRange(procSubTimes[pid][1], processResults[0], threadResults[0])

                startYpos = bar_height * (i + 4) + 10
                endYpos = startYpos + bar_height
                startXpos = self.mapRanges(convertedStartTime, largestRange[0], largestRange[1], 80, graph_width + 80)
                endXpos = self.mapRanges(convertedEndTime, largestRange[0], largestRange[1], 80, graph_width + 80)
                self.canvas.create_rectangle(startXpos, startYpos, endXpos, endYpos, fill='blue')
            # Get X coordinate for the end of execution of the fastest block
            endOfFastest = self.mapRanges(timeOfFastestEnd, largestRange[0], largestRange[1], 80, graph_width + 80)
            # Draws green line to demonstrate the end of the fastest code block
            self.canvas.create_line(endOfFastest,  # x0
                                    10,  # y0
                                    endOfFastest,  # x1
                                    graph_height + 10,  # y1
                                    fill='green',
                                    dash=(4, 1),
                                    width=3)
        # Reactivate cta button
        ctaButton.configure(state=tk.NORMAL)


class ToggleButton(tk.Button):
    """ Custom made toggle button layout"""
    def __init__(self, master=None, bd=0, **kwargs):
        super().__init__(master, bd=bd, command=self.onClick, **kwargs)
        self.state = False
        self.toggleImage = [tk.PhotoImage(file="./images/toggleOff.png"), tk.PhotoImage(file="./images/toggleOn.png")]
        self.config(image=self.toggleImage[self.state])

    def onClick(self):
        """ Toggle onClick event
        :return: None
        """
        self.state = not self.state
        self.config(image=self.toggleImage[self.state])


class CustomThread(threading.Thread):
    """ Special thread implementation for getting execution time"""
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs=None, daemon=None):
        super().__init__(group=group, target=target, name=name, args=args, kwargs=kwargs, daemon=daemon)
        self.returnValue = None

    # Overwrite run method
    def run(self):
        try:
            if self._target:
                self.returnValue = self._target(*self._args, **self._kwargs)
        finally:
            # Avoid a refcycle if the thread is running a function with
            # an argument that has a member that points to the thread.
            del self._target, self._args, self._kwargs
    # Overwrite join method
    def join(self):
        super().join()
        return self.returnValue


class CustomProcess(multiprocessing.Process):
    """Special process implementation to get execution time"""
    def __init__(self, group=None, target=None, name=None, args=(), kwargs={}, daemon=None):
        super().__init__(group=group, target=target, name=name, args=args, kwargs=kwargs, daemon=daemon)
        self.startTime = 0
        self.endTime = 0
        self.returnValue = None
    # Overwrite start method
    def start(self):
        self.startTime = perf_counter()
        super().start()
    # Overwrite join method
    def join(self):
        super().join()
        self.endTime = perf_counter()
        return self.startTime, self.endTime


if __name__ == '__main__':
    ui = UserInterfaceCoparison()
