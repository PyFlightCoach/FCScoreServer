from pydantic import BaseModel
from flightanalysis import ma
from flightdata import State
from typing import Any
from importlib.metadata import version
from importlib.util import find_spec
from numbers import Number
import subprocess
import os
import numpy as np
import pandas as pd
from flightdata.schemas import fcj


class LibraryVersions(BaseModel):
    flightanalysis: str
    flightdata: str
    pfc_geometry: str

    @staticmethod
    def get_version(lib: str):
        try:
            return (
                subprocess.run(
                    "git describe --tags",
                    shell=True,
                    check=True,
                    capture_output=True,
                    cwd=os.path.dirname(find_spec(lib.split("_")[-1]).origin),
                )
                .stdout.decode("utf-8")
                .strip()
            )
        except subprocess.CalledProcessError:
            return version(lib)


versions = LibraryVersions(
    **{
        k: LibraryVersions.get_version(k)
        for k in ["flightanalysis", "flightdata", "pfc_geometry"]
    }
)


def create_state(sts: list[dict]) -> State:
    return State(
        pd.DataFrame([fl.__dict__ for fl in sts])
        .set_index("t", drop=False)
        .infer_objects(copy=False)  # .fillna(value=np.nan)
        .dropna(axis=1)
    )


class AnalysisOutput(BaseModel):
    els: list[fcj.El]
    results: list[fcj.Score] | None
    fa_version: str
    info: str
    mdef: dict[str, Any]
    flown: list[dict]
    manoeuvre: dict[str, Any]
    template: list[dict]
    corrected: dict[str, Any] | None
    corrected_template: list[dict] | None
    full_scores: dict | None

    @staticmethod
    def build(
        man: ma.Scored | ma.Complete | ma.Alignment | ma.Basic,
        difficulty: int | str = "all",
        truncate: bool | str = "all",
        msg: str = None,
    ):
        df = man.flown.label_ranges("element").iloc[:, :3]
        df.columns = ["name", "start", "stop"]

        if isinstance(man, ma.Scored):
            if not msg:
                msg = f"Analysis Finished at {pd.Timestamp.now().strftime("%H:%M:%S")}"
        else:
            msg = f"Analysis Failed at {pd.Timestamp.now().strftime("%H:%M:%S")}"

        def ifscored(val):
            return val if isinstance(man, ma.Scored) else None

        return AnalysisOutput(
            els=[fcj.El(**v) for v in df.to_dict("records")],
            results=ifscored(
                [
                    fcj.Score(
                        score=fcj.ScoreValues(**man.scores.score_summary(diff, trunc)),
                        properties=fcj.ScoreProperties(difficulty=diff, truncate=trunc),
                    )
                    for diff in (
                        [difficulty] if isinstance(difficulty, Number) else [1, 2, 3]
                    )
                    for trunc in (
                        [truncate] if isinstance(truncate, bool) else [False, True]
                    )
                ]
            ),
            fa_version=versions.flightanalysis,
            info=msg,
            mdef=man.mdef.to_dict(True),
            flown=man.flown.to_dict(),
            manoeuvre=man.manoeuvre.to_dict(),
            template=man.template.to_dict(),
            corrected=ifscored(man.corrected).to_dict(),
            corrected_template=ifscored(man.corrected_template).to_dict(),
            full_scores=ifscored(man.scores.to_dict()),
        )
