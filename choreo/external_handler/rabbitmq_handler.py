# import pika
# import sys
#
#
# class RabbitMqHandler:
#     RABBITMQ_URL = "amqp://django:dkrabbitmqaudio@localhost:5673"
#
#
# class ProgressSender:
#     def __init__(self):
#         self.connection = pika.BlockingConnection(pika.URLParameters(RabbitMqHandler.RABBITMQ_URL))
#
#         self.channel = self.connection.channel()
#         self.channel.exchange_declare(exchange='progress', exchange_type='direct')
#
#     def send_progress(self, percent, user_id):
#         self.channel.queue_declare(str(percent))
#         self.channel.basic_publish(
#             exchange='progress', routing_key='', body=user_id)
#         print(" [x] Sent %r:%r" % (percent, user_id))
#         self.connection.close()
#
#
# class CandidateClient:
#     @staticmethod
#     def send_candidates(request_n, user_id, counter, choreo, audio_info):
#         print(request_n, user_id, counter, choreo, audio_info)
#
#         connection = pika.BlockingConnection(pika.URLParameters(RabbitMqHandler.RABBITMQ_URL))
#         channel = connection.channel()
#         channel.exchange_declare(exchange='candidates', exchange_type='direct')
#         channel.queue_declare(str(request_n))
#         channel.basic_publish(
#             exchange='candidates', routing_key=f"{request_n}.{user_id}.{counter}", body=audio_info + ":" + choreo)
#         print("sent " + audio_info + ":" + choreo)
#         connection.close()
#
#     @staticmethod
#     def get_selected_candidate(request_n, user_id, counter):
#         connection = pika.BlockingConnection(
#             pika.URLParameters(RabbitMqHandler.RABBITMQ_URL))
#         channel = connection.channel()
#
#         channel.exchange_declare(exchange='candidates', exchange_type='direct')
#         channel.queue_declare(str(request_n))
#
#         # channel.queue_bind(
#         #     exchange='candidates', queue=str(request_n), routing_key=f"{request_n}.{user_id}.{counter}")
#
#         method_frame, header_frame, body = channel.basic_get(queue=str(request_n))
#
#         while method_frame.NAME != 'Basic.GetEmpty':
#             channel.basic_ack(delivery_tag=method_frame.delivery_tag)
#             connection.close()
#             return body.decode()
#
# #
# # if __name__ == '__main__':
# #     #     # ProgressSender().send_progress(50, "aa")
# #     #     # ProgressSender().send_progress(50, "b")
# #     #     # ProgressSender().send_progress(50, "cc")
# #     #     # print(ProgressReceiver().receive_progress(50))
# #     CandidateClient.send_candidates(3, "this is user", 15, "xT9sBdQ3Uo0ㅡ13", "3:CM5VSP1QWXg~3")
# #     print(CandidateClient.get_selected_candidate(3, "this is user", 15))
# #
# # #     # RabbitMqHandler.test_send("plz")
# # #     # RabbitMqHandler.test_recv("KEY")
