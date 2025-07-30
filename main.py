import os
import sys
from dotenv import load_dotenv
from loguru import logger


load_dotenv()

SRC_PATH = os.path.join(os.path.dirname(__file__), "src")
if SRC_PATH not in sys.path:
    sys.path.append(SRC_PATH)


def main():
    try:
        from webui import demo
        demo.launch(
            server_name="0.0.0.0",
            server_port=7861,
            debug=True
        )

    except ImportError as ie:
        logger.error(f"Module import failure：{ie}")
        return 1

    except Exception as e:
        logger.error(f"Gradio failed to start：{e}")
        return 1

    return 0


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.info("Manual termination of the program")
        sys.exit(0)
    except Exception as e:
        logger.exception(f"Abnormalities in the starter：{e}")
        sys.exit(1)
