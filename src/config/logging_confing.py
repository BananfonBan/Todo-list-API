import logging

log_info = logging.basicConfig(
    format="[%(levelname)s] (%(asctime)s.%(msecs)03d)\
    %(module)s:%(lineno)d - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO,
)
