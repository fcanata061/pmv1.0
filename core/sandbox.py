import os
import shutil
import tempfile
import subprocess

class Sandbox:
    """
    Gerencia a criação, execução e limpeza de ambientes isolados para builds.
    """

    def __init__(self, config, use_fakeroot=False, keep=False):
        self.config = config
        self.use_fakeroot = use_fakeroot
        self.keep = keep
        self.base_path = None

    def create(self):
        """
        Cria um diretório temporário para o sandbox.
        """
        self.base_path = tempfile.mkdtemp(prefix="pm_sandbox_")
        os.chmod(self.base_path, 0o700)
        return self.base_path

    def run(self, cmd, cwd=None, check=True):
        """
        Executa um comando dentro do sandbox.
        """
        full_cmd = f"fakeroot {cmd}" if self.use_fakeroot else cmd
        result = subprocess.run(full_cmd, shell=True, cwd=cwd or self.base_path,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                text=True)
        if check and result.returncode != 0:
            raise subprocess.CalledProcessError(result.returncode, cmd, result.stdout, result.stderr)
        return result

    def copy_to_sandbox(self, src, dest):
        """
        Copia arquivos ou diretórios para o sandbox.
        """
        dest_path = os.path.join(self.base_path, dest)
        if os.path.isdir(src):
            shutil.copytree(src, dest_path)
        else:
            shutil.copy2(src, dest_path)
        os.chmod(dest_path, 0o700)

    def destdir_path(self, subdir):
        """
        Retorna o caminho para o subdiretório de instalação.
        """
        path = os.path.join(self.base_path, subdir)
        os.makedirs(path, exist_ok=True)
        return path

    def clean(self):
        """
        Remove o diretório do sandbox, se não for para manter.
        """
        if not self.keep and self.base_path:
            shutil.rmtree(self.base_path, ignore_errors=True)
