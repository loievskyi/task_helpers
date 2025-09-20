class QueueNameMixin:
    """
    Returns queue_name (with prefix and suffix, like "pending")
    profiles _build_queue_name method.
    """

    prefix_queue = ""

    def _build_queue_name(self, base_queue_name: str, suffix: str | None = None) -> str:
        """Returns queue_name (with prefix and suffix, like "pending")"""
        queue_name = base_queue_name
        if self.prefix_queue:
            queue_name = f"{self.prefix_queue}:{queue_name}"
        if suffix:
            queue_name = f"{queue_name}:{suffix}"
        return queue_name
