import os
import sys
from dotenv import load_dotenv
from loguru import logger

load_dotenv()
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))


def main():
    try:
        from webui import demo

        demo.launch(
            server_name="0.0.0.0",
            server_port=7860,
            share=False,
            debug=True
        )

    except Exception as e:
        print(f"fail to activate：{str(e)}")
        return 1

    return 0


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        logger.debug(f"\nLauncher error：{str(e)}")
        sys.exit(1)
print(sys.executable)