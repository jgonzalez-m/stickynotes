project('stickynotes',
  version: '1.0.0',
  license: 'GPL-3.0-or-later',
  meson_version: '>= 0.59.0'
)

gnome = import('gnome')
python = import('python')
i18n = import('i18n')
# Directorios estándar
pkgdatadir = get_option('prefix') / get_option('datadir') / meson.project_name()
moduledir = pkgdatadir / 'stickynotes'

# Configuración para el script ejecutable
conf = configuration_data()
conf.set('PYTHON', python.find_installation('python3').full_path())
conf.set('VERSION', meson.project_version())
conf.set('localedir', get_option('prefix') / get_option('localedir'))
conf.set('pkgdatadir', pkgdatadir)

configure_file(
  input: 'src/stickynotes.in',
  output: 'stickynotes',
  configuration: conf,
  install: true,
  install_dir: get_option('bindir')
)

# Archivos Python
stickynotes_sources = [
  'src/stickynotes/__init__.py',
  'src/stickynotes/main.py',
  'src/stickynotes/window.py',
  'src/stickynotes/note.py',
  'src/stickynotes/window.ui',
  'src/stickynotes/gtk/help-overlay.ui'
]

install_data(stickynotes_sources, install_dir: moduledir)

# Recursos (UI files)
resources = gnome.compile_resources(
  'stickynotes',
  'src/stickynotes.gresource.xml',
  source_dir: 'src',  # <--- ESTE ES EL CAMBIO CLAVE
  gresource_bundle: true,
  install: true,
  install_dir: pkgdatadir
)

# Instalación de esquemas y archivos de escritorio, etc.
subdir('data')
subdir('po')
