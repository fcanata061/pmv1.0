import os
import datetime
from colorama import Fore, Style, init

# Inicializa cores no terminal
init(autoreset=True)

class Logger:
    """
    Gerencia logs do PM com cores, persistência em arquivos e integração com DB.
    """

    LEVELS = ['DEBUG', 'INFO', 'WARNING', 'ERROR']
    COLORS = {
        'DEBUG': Fore.CYAN,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED
    }

    def __init__(self, log_path, level='INFO'):
        self.log_path = log_path
        self.level = level.upper()
        os.makedirs(log_path, exist_ok=True)
        self.log_file = os.path.join(log_path, 'pm.log')

    def _should_log(self, level):
        """
        Verifica se a mensagem deve ser registrada.
        """
        return self.LEVELS.index(level) >= self.LEVELS.index(self.level)

    def log(self, message, level='INFO'):
        """
        Registra uma mensagem de log.
        """
        level = level.upper()
        if not self._should_log(level):
            return

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        colored_msg = f"{self.COLORS.get(level, '')}[{level}] {timestamp} - {message}{Style.RESET_ALL}"
        plain_msg = f"[{level}] {timestamp} - {message}"

        # Exibe no terminal
        print(colored_msg)

        # Persiste no arquivo
        with open(self.log_file, 'a') as f:
            f.write(plain_msg + "\n")

    def debug(self, message):
        self.log(message, 'DEBUG')

    def info(self, message):
        self.log(message, 'INFO')

    def warning(self, message):
        self.log(message, 'WARNING')

    def error(self, message):
        self.log(message, 'ERROR')
