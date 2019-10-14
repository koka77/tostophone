import threading
from array import array
from Queue import Queue, Full
from subprocess import call

import pyaudio


CHUNK_SIZE = 256
MIN_VOLUME = 30000
# if the recording thread can't consume fast enough,
# the listener will start discarding
BUF_MAX_SIZE = CHUNK_SIZE * 10


def main():
    stopped = threading.Event()
    q = Queue(maxsize=int(round(BUF_MAX_SIZE / CHUNK_SIZE)))

    listen_t = threading.Thread(target=listen, args=(stopped, q))
    listen_t.start()
    record_t = threading.Thread(target=record, args=(stopped, q))
    record_t.start()

    try:
        while True:
            listen_t.join(0.1)
            record_t.join(0.1)
    except KeyboardInterrupt:
        stopped.set()

    listen_t.join()
    record_t.join()


def record(stopped, q):
    while True:
        if stopped.wait(timeout=0):
            break
        chunk = q.get()
        vol = max(chunk)
        if vol >= MIN_VOLUME:
            print vol,
            # call(['gphoto2', '--port', 'usb:', '--capture-image'])
        else:
            print "-",


def listen(stopped, q):
    stream = pyaudio.PyAudio().open(
        format=pyaudio.paInt16,
        channels=1,
        rate=44100,
        input=True,
        input_device_index = 2
        frames_per_buffer=CHUNK_SIZE
    )

    while True:
        if stopped.wait(timeout=0):
            break
        try:
            q.put(array('h', stream.read(CHUNK_SIZE, exception_on_overflow = False)))
        except Full:
            pass  # discard


if __name__ == '__main__':
    main()