# About

Youtube Metadata Sync is a command-line tool to download metadata for the
playlists in your Youtube account and save it locally as json. It is well
suited to being called from cron, keeping your metadata up to date and only
producing output when new metadata is saved. In addition, it features a simple
plugin interface that can run scripts using the local metadata.

## Dependencies

    google_api_python_client

## First time usage

    python youtube_metadata_sync.py -o output_directory init

Authenticates the user, saves credentials to auth.json, then downloads
metadata. If metadata already exists, a warning will be displayed - after
confirmation, existing metadata will be deleted.

## Call from cron

    python youtube_metadata_sync.py -o output_directory update

Syncs new metadata, then executes any plugins.

## Plugins

A script placed in the 'plugins/' directory, with executable permissions, will
be executed exactly once for every entry in the metadata, being passed the url
of the metadata element as an argument. The script is executed in an empty
temporary directory, containing no files. If the script creates an output file
in this directory, that file will be moved to 'output_directory/files', and
renamed to the value of the 'safename' field in the metadata.

Once the script is called for a given metadata element, the metadata is
modified by adding a field 'status', with the value 'success' if the script
exited successfully (return value 0) or the value 'failure' otherwise. The
script won't be invoked as long as the 'status' field is set.

See the file 'plugin_config.cfg' for more, although the only option currently
implemented is changing 'command' to pass additional arguments to the plugin
script.
