pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
moduledir = join_paths(pkgdatadir, 'stickynotes')
gnome = import('gnome')

gnome.compile_resources('stickynotes',
  'stickynotes.gresource.xml',
  gresource_bundle: true,
  install: true,
  install_dir: pkgdatadir,
  source_dir: meson.current_source_dir()  # This ensures it looks in the src directory
)

python = import('python')

conf = configuration_data()
conf.set('PYTHON', python.find_installation('python3').path())
conf.set('VERSION', meson.project_version())
conf.set('localedir', join_paths(get_option('prefix'), get_option('localedir')))
conf.set('pkgdatadir', pkgdatadir)

configure_file(
  input: 'stickynotes.in',
  output: 'stickynotes',
  configuration: conf,
  install: true,
  install_dir: get_option('bindir')
)

stickynotes_sources = [
  'stickynotes/__init__.py',
  'stickynotes/main.py',
  'stickynotes/window.py',
  'stickynotes/note.py',
  'stickynotes/window.ui',
  'stickynotes/gtk/help-overlay.ui'
]

install_data(stickynotes_sources, install_dir: moduledir)
