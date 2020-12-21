# import time
# from choreo.job import rediswq
#
# host = "redis_choreo"
#
# q = rediswq.RedisWQ(name="produce_j", host="redis")
# print("Worker with sessionID: " + q.sessionID())
# print("Initial queue state: empty=" + str(q.empty()))
# while not q.empty():
#     item = q.lease(lease_secs=10, block=True, timeout=2)
#     if item is not None:
#         choreo = item.decode("utf-8")
#         #TODO call produce method
#         #print(f"{user_id}: {choreo}")
#         #print(f"{user_id}: {choreo path}")
#         q.complete(item)
#     else:
#         print("Waiting for work")
# print("Queue empty, exiting")
