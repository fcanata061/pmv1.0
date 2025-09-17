from collections import deque

class DependencyResolver:
    """
    Gerencia a resolução de dependências de pacotes,
    suporte a revdep, grupos e flags USE.
    """

    def __init__(self, db):
        """
        db: dicionário simulando o banco de dados de pacotes
        Exemplo:
        db = {
            'gcc': {'dependencies': ['mpfr', 'gmp'], 'use': [], 'group': 'base'},
            'vim': {'dependencies': ['ncurses'], 'use': ['python'], 'group': 'editor'},
            ...
        }
        """
        self.db = db

    def resolve(self, packages):
        """
        Retorna uma lista de pacotes ordenados topologicamente para instalação.
        """
        resolved = []
        visited = set()

        def visit(pkg):
            if pkg in visited:
                return
            for dep in self.db.get(pkg, {}).get('dependencies', []):
                visit(dep)
            resolved.append(pkg)
            visited.add(pkg)

        for p in packages:
            visit(p)
        return resolved

    def revdep(self, package):
        """
        Retorna uma lista de pacotes que dependem do pacote fornecido.
        """
        reverse = []
        for pkg, data in self.db.items():
            if package in data.get('dependencies', []):
                reverse.append(pkg)
        return reverse

    def resolve_with_use(self, packages, enabled_use_flags):
        """
        Resolve dependências considerando flags USE habilitadas.
        """
        resolved = []
        visited = set()

        def visit(pkg):
            if pkg in visited:
                return
            pkg_data = self.db.get(pkg, {})
            # Adiciona dependências de USE habilitadas
            for use_flag in pkg_data.get('use', []):
                if use_flag in enabled_use_flags:
                    dep_pkg = use_flag  # Assumindo que o nome do pacote é igual à flag
                    visit(dep_pkg)
            # Adiciona dependências normais
            for dep in pkg_data.get('dependencies', []):
                visit(dep)
            resolved.append(pkg)
            visited.add(pkg)

        for p in packages:
            visit(p)
        return resolved

    def packages_in_group(self, group_name):
        """
        Retorna todos os pacotes pertencentes a um grupo específico.
        """
        return [pkg for pkg, data in self.db.items() if data.get('group') == group_name]
