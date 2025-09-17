from dependency import DependencyResolver
from install import Installer
from remove import Remover
from logger import Logger

class GroupManager:
    """
    Gerencia grupos de pacotes no PM.
    """

    def __init__(self, db, logger: Logger = None, hooks=None, install_root="/usr/local"):
        self.db = db
        self.logger = logger
        self.hooks = hooks
        self.dep_resolver = DependencyResolver(db)
        self.installer = Installer(db, logger=logger, hooks=hooks)
        self.remover = Remover(db, logger=logger, hooks=hooks, install_root=install_root)

    def install_group(self, group_name, use_flags=None, fakeroot=False, destdir=None):
        """
        Instala todos os pacotes de um grupo.
        """
        group_packages = self.dep_resolver.packages_in_group(group_name)
        if self.logger:
            self.logger.info(f"Iniciando instalação do grupo '{group_name}' com pacotes: {group_packages}")
        for pkg_name in group_packages:
            pkg_recipe = self.db.get(pkg_name)
            if pkg_recipe:
                self.installer.install_package(pkg_recipe, use_flags=use_flags, fakeroot=fakeroot, destdir=destdir)
            else:
                if self.logger:
                    self.logger.warning(f"Receita de {pkg_name} não encontrada, pulando.")

    def remove_group(self, group_name):
        """
        Remove todos os pacotes de um grupo.
        """
        group_packages = self.dep_resolver.packages_in_group(group_name)
        if self.logger:
            self.logger.info(f"Iniciando remoção do grupo '{group_name}' com pacotes: {group_packages}")
        for pkg_name in group_packages:
            self.remover.remove_package(pkg_name)

    def list_group(self, group_name):
        """
        Retorna a lista de pacotes pertencentes a um grupo.
        """
        return self.dep_resolver.packages_in_group(group_name)
