"""
Rebuild the Healthy Respiratory Model from HLCA Full.

Use this in Colab (where hlca_full.h5ad lives) to regenerate the model artefacts
into models/respiratory_model/ after a build-logic change.

The build reads adata.X, which in the HLCA (CellxGene) is ALREADY log1p(CP10K),
and uses it as-is (no re-normalization). See app/services/respiratory_model.py.

RUN (Colab):
    !cd /content/HEALTH && HLCA_FULL_PATH=/content/hlca_full.h5ad python scripts/build_model.py
"""

import os
import sys

# Repo root on path so `import app...` works
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

# Point the build at the data file. Override with the env var if set.
os.environ.setdefault("HLCA_FULL_PATH", os.path.join(ROOT, "data", "hlca_full.h5ad"))


def main() -> int:
    from app.core.config import settings
    print(f"HLCA_FULL_PATH : {settings.HLCA_FULL_PATH}")
    print(f"Artefacts ->    : {settings.RESPIRATORY_MODEL_DIR}")
    if not settings.HLCA_FULL_PATH.exists():
        print(f"\nERROR: file not found: {settings.HLCA_FULL_PATH}")
        print("Set it, e.g.:  HLCA_FULL_PATH=/content/hlca_full.h5ad python scripts/build_model.py")
        return 1

    from app.services.respiratory_model import build_respiratory_model
    print("\nBuilding (reads adata.X as-is — already log1p CP10K) ...\n")
    meta = build_respiratory_model()

    print("\nDone. meta:")
    for k, v in meta.items():
        print(f"  {k}: {v}")
    print(f"\nArtefacts written to: {settings.RESPIRATORY_MODEL_DIR}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
