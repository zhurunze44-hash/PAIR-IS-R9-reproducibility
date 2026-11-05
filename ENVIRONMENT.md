# Software environment and execution authority

The public CI uses GitHub Ubuntu runners with Python 3.13, numpy==2.3.5 and sympy==1.14.0 from `requirements-verified.txt`. This is the environment for **constructed mathematical tests only**.

The original author-server K562, ENCODE, Replogle, CTRPv2 and GDSC production toolchains are separate historical environments. They are **not** reconstructed by the CI image. The original scoring scripts are byte-pinned in `evidence/native_input_pins.json`; source-era command lines and package versions must be recovered from original code and run records rather than back-filled from present-day libraries.

`reproduction/verify_native_inputs.py` uses only Python's standard library; Parquet diagnostics in `reproduction/recompute_frozen_counts.py` additionally require pyarrow in an isolated non-production environment. A successful CI does not establish original producer or frozen scoring result reproduction.
