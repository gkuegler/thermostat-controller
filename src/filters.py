class SlidingAverage():
    def __init__(self, sample_count) -> None:
        self.sample_count = sample_count
        self.samples = [None]*sample_count
        self.index = 0

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
        """
        Return the average temperature across the last (3) samples.
        """
        self.samples[self.index] = sample
        self.increment_index()
        sum = 0
        for x in self.samples:
            if isinstance(x, (int, float)):
                sum += x
            else:
                return None
        return sum/float(len(self.samples))