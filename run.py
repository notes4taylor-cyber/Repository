#!/usr/bin/env python3
"""
MasterFlow - Run Script

Start the MasterFlow music mastering platform.
"""
import uvicorn
from app.core.config import settings


def main():
    """Run the MasterFlow application."""
    print("""
    ╔══════════════════════════════════════════════════════════════════╗
    ║                                                                  ║
    ║   ███╗   ███╗ █████╗ ███████╗████████╗███████╗██████╗           ║
    ║   ████╗ ████║██╔══██╗██╔════╝╚══██╔══╝██╔════╝██╔══██╗          ║
    ║   ██╔████╔██║███████║███████╗   ██║   █████╗  ██████╔╝          ║
    ║   ██║╚██╔╝██║██╔══██║╚════██║   ██║   ██╔══╝  ██╔══██╗          ║
    ║   ██║ ╚═╝ ██║██║  ██║███████║   ██║   ███████╗██║  ██║          ║
    ║   ╚═╝     ╚═╝╚═╝  ╚═╝╚══════╝   ╚═╝   ╚══════╝╚═╝  ╚═╝          ║
    ║                                                                  ║
    ║   ███████╗██╗      ██████╗ ██╗    ██╗                           ║
    ║   ██╔════╝██║     ██╔═══██╗██║    ██║                           ║
    ║   █████╗  ██║     ██║   ██║██║ █╗ ██║                           ║
    ║   ██╔══╝  ██║     ██║   ██║██║███╗██║                           ║
    ║   ██║     ███████╗╚██████╔╝╚███╔███╔╝                           ║
    ║   ╚═╝     ╚══════╝ ╚═════╝  ╚══╝╚══╝                            ║
    ║                                                                  ║
    ║   AI-Powered Music Mastering - Better Quality, Better Prices    ║
    ║                                                                  ║
    ╚══════════════════════════════════════════════════════════════════╝
    """)

    print(f"🚀 Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    print(f"📍 Server: http://{settings.HOST}:{settings.PORT}")
    print(f"📚 API Docs: http://{settings.HOST}:{settings.PORT}/docs")
    print()

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )


if __name__ == "__main__":
    main()
