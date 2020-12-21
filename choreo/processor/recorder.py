from choreo.dbmanager.redis_dao import *
import os, glob
from configuration.config import *
# from choreo.external_handler.rabbitmq_handler import RabbitMqHandler


class Recorder:
    @staticmethod
    def record(*args):
        """
        :param args: user_id, selected_choreo_id, counter(1-)
        :return: None (only cache data access - change counter value)
        """
        p = [25, 50, 99]
        p_a = [0, 25, 50, 75, 99]
        c_a = []
        belongs_to = None
        print("==============This is recorder babe===============")
        print(args)
        try:
            prev_counter, interval = [int(k) for k in UserRedisHandler.get_user_info(args[0], "counter", "interval_n")]
            print(prev_counter, interval)

            # TODO 요청이 오면 rabbitmq를 통해 선택될 때마다 보내기 > 2까지?
            print("hi")

            # TODO 마지막 요청이 오면 다 합치도록 메시지 보내기


            # if prev_counter < args[2]:  # 이전으로 돌아간 경우를 판별하는 로직
            # general_folder = set(glob.glob(f"/home/jihee/choleor_media/product/{args[0]}/*")) ^ set(
            #     glob.glob(f"/home/jihee/choleor_media/product/{args[0]}/*%"))
            #
            # for i in general_folder:
            #     if args[2] <= int(i.split("/")[-1]) <= prev_counter:
            #         for k in glob.glob(i + "/*"):
            #             os.remove(k)
            #     os.rmdir(i)
            # TDO rabbitmq로 보내기
            # restart = 1

            # start_idx = 14
            #
            # c_a = [int(interval * k * 0.01) + start_idx for k in p_a]  # [14, 17, 20, 23, 25]
            # c_a.append(int(interval * 99 * 0.01) + start_idx - 1)
            #
            # for k in range(len(c_a)):  # check current percentage
            #     if c_a[k] <= args[2] < c_a[k + 1]:
            #         belongs_to = p[k]
            #         print(p[k])

            # if bool(belongs_to) and bool(glob.glob(f"/home/jihee/choleor_media/product/{args[0]}/*%")):
            #     for i in glob.glob(f"/home/jihee/choleor_media/product/{args[0]}/*%"):
            #         if int(i.split("/")[-1].split("%")[0]) >= belongs_to:
            #             for k in glob.glob(i + "*"):
            #                 os.remove(k)
            #             os.rmdir(i)

            # selection handling
            existed_choreos = SelectionRedisHandler.get_selection_info(args[0])
            print(existed_choreos)
            new_choreos = None
            print("current counter is " + str(args[2]))

            if args[2] is not 1:
                if args[2] < len(existed_choreos):
                    new_choreos = existed_choreos[:args[2]] + [args[1]]
                else:
                    new_choreos = existed_choreos + [args[1]]
                print(new_choreos)
                SelectionRedisHandler.add_selection_info(args[0], *new_choreos)

        except Exception as e:
            print(e)

        finally:
            UserRedisHandler.set_user_counter(args[0], args[2])
            # routing_k = [25, 50, 99]
            # if args[1] in c_a[2:]:  # [20, 23, 25]
            #     print(args[1], c_a[2:])
            #     send.send_progress(user_id=args[0], percent=routing_k[c_a.index(args[1])])
            print(args[0])
            print(args[1])
            return args[0], args[1]  # user_id, selected_choreo_id
