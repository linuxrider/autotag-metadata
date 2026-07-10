"""Regenerate doc/images/tour-*.png from the live guided tour.

Steps through every ``TourStep`` in ``AutotagApp``'s guided tour, running each
step's ``on_enter`` exactly as the real tour does, and grabs a screenshot of the
whole window (with the coach-mark bubble and spotlight) after each one.

Run via the pixi task: ``pixi run -e dev screenshots``. Requires
QT_QPA_PLATFORM=offscreen and a real FONTCONFIG_FILE (both set by the task) —
without them Qt silently falls back to a low-quality bitmap font.
"""
# ********************************************************************
#  This file is part of autotag-metadata.
#
#        Copyright (C) 2026 Johannes Hermann
#
#  autotag-metadata is free software: you can redistribute it and/or
#  modify it under the terms of the GNU General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#
#  autotag-metadata is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with autotag-metadata. If not, see
#  <https://www.gnu.org/licenses/>.
# ********************************************************************

import re
from pathlib import Path

from PyQt6 import QtCore, QtWidgets

from autotag_metadata.app import AutotagApp

OUT_DIR = Path(__file__).parent / "images"


def _slug(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")


def main() -> None:
    app = QtWidgets.QApplication([])
    win = AutotagApp()
    win.resize(1400, 900)
    win.show()
    app.processEvents()

    tour = win._tour
    tour.start()
    app.processEvents()

    titles = tour.step_titles
    for i, title in enumerate(titles):
        tour.show_step(i)
        # Flush Qt's deferred-delete queue so cleared/rebuilt panels don't leave
        # stale widgets behind in the grab (plain processEvents() doesn't do this).
        QtCore.QCoreApplication.sendPostedEvents(None, QtCore.QEvent.Type.DeferredDelete.value)
        for _ in range(5):
            app.processEvents()
        fname = OUT_DIR / f"tour-{i:02d}-{_slug(title)}.png"
        win.grab().save(str(fname))
        print(f"saved {fname}")

    # The tour never reached its normal finish, so its scratch template/snippet/view
    # entries are still seeded in the config — stop() runs the same cleanup a real
    # "Done" click would (deletes them, restores the user's prior settings).
    tour.stop()
    win.config.save_settings()
    print(f"done, {len(titles)} steps")


if __name__ == "__main__":
    main()
