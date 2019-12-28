class EventBus(object):
    subscriptions = dict()

    def pub(event, payload):
        callbacks = EventBus.subscriptions.get(event, list())
        for callback in callbacks:
            try:
                callback(event, payload)
            except:
                print("EVENTBUS: Error calling callback {!r} for event {} and payload {!r}".format(callback, event, payload))

    def sub(event, callback):
        callbacks = EventBus.subscriptions.get(event, list())
        callbacks.append(callback)
        EventBus.subscriptions[event] = callbacks

    def unsub(event, callback):
        EventBus.subscriptions[event] = [x for x in EventBus.subscriptions.get(event, List()) if x is not callback]
