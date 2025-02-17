from abc import ABC, abstractmethod

class Notifier(ABC):
    @abstractmethod
    def send_notification(self, message: str, target: str):
        pass

    def send_notifications(self, message: str, targets: list):
        for target in targets:
            self.send_notification(message, target) 