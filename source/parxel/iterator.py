class Iterator:
    def __init__(self, iterable: list):
        self.buffer : list = iterable
        self.pos : int = 0
        self.beg : int = 0
        self.end : int = len(self.buffer)

        if self.end > 0:
            self.el = self.buffer[0]

    def __bool__(self) -> bool:
        return self.pos < self.end

    def __getitem__(self, index: int):
        if not self or index >= self.end:
            return None

        return self.buffer[index]

    def get(self):
        if not self:
            return None

        self.el = self.buffer[self.pos]
        return self.el

    def next(self):
        self.pos += 1

        return self.get()
    
    def prev(self):
        if self.pos > 0:
            self.pos -= 1

        return self.get()

    def advance(self, distance: int):
        el = None
        for _ in range(distance):
            el = self.next()
        return el

    def peek(self, distance: int = 1) -> list | None:
        if self.pos + distance < self.end:
            return self.buffer[self.pos + distance]
        return None
    
    def consume(self, el) -> bool:
        if self.buffer[self.pos] == el:
            self.next()
            return True
        return False

    def consume_any(self, el : list) -> bool:
        if self.buffer[self.pos] in el:
            self.next()
            return True
        return False

    def consume_until(self, el):
        while self and self.buffer[self.pos] != el:
            self.next()

    def consume_until_any(self, el : list):
        while self and self.buffer[self.pos] not in el:
            self.next()

    def consume_while(self, el):
        while self and self.buffer[self.pos] == el:
            self.next()

    def consume_while_any(self, el : list):
        while self and self.buffer[self.pos] in el:
            self.next()
