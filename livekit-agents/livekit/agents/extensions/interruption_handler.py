import os
import logging

logger = logging.getLogger("interruption-handler")
logger.setLevel(logging.INFO)

IGNORED_WORDS = os.getenv("IGNORED_WORDS", "uh,umm,hmm,haan").split(",")

class InterruptionHandler:
    """
    Filters out filler words when the agent is speaking.
    """

    def __init__(self):
        self.agent_speaking = False

    async def on_agent_speaking(self, speaking: bool):
        """Called when the agent starts or stops speaking."""
        self.agent_speaking = speaking
        logger.debug(f"Agent speaking = {self.agent_speaking}")

    async def process_transcription(self, text: str, confidence: float = 1.0):
        """
        Decide whether to ignore or process a transcription event.
        Returns: 'ignore', 'interrupt', or 'register'
        """
        if not text:
            return "ignore"

        text = text.lower().strip()
        words = [w for w in text.split() if w.isalpha()]

        # Ignore low-confidence mumble
        if confidence < 0.6:
            logger.debug("Ignored low confidence")
            return "ignore"

        # Only filler words while agent is speaking
        if self.agent_speaking and all(w in IGNORED_WORDS for w in words):
            logger.info(f"Ignored filler during agent speech: {text}")
            return "ignore"

        # Real input while agent is speaking
        if self.agent_speaking and any(w not in IGNORED_WORDS for w in words):
            logger.info(f"Interrupt detected: {text}")
            return "interrupt"

        # Agent quiet
        return "register"
