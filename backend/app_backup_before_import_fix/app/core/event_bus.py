class EventBus:

    def __init__(self):

        self.listeners = {}

    def subscribe(self, event, callback):

        self.listeners.setdefault(event, [])

        self.listeners[event].append(callback)

    async def publish(self, event):

        callbacks = self.listeners.get(event.event_type, [])

        for callback in callbacks:

            await callback(event)


event_bus = EventBus()
