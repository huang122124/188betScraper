import logging
import os.path
import sys
import time



def createLogFile(name, level):
    # 创建一个logger
    logger = logging.getLogger()
    logger.setLevel(level)  # Log等级总开关
    logger.handlers.clear()        # 清空已经存在的handler
    # 创建一个handler，用于写入日志文件
    rq = time.strftime('%Y-%m-%d', time.localtime(time.time()))
    # log_date = rq[:10]
    log_path = os.getcwd() + '/Logs/'
    isExists = os.path.exists(log_path)
    # # 判断结果
    if not isExists:
        os.makedirs(log_path)
    log_name = os.getcwd() + '/Logs/{}-'.format(rq) + name + '.log'
    # 定义handler的输出格式
    formatter = logging.Formatter("%(asctime)s - %(levelname)s--->: %(message)s")
    fh = logging.FileHandler(log_name, mode='a')
    # fh.setLevel(logging.DEBUG)  # 输出到file的log等级的开关
    fh.setFormatter(formatter)
    # 输出到控制台（标准输出流）console_handler = cs
    ch = logging.StreamHandler(sys.stdout)  # 明确指定日志输出到标准输出流中
    # ch.setLevel(logging.INFO)  # 输出到console的log等级的开关Debug
    ch.setFormatter(formatter)
    logger.addHandler(fh)
    logger.addHandler(ch)



def print_info(info, *args):
    createLogFile("info", logging.INFO)
    if len(args) > 0:
        log = ""
        for arg in args:
            log += "{}"
        logging.info((info + log).format(*args))
    else:
        logging.info(info)

def print_debug(debug, *args):
    createLogFile("debug", logging.DEBUG)
    if len(args) > 0:
        log = ""
        for arg in args:
            log += "{}"
        logging.debug((debug + log).format(*args))
    else:
        logging.debug(debug)

def print_error(error, *args):
    createLogFile("error",logging.ERROR)
    if len(args) > 0:
        log = ""
        for arg in args:
            log += "{}"
        logging.error((error + log).format(*args))
    else:
        logging.error(error)

def deleteBigFile(path):
    for file in os.listdir(path):
        fsize = os.path.getsize(f'{path}{file}')
        if (fsize > 1 * 1024 * 1024 * 1024):
            os.remove(f'{path}{file}')

if __name__ == '__main__':
    createLogFile("info", logging.INFO)