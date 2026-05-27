import os
from pathlib import Path
import sys
import warnings


def configure_runtime_noise():
    os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")
    os.environ.setdefault("GLOG_minloglevel", "2")
    warnings.filterwarnings(
        "ignore",
        message=r"SymbolDatabase\.GetPrototype\(\) is deprecated\.",
        category=UserWarning,
        module=r"google\.protobuf\.symbol_database",
    )


configure_runtime_noise()


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from hand_gesture_media_controller.camera_controller import main


if __name__ == "__main__":
    main()
