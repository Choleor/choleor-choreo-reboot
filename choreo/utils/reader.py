import abc
import unicodecsv, csv
import sys
import re


# import choreo.utils.modif_ds as dsutils


class Reader(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def read(self, **kwargs):
        raise NotImplementedError()


class TxtReader(Reader):
    def read(self, file):
        try:
            # try: #if there's no given operation(lambda) of user
            #     kwargs['lambda'](open(self._file, mode='rt', encoding='utf-8').readlines())
            # except KeyError:
            return open(file, mode='rt', encoding='utf-8').readlines()
        except FileNotFoundError:
            sys.stderr.write("No such text file: %s\n" % file)
            return None


class CsvReader(Reader):
    def read(self, file, **kwargs):
        try:
            if not bool(kwargs):
                self.read_all()
                exit(0)
            __cols__ = [v for k, v in kwargs.items() if re.compile(r'col').search(k)]
            __vals__ = []
            for col in __cols__:
                with open(file, mode='r', encoding='utf-8') as f:
                    __vals__.append([row[col] for row in csv.DictReader(f)])

            _dict = {k: v for k, v in zip(__cols__, __vals__)}
            return _dict if not kwargs.get('lambda') else kwargs.get('lambda')(_dict)

        except FileNotFoundError:
            sys.stderr.write("No such text file: %s\n" % file)
            exit(1)

        except NotImplementedError:
            pass

    def read_all(self, file):
        with open(file, 'r', encoding="utf-8") as rf:
            for row in unicodecsv.DictReader(rf, delimiter='\t'):
                type(row)


#
test_path = "/home/jihee/choleor_media/"
# if __name__ == '__main__':
#     result = CsvReader(test_path + "test.csv").read(
#         **{'col1': 'choreo_vid', 'col2': 'choreo_url', 'col3': 'start', 'col4': 'end'})
#     print(result)
#     print(dsutils.listdict_to_dictlist(result))
