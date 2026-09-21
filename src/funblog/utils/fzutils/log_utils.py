# coding:utf-8

# log utils

"""
切记: 不要重复创造日志对象，否则会重复打印
"""

from farlog import getLogger

__all__ = [
    'set_logger'
]


def set_logger(log_file_name=None,
               console_log_level=None,
               file_log_level=None,
               console_formatter=None,
               file_formatter=None,
               logger_name='my_logger'):
    """
    获取一个具名 logger。

    历史上本函数会手动创建 `StreamHandler`/`RotatingFileHandler` 并绑定到 logger 上；
    现统一改为组织自有的 `farlog`，落盘路径、轮转与级别由 `farlog` 统一管理，
    不再由业务代码自行配置 handler。`log_file_name`/`console_log_level` 等参数仅为
    兼容历史调用方保留，不再生效。

    :param log_file_name: 历史参数，已废弃，不再使用
    :param console_log_level: 历史参数，已废弃，不再使用
    :param file_log_level: 历史参数，已废弃，不再使用
    :param console_formatter: 历史参数，已废弃，不再使用
    :param file_formatter: 历史参数，已废弃，不再使用
    :param logger_name: logger 名称
    :return: 具名 logger
    """
    return getLogger(logger_name)
