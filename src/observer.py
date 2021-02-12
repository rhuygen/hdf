import abc


class Observer(abc.ABC):
    @abc.abstractmethod
    def update(self, changed_object):
        pass

    @abc.abstractmethod
    def do(self, actions):
        pass


class Observable:
    def __init__(self):
        self.observers = []

    def addObserver(self, observer):
        if observer not in self.observers:
            self.observers.append(observer)

    def deleteObserver(self, observer):
        self.observers.remove(observer)

    def clearObservers(self):
        self.observers = []

    def countObservers(self):
        return len(self.observers)

    def notifyObservers(self, changedObject):
        for observer in self.observers:
            observer.update(changedObject)

    def actionObservers(self, actions):
        for observer in self.observers:
            observer.do(actions)
