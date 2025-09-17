import subprocess
from logger import Logger

class Hooks:
    """
    Gerencia a execução de hooks pre e post para download, build, install e remove.
    """

    def __init__(self, hooks_config, logger: Logger = None):
        """
        hooks_config: dicionário com chaves:
            pre_download, post_download,
            pre_build, post_build,
            pre_install, post_install,
            pre_remove, post_remove
        """
        self.hooks = hooks_config or {}
        self.logger = logger

    def run(self, hook_type: str, program_name: str):
        """
        Executa os comandos de hook para o tipo especificado.
        """
        commands = self.hooks.get(hook_type, [])
        for cmd in commands:
            full_cmd = cmd.replace("{program}", program_name)
            try:
                if self.logger:
                    self.logger.info(f"Executando hook {hook_type} para {program_name}: {full_cmd}")
                subprocess.run(full_cmd, shell=True, check=True)
            except subprocess.CalledProcessError as e:
                if self.logger:
                    self.logger.error(f"Hook {hook_type} falhou para {program_name}: {e}")
                raise
