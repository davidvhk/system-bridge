"""System Bridge: Server Handler - Media"""
import mimetypes
import os

import aiofiles
from plyer import storagepath
from sanic.request import Request
from sanic.response import HTTPResponse, file, json

QUERY_BASE = "base"
QUERY_PATH = "path"
QUERY_FILENAME = "filename"

BASE_DIRECTORIES = {
    "documents": storagepath.get_documents_dir(),
    "downloads": storagepath.get_downloads_dir(),
    "home": storagepath.get_home_dir(),
    "music": storagepath.get_music_dir(),
    "pictures": storagepath.get_pictures_dir(),
    "videos": storagepath.get_videos_dir(),
}


def get_directories() -> list[dict]:
    """Get directories"""
    directories = []
    for key, value in BASE_DIRECTORIES.items():
        directories.append(
            {
                "key": key,
                "path": value,
            }
        )
    return directories


def get_files(
    base_path: str,
    path: str,
) -> list[dict]:
    """Get files from path"""
    files = []
    for filename in os.listdir(path):
        files.append(
            get_file(BASE_DIRECTORIES[base_path], os.path.join(path, filename))
        )

    return files


def get_file(
    base_path: str,
    filepath: str,
) -> dict:
    """Get file from path"""
    stat = os.stat(filepath)

    mime_type = None
    if os.path.isfile(filepath):
        mime_type = mimetypes.guess_type(filepath)[0]

    return {
        "name": os.path.basename(filepath),
        "path": filepath.removeprefix(base_path)[1:],
        "fullpath": filepath,
        "size": stat.st_size,
        "last_accessed": stat.st_atime,
        "created": stat.st_ctime,
        "modified": stat.st_mtime,
        "is_directory": os.path.isdir(filepath),
        "is_file": os.path.isfile(filepath),
        "is_link": os.path.islink(filepath),
        "mime_type": mime_type,
    }


async def get_file_data(
    filepath: str,
) -> HTTPResponse:
    """Get file data"""
    return await file(filepath)


async def handler_media_directories(
    _: Request,
) -> HTTPResponse:
    """Handler for media directories"""
    return json(
        {
            "directories": get_directories(),
        }
    )


async def handler_media_files(
    request: Request,
) -> HTTPResponse:
    """Handler for media files"""
    if not (query_base := request.args.get(QUERY_BASE)):
        return json(
            {"message": "No base specified"},
            status=400,
        )
    query_path = request.args.get(QUERY_PATH)
    path = (
        os.path.join(BASE_DIRECTORIES[query_base], query_path)
        if query_path
        else BASE_DIRECTORIES[query_base]
    )
    if not os.path.exists(path):
        return json(
            {"message": "Cannot find path", "path": path},
            status=404,
        )
    if not os.path.isdir(path):
        return json(
            {"message": "Path is not a directory", "path": path},
            status=400,
        )

    return json(
        {
            "files": get_files(query_base, path),
            "path": path,
        }
    )


async def handler_media_file(
    request: Request,
) -> HTTPResponse:
    """Handler for media file requests"""
    if not (query_base := request.args.get(QUERY_BASE)):
        return json(
            {"message": "No base specified"},
            status=400,
        )
    if not (query_path := request.args.get(QUERY_PATH)):
        return json(
            {"message": "No path specified"},
            status=400,
        )
    path = os.path.join(BASE_DIRECTORIES[query_base], query_path)
    if not os.path.exists(path):
        return json(
            {"message": "Cannot find path", "path": path},
            status=404,
        )
    if not os.path.isfile(path):
        return json(
            {"message": "Path is not a file", "path": path},
            status=400,
        )

    return json(get_file(BASE_DIRECTORIES[query_base], path))


async def handler_media_file_data(
    request: Request,
) -> HTTPResponse:
    """Handler for media file requests"""
    if not (query_base := request.args.get(QUERY_BASE)):
        return json(
            {"message": "No base specified"},
            status=400,
        )
    query_path = request.args.get(QUERY_PATH)
    path = os.path.join(BASE_DIRECTORIES[query_base], query_path)
    if not path:
        return json(
            {"message": "Cannot find path", "path": path},
            status=400,
        )
    if not os.path.exists(path):
        return json(
            {"message": "File does not exist", "path": path},
            status=404,
        )
    if not os.path.isfile(path):
        return json(
            {"message": "Path is not a file", "path": path},
            status=400,
        )

    return await get_file_data(path)


async def handler_media_file_write(
    request: Request,
) -> HTTPResponse:
    """Handler for media file write requests"""
    if not (query_base := request.args.get(QUERY_BASE)):
        return json(
            {"message": "No base specified"},
            status=400,
        )
    if not (query_path := request.args.get(QUERY_PATH)):
        return json(
            {"message": "No path specified"},
            status=400,
        )
    if not (query_filename := request.args.get(QUERY_FILENAME)):
        return json(
            {"message": "No filename specified"},
            status=400,
        )
    path = os.path.join(BASE_DIRECTORIES[query_base], query_path)
    if not path:
        return json(
            {"message": "Cannot find path", "path": path},
            status=400,
        )
    if not request.body:
        return json(
            {"message": "No file specified"},
            status=400,
        )

    if not os.path.exists(path):
        os.makedirs(path)
    async with aiofiles.open(os.path.join(path, query_filename), "wb") as new_file:
        await new_file.write(request.body)
        await new_file.close()

    return json(
        {
            "message": "File uploaded",
            "path": path,
            "filename": query_filename,
        }
    )
