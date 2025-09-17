import argparse
from logger import Logger
from install import Installer
from remove import Remover
from build import Builder
from groups import GroupManager
from updater import Updater
from version_tracker import VersionTracker

# Banco de pacotes simulado
db = {}  # Este DB deve ser preenchido com receitas reais

# Logger
logger = Logger()

# Hooks (vazio por enquanto, pode ser configurado)
from hooks import Hooks
hooks = Hooks()

# Instâncias principais
installer = Installer(db, logger=logger, hooks=hooks)
remover = Remover(db, logger=logger, hooks=hooks)
group_manager = GroupManager(db, logger=logger, hooks=hooks)
updater = Updater(db, config_path='config.yaml', logger=logger, hooks=hooks)
version_tracker = VersionTracker(config_path='config.yaml', db=db, logger=logger)

# CLI
parser = argparse.ArgumentParser(description="Package Manager CLI")
subparsers = parser.add_subparsers(dest="command")

# install / i
parser_install = subparsers.add_parser('install', aliases=['i'], help="Instalar pacote")
parser_install.add_argument('package')

# remove / rm
parser_remove = subparsers.add_parser('remove', aliases=['rm'], help="Remover pacote")
parser_remove.add_argument('package')

# build / b
parser_build = subparsers.add_parser('build', aliases=['b'], help="Build pacote")
parser_build.add_argument('package')

# group / g
parser_group = subparsers.add_parser('group', aliases=['g'], help="Operações em grupo")
parser_group.add_argument('action', choices=['install', 'remove', 'list'])
parser_group.add_argument('group_name')

# update / up
parser_update = subparsers.add_parser('update', aliases=['up'], help="Atualizar pacotes")
parser_update.add_argument('target', nargs='?', default='all', help="Nome do pacote, grupo ou 'all'")

# search / s
parser_search = subparsers.add_parser('search', aliases=['s'], help="Buscar pacote")
parser_search.add_argument('query')

args = parser.parse_args()

# Execução
if args.command in ['install', 'i']:
    recipe = db.get(args.package)
    if recipe:
        installer.install_package(recipe)
    else:
        logger.error(f"Pacote {args.package} não encontrado.")

elif args.command in ['remove', 'rm']:
    remover.remove_package(args.package)

elif args.command in ['build', 'b']:
    recipe = db.get(args.package)
    if recipe:
        builder = Builder(recipe=recipe, logger=logger, hooks=hooks)
        builder.build()
    else:
        logger.error(f"Pacote {args.package} não encontrado.")

elif args.command in ['group', 'g']:
    if args.action == 'install':
        group_manager.install_group(args.group_name)
    elif args.action == 'remove':
        group_manager.remove_group(args.group_name)
    elif args.action == 'list':
        pkgs = group_manager.list_group(args.group_name)
        logger.info(f"Pacotes no grupo '{args.group_name}': {pkgs}")

elif args.command in ['update', 'up']:
    if args.target == 'all':
        updater.update_all()
    elif args.target in db:
        updater.update_package(args.target)
    else:
        # Assume que é um grupo
        updater.group_manager.update_group(args.target)

elif args.command in ['search', 's']:
    results = [pkg for pkg in db if args.query in pkg]
    for pkg in results:
        installed = '[✔]' if pkg in db else '[ ]'
        logger.info(f"{installed} {pkg}")
