from telegram.ext import CommandHandler


class CommandHandlerWithHelp(CommandHandler):
    helps = dict()

    def __init__(self, command, callback, help_text, *args, **kwargs):
        super(CommandHandlerWithHelp, self).__init__(command,callback,*args, **kwargs)
        self.help = help_text
        self.helps[command] = help_text