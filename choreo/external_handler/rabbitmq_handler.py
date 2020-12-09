import pika
from choreo.utils.singleton_factory import *


class RabbitMqHandler(SingletonInstance):
    def __init__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters('127.0.0.1:6072'))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='choreo_result')
        self.channel.queue_declare(queue='progress_notification')

    @staticmethod
    def send_progress(user_id, progress):
        RabbitMqHandler.instance().channel.queue_declare(queue='progress_notification')
        RabbitMqHandler.instance().channel.basic_publish(exchange='', routing_key=user_id, body=progress)
        RabbitMqHandler.instance().connection.close()

    @staticmethod
    def receive_result():
        def callback(ch, method, properties, body):
            print(" [x] Received %r" % body)

        RabbitMqHandler.instance().channel.basic_consume(queue='choreo_result', on_message_callback=callback,
                                                         auto_ack=True)
        print(' [*] Waiting for messages. To exit press CTRL+C')
        RabbitMqHandler.instance().channel.start_consuming()
