from abc import ABC, abstractmethod

class BaseBrain(ABC):
    """
    Abstract interface that all OmniDev intelligence providers must implement.
    """
    @abstractmethod
    def ask(self, prompt: str, new_chat: bool = False, file_to_attach: any = None) -> str:
        """
        Sends prompt to the AI model and returns the text response.
        If new_chat is True, forces a fresh conversation session.
        If file_to_attach is provided, attaches the file/code directly.
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """
        Returns True if the backend is connected and ready.
        """
        pass
