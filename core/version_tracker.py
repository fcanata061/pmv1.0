import requests
import datetime
import yaml
from logger import Logger

class VersionTracker:
    """
    Rastreia versões de pacotes instalados e verifica atualizações.
    """

    def __init__(self, config_path, db, logger: Logger = None):
        """
        config_path: caminho para o arquivo YAML de configuração do tracker
        db: banco de dados de pacotes instalados {package_name: {'version': 'x.y.z'}}
        logger: instância do Logger do PM
        """
        self.db = db
        self.logger = logger
        self.config_path = config_path
        self.config = self.load_config()
        self.last_checked = datetime.datetime.now() - datetime.timedelta(days=self.config.get('check_interval_days', 7))

    def load_config(self):
        with open(self.config_path, 'r') as f:
            return yaml.safe_load(f)

    def check_updates(self):
        """
        Verifica atualizações de todos os pacotes instalados.
        """
        updates = {}
        now = datetime.datetime.now()
        interval = self.config.get('check_interval_days', 7)
        if (now - self.last_checked).days < interval:
            return updates  # Não precisa checar ainda

        for pkg, data in self.db.items():
            latest_version = self.get_latest_version(pkg)
            if latest_version and latest_version != data['version']:
                updates[pkg] = {
                    'current': data['version'],
                    'latest': latest_version,
                    'critical': pkg in self.config.get('critical_programs', [])
                }
                if self.logger:
                    if pkg in self.config.get('critical_programs', []):
                        self.logger.warning(f"{pkg} possui nova versão: {latest_version} (CRÍTICO)")
                    elif self.config.get('auto_update', False):
                        self.logger.info(f"{pkg} será atualizado automaticamente para {latest_version}")

        self.last_checked = now
        return updates

    def get_latest_version(self, package):
        """
        Busca a versão mais recente de um pacote.
        Pode ser via API ou scraping simples (exemplo HTTP).
        """
        # Exemplo simplificado: supomos que existe um arquivo online com versão
        urls = {
            'gcc': 'https://ftp.gnu.org/gnu/gcc/gcc-latest-version.txt',
            'vim': 'https://raw.githubusercontent.com/vim/vim/master/version.txt',
            # Adicione outros pacotes conforme necessário
        }
        url = urls.get(package)
        if not url:
            return None
        try:
            resp = requests.get(url, timeout=5)
            if resp.status_code == 200:
                return resp.text.strip()
        except requests.RequestException:
            if self.logger:
                self.logger.error(f"Falha ao buscar versão de {package}")
        return None

    def auto_update_packages(self, pm_interface):
        """
        Atualiza pacotes seguros automaticamente, usando interface do PM.
        """
        updates = self.check_updates()
        for pkg, info in updates.items():
            if not info['critical'] and self.config.get('auto_update', False):
                pm_interface.update_package(pkg)  # Deve ser implementado no PM
                if self.logger:
                    self.logger.info(f"{pkg} atualizado automaticamente de {info['current']} para {info['latest']}")
