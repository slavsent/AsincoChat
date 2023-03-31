def fizzbuzz(fizz, buzz):
    for el in range(1, 100):
        if el % fizz == 0 and el % buzz == 0:
            yield f'{el} fizzbuzz'
        elif el % fizz == 0:
            yield f'{el} fizz'
        elif el % buzz == 0:
            yield f'{el} buzz'
        else:
            yield el


for i in fizzbuzz(fizz=3, buzz=5):
    print(i)


class PlayFizzbuzz:

    def play_result(self, fizz, buzz):
        self.fizz = fizz
        self.buzz = buzz
        for el in range(1, 100):
            if el % self.fizz == 0 and el % self.buzz == 0:
                yield f'{el} fizzbuzz'
            elif el % self.fizz == 0:
                yield f'{el} fizz'
            elif el % self.buzz == 0:
                yield f'{el} buzz'
            else:
                yield el


for i in PlayFizzbuzz().play_result(4, 6):
    print(i)
