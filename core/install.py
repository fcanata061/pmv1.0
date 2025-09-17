from build import Builder
from hooks import Hooks
from logger import Logger
from dependency import DependencyResolver

class Installer:
    """
    Gerencia a instalação de pacotes no PM.
    """

    def __init__(self, db, logger: Logger = None, hooks: Hooks = None):
        """
        db: banco de dados de pacotes (pode ser dict ou interface de DB real)
        """
        self.db = db
        self.logger = logger
        self.hooks = hooks
        self.dep_resolver = DependencyResolver(db)

    def install_package(self, recipe, use_flags=None, fakeroot=False, destdir=None):
        """
        Instala um pacote único, resolvendo dependências.
        """
        use_flags = use_flags or []
        # Resolve dependências topológicas
        all_packages = self.dep_resolver.resolve_with_use([recipe['name']], use_flags)
        if self.logger:
            self.logger.info(f"Pacotes a instalar (resolução de dependências): {all_packages}")

        # Instala pacote por pacote
        for pkg_name in all_packages:
            pkg_recipe = self.db.get(pkg_name)
            if not pkg_recipe:
                if self.logger:
                    self.logger.warning(f"Receita de {pkg_name} não encontrada, pulando.")
                continue

            builder = Builder(recipe=pkg_recipe, logger=self.logger, hooks=self.hooks)
            builder.build(stage='install', use_fakeroot=fakeroot, destdir=destdir)
            if self.logger:
                self.logger.info(f"{pkg_name} instalado com sucesso.")

    def install_group(self, group_name, use_flags=None, fakeroot=False, destdir=None):
        """
        Instala todos os pacotes de um grupo.
        """
        group_packages = self.dep_resolver.packages_in_group(group_name)
        if self.logger:
            self.logger.info(f"Instalando grupo '{group_name}' com pacotes: {group_packages}")

        for pkg_name in group_packages:
            pkg_recipe = self.db.get(pkg_name)
            if not pkg_recipe:
                if self.logger:
                    self.logger.warning(f"Receita de {pkg_name} não encontrada, pulando.")
                continue

            self.install_package(pkg_recipe, use_flags=use_flags, fakeroot=fakeroot, destdir=destdir)
