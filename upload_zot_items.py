#!/usr/bin/python3.6

import logging
import logging.config


logging.config.fileConfig(fname='log.cfg')
log = logging.getLogger('upload_zot_items')


def main():
    log.debug("log main() 1")
    log.info("log main() 2")
    log.warning("log main() 3")
    log.error("log main() 4")
    log.critical("log main() 5")


if __name__ == "__main__":
    main()
    log.debug("log 1")
    log.info("log 2")
    log.warning("log 3")
    log.error("log 4")
    log.critical("log 5")
