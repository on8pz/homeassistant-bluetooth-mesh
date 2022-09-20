import json
import logging
import asyncio


class MessengerModule:
    """
    Base class for all MQTT messenger modules

    Provides default implementations, that should work for most common nodes.
    They can however be overriden, if more sophisticated behaviour is required.
    """

    def __init__(self, messenger):
        self._messenger = messenger

    @property
    def component(self):
        return None

    def _property_change(self, node, property, value):
        try:
            # get handler from property name
            handler = getattr(self, f'_node_{property}')
        except:
            logging.warning(f'Missing handler for property {property}')
            return

        # TODO: track task
        asyncio.create_task(handler(node, value))

    async def listen(self, node):
        """
        Listen for incoming messages and node changes
        """

        # listen for node changes
        node.subscribe(self._property_change)

        # listen for incoming MQTT messages
        async with self._messenger.filtered_messages(self.component, node) as messages:
            async for message in messages:
                logging.info(f'Received message on {message.topic}:\n{message.payload}')

                # get command from topic and load message
                command = message.topic.split('/')[-1]
                payload = json.loads(message.payload.decode())
                
                try:
                    # get handler from command name
                    handler = getattr(self, f'_mqtt_{command}')
                except:
                    logging.warning(f'Missing handler for command {command}')
                    continue

                await handler(node, payload)

    async def config(self, node):
        """
        Send discovery message
        """
        pass