from choreo.utils.reader import *
from abc import ABC
import chardet
from configuration.config import *


class AlreadyExistsError(Exception):  # Exception을 상속받아서 새로운 예외를 만듦
    def __init__(self):
        super().__init__("Download failure. There's already downloaded source.")


class Writer(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def write(self, **kwargs):
        raise NotImplementedError()


class TxtWriter(Writer):
    def write(self, file, *args):
        try:
            with open(file, mode='w', encoding='utf-8') as f:
                f.writelines(*args)
            return 0
        except IOError:
            sys.stderr.write("No such text file: %s\n" % file)
            return 1


class CsvWriter(Writer):
    def write(self, csv_in, **column_infos):
        """
        :param csv_in:
        :param args: column name
        :param column_infos: column name(key) ---- value lists (value)
        :return:
        """
        # count row numbers
        num_rows = 0
        for row in open(csv_in):
            num_rows += 1

        with open(csv_in, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=column_infos.keys())
            writer.writeheader()

            for v in column_infos.values():
                writer.writerow({'': 'Baked', '': 'Beans'})

    @staticmethod
    def append_new_column(in_csv, out_csv, opt="end", **kwargs):
        """
        :param in_csv:
        :param out_csv:
        :param kwargs: key = new_col / value = col
        :return:
        """
        with open(in_csv, 'r', encoding='cp1252') as input:
            with open(out_csv, 'w', encoding='utf-8') as output:
                writer = csv.writer(output, lineterminator='\n')
                reader = csv.reader(input)
                all = []
                row = next(reader)
                for new_c in kwargs:
                    row = row + [new_c] if opt is "end" else [new_c] + row
                row = [r.encode('UTF-8') for r in row]
                all.append(row)

                for row in reader:
                    for val_c in kwargs.values():
                        if opt is "end":
                            row.append(val_c)
                        else:
                            row = [val_c] + row  # list item
                    row = [r.encode('UTF-8') for r in row]
                    all.append(row)

                writer.writerows(all)

    @staticmethod
    def replace_column(_in_csv, _out_csv, _lambda=None, **kwargs):
        """
        :param _in_csv:
        :param _out_csv:
        :param _lambda: lambda to apply on existing value
        :param kwargs: key () - value lists (nothing when there's lambda)
        :return:
        """

        with open(_in_csv, 'r', encoding='utf-8') as input:
            with open(_out_csv, 'w', encoding='utf-8') as output:
                writer = csv.writer(output, lineterminator='\n')
                reader = csv.reader(input)

                col_idx_to_replace = {}  # ex "column1" : 4(th column) --> column's index
                all = []
                row = next(reader)

                for idx, col_name in enumerate(row):
                    if col_name in kwargs:
                        col_idx_to_replace[col_name] = idx

                all.append(row)

                for row_idx, row in enumerate(reader):
                    if _lambda is None:
                        for column_name, value_lists in kwargs:
                            row[col_idx_to_replace[column_name]] = value_lists[row_idx - 1]
                    else:
                        for column_name in kwargs.keys():
                            row[col_idx_to_replace[column_name]] = _lambda(row[col_idx_to_replace[column_name]])
                    all.append(row)

                writer.writerows(all)

    # @staticmethod
    # def to_utf8(lst):
    #     return [unicode(elem).encode('utf-8') for elem in lst]


if __name__ == '__main__':
    in_csv = "/home/jihee/choleor_media/choreo_copy.csv"
    out_csv = "/home/jihee/choleor_media/choreo_final.csv"
    CsvWriter.replace_column(in_csv, out_csv, lambda x: x.split("ㅡ")[0] + "ㅡ" + str(int(x.split("ㅡ")[1]) - 1),
                             **{"choreo_slice_id": [0], "start_pose_id": [0], "end_pose_id": [0]})

    with open("/home/jihee/choleor_media/choreo_final.csv", "r") as f:
        file_data = f.readline()
        print(file_data.encode())
    print(chardet.detect(file_data.encode()))
