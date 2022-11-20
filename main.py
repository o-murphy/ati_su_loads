import logging
from modules import bot, CONFIG


def main():
    logging.basicConfig(**CONFIG['logger'])
    bot.run()


if __name__ == '__main__':
    main()
