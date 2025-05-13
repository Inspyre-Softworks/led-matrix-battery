class Animation:
    def __init__(self, frame_data: list[dict], fallback_frame_duration=.33):
        self.__frames                  = None
        self.__cursor                  = None
        self.__fallback_frame_duration = None

    @property
    def cursor(self):
        return self.__cursor or 0

    @cursor.setter
    def cursor(self, new):
        if not isinstance(new, int):
            raise TypeError("Cursor must be an integer")

        if new < 0 or new >= len(self.frames):
            raise IndexError("Cursor out of bounds")

        self.__cursor = new

    @property
    def fallback_frame_duration(self):
        return self.__fallback_frame_duration or .33

    @fallback_frame_duration.setter
    def fallback_frame_duration(self, new):
        if not isinstance(new, (float, int)):
            raise TypeError("Fallback frame duration must be a float or integer!")

        self.__fallback_frame_duration = new

    @property
    def frames(self):
        return self.__frames

    def play(self):
        for frame in self.frames:
            frame.play()
