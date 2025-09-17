from dependency import DependencyResolver
from hooks import Hooks
from logger import Logger
import shutil
import os

class Remover:
    """
    Gerencia a remoção de pacotes no PM.
    """

    def __init__(self, db, logger: Logger = None, hooks: Hooks = None, install_root="/usr/local"):
        """
        db: banco de dados de pacotes (dict ou interface real)
        install_root: diretório raiz de instalação dos pacotes
        """
        self.db = db
        self.logger = logger
        self.hooks = hooks
        self.dep_resolver = DependencyResolver(db)
        self.install_root = install_root

    def remove_package(self, package_name):
        """
        Remove um pacote individual, verificando dependências invertidas (revdep).
        """
        # Checa revdep
        reverse_deps = self.dep_resolver.revdep(package_name)
        if reverse_deps:
            if self.logger:
                self.logger.warning(f"Não é possível remover {package_name}, ainda é requerido por: {reverse_deps}")
            return

        # Pre-remove hook
        if self.hooks:
            self.hooks.run("pre_remove", package_name)

        # Remove diretório do pacote (exemplo simplificado)
        pkg_path = os.path.join(self.install_root, package_name)
        if os.path.exists(pkg_path):
            shutil.rmtree(pkg_path)
            if self.logger:
                self.logger.info(f"{package_name} removido do sistema.")

        # Atualiza DB
        if package_name in self.db:
            del self.db[package_name]

        # Post-remove hook
        if self.hooks:
            self.hooks.run("post_remove", package_name)

    def remove_group(self, group_name):
        """
        Remove todos os pacotes de um grupo, respeitando revdep.
        """
        group_packages = self.dep_resolver.packages_in_group(group_name)
        if self.logger:
            self.logger.info(f"Removendo grupo '{group_name}' com pacotes: {group_packages}")
        for pkg in group_packages:
            self.remove_package(pkg)

    def remove_orphans(self):
        """
        Remove pacotes órfãos que não são dependência de nenhum outro pacote.
        """
        orphans = []
        for pkg in list(self.db.keys()):
            if not self.dep_resolver.revdep(pkg):
                orphans.append(pkg)

        if self.logger:
            self.logger.info(f"Pacotes órfãos detectados: {orphans}")

        for orphan in orphans:
            self.remove_package(orphan)
