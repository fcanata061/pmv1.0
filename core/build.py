import os
import subprocess
import shutil
from sandbox import Sandbox
from hooks import Hooks
from logger import Logger

class Builder:
    """
    Gerencia o processo de build de pacotes.
    """

    def __init__(self, recipe, logger: Logger = None, hooks: Hooks = None, sandbox_config=None):
        self.recipe = recipe
        self.logger = logger
        self.hooks = hooks
        self.sandbox_config = sandbox_config or {}
        self.sandbox = Sandbox(sandbox_config)

    def prepare_sandbox(self):
        """
        Cria e retorna o sandbox para a construção.
        """
        path = self.sandbox.create()
        if self.logger:
            self.logger.info(f"Sandbox criado em {path}")
        return path

    def apply_patches(self, build_path):
        """
        Aplica patches listados na receita.
        """
        for patch in self.recipe.get('patches', []):
            patch_file = patch['file']
            cmd = f"patch -p{patch.get('strip', 1)} < {patch_file}"
            if self.logger:
                self.logger.info(f"Aplicando patch: {patch_file}")
            subprocess.run(cmd, shell=True, cwd=build_path, check=True)

    def build(self, stage='build', use_fakeroot=False, destdir=None):
        """
        Executa o build completo:
        - Pre-hooks
        - Build (autotools, make, etc.)
        - Post-hooks
        """
        sandbox_path = self.prepare_sandbox()
        build_path = os.path.join(sandbox_path, 'build')
        os.makedirs(build_path, exist_ok=True)

        # Pre-build hook
        if self.hooks:
            self.hooks.run(f"pre_{stage}", self.recipe['name'])

        # Extrair fontes
        src_tarball = self.recipe.get('tarball')
        if src_tarball:
            cmd_extract = f"tar xf {src_tarball} -C {build_path}"
            if self.logger:
                self.logger.info(f"Extraindo fontes: {src_tarball}")
            subprocess.run(cmd_extract, shell=True, check=True)

        # Aplicar patches
        self.apply_patches(build_path)

        # Configuração do build (exemplo: ./configure ou mozconfig)
        config_cmd = self.recipe.get('config_cmd')
        if config_cmd:
            full_cmd = f"{config_cmd}"
            if use_fakeroot:
                full_cmd = f"fakeroot {full_cmd}"
            if self.logger:
                self.logger.info(f"Configurando build: {full_cmd}")
            subprocess.run(full_cmd, shell=True, cwd=build_path, check=True)

        # Compilação
        build_cmd = self.recipe.get('build_cmd', 'make -j$(nproc)')
        if use_fakeroot:
            build_cmd = f"fakeroot {build_cmd}"
        if self.logger:
            self.logger.info(f"Compilando: {build_cmd}")
        subprocess.run(build_cmd, shell=True, cwd=build_path, check=True)

        # Instalação (DESTDIR)
        if destdir:
            install_cmd = f"{self.recipe.get('install_cmd', 'make install')} DESTDIR={destdir}"
        else:
            install_cmd = self.recipe.get('install_cmd', 'make install')
        if use_fakeroot:
            install_cmd = f"fakeroot {install_cmd}"
        if self.logger:
            self.logger.info(f"Instalando: {install_cmd}")
        subprocess.run(install_cmd, shell=True, cwd=build_path, check=True)

        # Post-build hook
        if self.hooks:
            self.hooks.run(f"post_{stage}", self.recipe['name'])

        # Limpeza do sandbox
        self.sandbox.clean()
        if self.logger:
            self.logger.info("Sandbox limpo após build")
