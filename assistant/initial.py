# Ultroid - UserBot
# Copyright (C) 2021-2022 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

import re

from . import *

STRINGS = {
    1: """ **Thanks for Deploying Rizmil Userbot!**

• Userbot Ini Adalah Punya Ultroid, Dan Saya Hanya Tukang Kang .""",
    2: """** Tentang Rizmil**

 Rizmil adalah Telethon Userbot yang dapat dipasang dan kuat, dibuat dengan Python dari Scratch. Hal ini Bertujuan Untuk Meningkatkan Keamanan Bersama dengan Penambahan Fitur-Fitur Bermanfaat Lainnya. Full Translate By Me

❣ Kang by **[Kunth](https://t.me/kunthulsupport**""",
    3: """**💡• FAQs •**
    
**• Untuk Mengetahui Tentang Pembaruan**
  - Tanya **[Kunth](https://t.me/kunthulsupport**.""",
    4: f"""• `Untuk Mengetahui Semua Perintah yang Tersedia`

  - `{HNDLR}help`
  - `{HNDLR}cmds`""",
    5: """** Thanks for Reaching till END.**""",
}


@callback(re.compile("initft_(\\d+)"))
async def init_depl(e):
    CURRENT = int(e.data_match.group(1))
    if CURRENT == 5:
        return await e.edit(
            STRINGS[5],
            buttons=Button.inline("<< Kembali", "initbk_4"),
            link_preview=False,
        )

    await e.edit(
        STRINGS[CURRENT],
        buttons=[
            Button.inline("<<", f"initbk_{str(CURRENT - 1)}"),
            Button.inline(">>", f"initft_{str(CURRENT + 1)}"),
        ],
        link_preview=False,
    )


@callback(re.compile("initbk_(\\d+)"))
async def ineiq(e):
    CURRENT = int(e.data_match.group(1))
    if CURRENT == 1:
        return await e.edit(
            STRINGS[1],
            buttons=Button.inline("Mulai Kembali >>", "initft_2"),
            link_preview=False,
        )

    await e.edit(
        STRINGS[CURRENT],
        buttons=[
            Button.inline("<<", f"initbk_{str(CURRENT - 1)}"),
            Button.inline(">>", f"initft_{str(CURRENT + 1)}"),
        ],
        link_preview=False,
    )
