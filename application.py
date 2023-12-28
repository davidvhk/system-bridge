"""System Bridge."""
import asyncio
from dataclasses import dataclass
import logging
from os import path
import subprocess
import sys

from systembridgeshared.logger import setup_logger
from systembridgeshared.settings import Settings
from typer import Typer

python_mode = sys.argv[0].endswith(".py")

app = Typer()

settings = Settings()

logger = setup_logger(settings.data.log_level, "system-bridge")
logging.getLogger("zeroconf").setLevel(logging.ERROR)


@dataclass
class Application:
    """Application."""

    name: str
    path: str


applications = [
    Application(
        name="systembridgebackend",
        path=path.abspath(
            path.join(
                "systembridgebackend",
                f"systembridgebackend{'.exe' if sys.platform == 'win32' else ''}",
            )
        ),
    ),
    Application(
        name="systembridgegui",
        path=path.abspath(
            path.join(
                "systembridgegui",
                f"systembridgegui{'.exe' if sys.platform == 'win32' else ''}",
            )
        ),
    ),
]


async def application_launch_and_keep_alive(application: Application) -> None:
    """Launch application and keep alive."""
    app_path = (
        [sys.executable, "-m", application.name] if python_mode else [application.path]
    )
    logger.info("Launching application: %s", app_path)

    # Run application process
    with subprocess.Popen(
        app_path,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ) as process:
        # Wait for process to finish
        process.wait()

        if code := process.wait() == 0:
            logger.info(
                "Application %s exited normally with code %s",
                application.name,
                code,
            )
            return

    logger.error("Application %s exited with code %s", application.name, code)
    logger.info("Restarting application: %s", application)
    await application_launch_and_keep_alive(application)


@app.command(name="main", short_help="Launch Applications")
def main() -> None:
    """Launch Applications."""
    logger.info("Launching applications")

    async def run_all_applications():
        # Create a list of tasks
        tasks = [
            application_launch_and_keep_alive(application)
            for application in applications
        ]

        # Run all tasks concurrently
        await asyncio.gather(*tasks)

    # Run the async function
    asyncio.run(run_all_applications())


if __name__ == "__main__":
    app()
