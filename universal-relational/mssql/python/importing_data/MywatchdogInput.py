# import time module, Observer, FileSystemEventHandler
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import inputOne

class OnMyWatch:
    # Set the directory on watch
    watchDirectory = "C:/temp"

    def __init__(self):
        self.observer = Observer()

    def run(self):
        event_handler = Handler()
        self.observer.schedule(event_handler, self.watchDirectory, recursive=True)
        self.observer.start()
        try:
            while True:
                time.sleep(5)
        except:
            self.observer.stop()
            print("Observer Stopped")

        self.observer.join()


class Handler(FileSystemEventHandler):

    @staticmethod
    def on_any_event(event):
        if event.is_directory:
            return None

        elif event.event_type == 'created':
            inputOne.input(event.src_path.replace('\\','/'))
            #print("Watchdog received created event - % s." % event.src_path.replace('\\','/'))

if __name__ == '__main__':
    watch = OnMyWatch()
    watch.run()