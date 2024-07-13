class SlidingWindowAverageCooling(object):
    """
    docstring
    """

    def __init__(self, sp, threshold, cb_above, cb_below, sample_count, mock_outputs=True):
        self.sp = sp
        self.threshold = threshold
        self.cb_above = cb_above
        self.cb_below = cb_below
        self.sample_count = sample_count
        self.mock = mock_outputs

        self.samples = [None] * sample_count
        self.index = 0

        self.mode = "off"

    def increment_index(self):
        """
        Wrap the index around the circular buffer.
        """
        if self.index >= self.sample_count - 1:
            self.index = 0
        else:
            self.index += 1

    def clear_buf(self):
        for i in range(len(self.samples)):
            self.samples[i] = None

    def update(self, sample):
        self.samples[self.index] = sample
        self.increment_index()

        sum = 0
        for x in self.samples:
            if isinstance(x, (int, float)):
                sum += x
            else:
                return None

        avg = sum / float(len(self.samples))

        if avg > self.sp:
            print("Cooling Needed")
            self.mode = "on"
        elif avg < (self.sp - self.threshold):
            print("Cooling Off")
            self.mode = "off"
        else:
            print("Threshold")


        if self.mode == "on":
            if not self.mock:
                self.cb_above()

        elif self.mode == "off":
            if not self.mock:
                self.cb_below()
