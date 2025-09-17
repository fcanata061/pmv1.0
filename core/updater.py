from version_tracker import VersionTracker
from install import Installer
from dependency import DependencyResolver
from groups import GroupManager
from logger import Logger

class Updater:
    """
    Gerencia atualizações de pacotes usando VersionTracker e Installer.
    """

    def __init__(self, db, config_path, logger: Logger = None, hooks=None):
        self.db = db
        self.logger = logger
        self.hooks = hooks
        self.version_tracker = VersionTracker(config_path, db, logger)
        self.installer = Installer(db, logger=logger, hooks=hooks)
        self.dep_resolver = DependencyResolver(db)
        self.group_manager = GroupManager(db, logger=logger, hooks=hooks)

    def update_package(self, package_name):
        """
        Atualiza um pacote individual se houver nova versão e não for crítico.
        """
        updates = self.version_tracker.check_updates()
        if package_name not in updates:
            if self.logger:
                self.logger.info(f"{package_name} já está na versão mais recente.")
            return

        info = updates[package_name]
        if info['critical']:
            if self.logger:
                self.logger.warning(f"{package_name} é crítico. Apenas avisando nova versão {info['latest']}.")
            return

        pkg_recipe = self.db.get(package_name)
        if not pkg_recipe:
            if self.logger:
                self.logger.warning(f"Receita de {package_name} não encontrada. Atualização ignorada.")
            return

        self.installer.install_package(pkg_recipe)
        if self.logger:
            self.logger.info(f"{package_name} atualizado de {info['current']} para {info['latest']}.")

    def update_group(self, group_name):
        """
        Atualiza todos os pacotes de um grupo.
        """
        group_packages = self.dep_resolver.packages_in_group(group_name)
        if self.logger:
            self.logger.info(f"Iniciando atualização do grupo '{group_name}'")
        for pkg in group_packages:
            self.update_package(pkg)

    def update_all(self):
        """
        Atualiza todos os pacotes não críticos com novas versões.
        """
        updates = self.version_tracker.check_updates()
        for pkg, info in updates.items():
            if not info['critical']:
                self.update_package(pkg)
