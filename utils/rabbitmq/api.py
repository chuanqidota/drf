import pika


class RabbitMQClient:
    def __init__(self, host='localhost', port=5672, virtual_host='/', username=None, password=None):
        """

        :param host:   RabbitMQ host
        :param port:   RabbitMQ port
        :param virtual_host:  RabbitMQ virtual host
        :param username:   RabbitMQ username
        :param password:   RabbitMQ password
        """
        self.connection_parameters = pika.ConnectionParameters(
            host=host,
            port=port,
            virtual_host=virtual_host,
            credentials=pika.PlainCredentials(username, password) if username and password else None
        )
        self.connection = None
        self.channel = None

    def connect(self):
        self.connection = pika.BlockingConnection(self.connection_parameters)
        self.channel = self.connection.channel()

    def disconnect(self):
        if self.connection and self.connection.is_open:
            self.connection.close()

    def declare_exchange(self, exchange_name, exchange_type='direct', durable=True, auto_delete=False):
        self.channel.exchange_declare(
            exchange=exchange_name,
            exchange_type=exchange_type,
            durable=durable,
            auto_delete=auto_delete
        )

    def declare_queue(self, queue_name, durable=True, exclusive=False, auto_delete=False, arguments=None):
        self.channel.queue_declare(
            queue=queue_name,
            durable=durable,
            exclusive=exclusive,
            auto_delete=auto_delete,
            arguments=arguments
        )

    def bind_queue_to_exchange(self, exchange_name, queue_name, routing_key=''):
        self.channel.queue_bind(
            exchange=exchange_name,
            queue=queue_name,
            routing_key=routing_key
        )

    def publish_message(self, exchange_name, routing_key, body, properties=None):
        if not properties:
            properties = pika.BasicProperties()
        self.channel.basic_publish(
            exchange=exchange_name,
            routing_key=routing_key,
            body=str(body).encode(),
            properties=properties
        )

    def consume_messages(self, queue_name, callback, auto_ack=False, consumer_tag=None):
        self.channel.basic_consume(
            queue=queue_name,
            on_message_callback=callback,
            auto_ack=auto_ack,
            consumer_tag=consumer_tag
        )

    def start_consuming(self):
        self.channel.start_consuming()

    def stop_consuming(self):
        self.channel.stop_consuming()

    def purge_queue(self, queue_name):
        self.channel.queue_purge(queue=queue_name)
