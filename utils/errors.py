import os
import abc

ERR_HEAD = """
A error has been detected and the game has been shut down.Please contact bookyzhang@qq.com and send this file for help.
Or send a "issue" to Github xkcdjerry/Tank-Wars,thank you.

一个错误被检测到了，游戏已关闭，请联系bookyhang@qq.com并发送这个文件来获得帮助，或者在GitHub的xkcdjerry/Tank-Wars上添加一个issue，谢谢。
"""


def ErrorHandler():
    """
A factory function for error handlers
    """
    return RaiseErrorHandler()


def get_error_log_file_name():
    """
    returns a file name to write the bug report
    """
    i = 1
    fmt = "bugreport%i.txt"
    while os.path.isfile(fmt % i):
        i += 1
    return fmt % i


class Handler(metaclass=abc.ABCMeta):
    """
    Base Class for Error Handlers
    """

    @abc.abstractmethod
    def handle(self, err):
        return err


class RaiseErrorHandler(Handler):
    def handle(self, err):
        raise err from None

class LogErrorHandler(Handler):
    def handle(self, err):
        import traceback
        print("Error Found（已检测到错误）...")
        print("Shutting down program（正在结束程序）...")
        file_name = get_error_log_file_name()
        s = traceback.format_exc()
        with open(file_name, "w", encoding="utf-8") as f:
            f.write(ERR_HEAD)
            f.write("\n\n")
            f.write(s)
        traceback.print_exc()
        return err
