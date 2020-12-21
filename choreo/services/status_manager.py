from abc import ABC, abstractmethod
from choreo.dbmanager.redis_dao import *


class StatusManager:
    """
    Status Manager's Role / state pattern
    - checks whether the user goes forward or backward
    - records the user's status or selection (if not X)
    - reports to product server with handling rabbitmq

    Input
    counter (current status) > which judges forward or backward
    user's id > record on user redis
    selected choreography slice's id > record on selection redis

    """

    def __init__(self, *args):
        """
        :param args: [0] user_id   [1] selected_choreo_id   [2] counter
        """
        # self.state = None
        self.info = [self.user_id, self.selected_choreo_id, self.counter] = args

        # Rabbitmq configuration settings
        # RABBITMQ_URL = "amqp://rabbitmq:dkrabbitmq@rabbitmq:5673"
        # self.connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
        # self.channel = self.connection.channel()
        # self.channel.exchange_declare(exchange='produce_req', exchange_type='direct')
        # self.cancel = False

    def update_redis(self):
        # if UserRedisHandler.get_user_counter(self.user_id) >= int(self.counter):
        #     self.cancel = True
        UserRedisHandler.set_user_counter(self.user_id, self.counter)

        for i in range(1, 7):
            UserRedisHandler.dao.hset(self.user_id, str(i), "0")

        if self.counter != 1:
            selected = SelectionRedisHandler.get_selection_info(self.user_id)
            print(selected)
            if self.counter == 2:
                to_insert = [self.user_id, self.selected_choreo_id]
            else: # counter가 3 > selected가 기존에 1개 들어가있을 것
                to_insert = [self.user_id] + selected[:(self.counter - 2)] + [self.selected_choreo_id]
            print(to_insert)
            print("to insert")
            SelectionRedisHandler.dao.delete(self.user_id)
            SelectionRedisHandler.add_selection_info(*to_insert)

    # def send_produce_request(self):
    #     print("Here.")
    #     if self.counter != 1:
    #         self.channel.queue_declare("produce_req")
    #         self.channel.basic_publish(exchange='produce_req', routing_key='', body=self.user_id)
    #         self.connection.close()

    # def send_cancel_request(self):
    #     self.channel.queue_declare("cancel")
    #     self.channel.basic_publish(exchange='cancel_req', routing_key='', body=self.user_id)
    #     self.connection.close()

    def manage_status(self):
        self.update_redis()
        # self.send_produce_request()
        # if self.cancel:
        #     self.send_cancel_request


# if __name__ == '__main__':
#     StatusManager("testuser", "WYBn-iqU9ds~5", 5).manage_status()
