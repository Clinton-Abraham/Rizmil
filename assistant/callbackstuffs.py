# Ultroid - UserBot
# Copyright (C) 2021-2022 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.


import asyncio
import re
import sys
import time
from asyncio.exceptions import TimeoutError as AsyncTimeOut
from os import execl, remove
from random import choice

from bs4 import BeautifulSoup as bs

try:
    from pyUltroid.fns.gDrive import GDriveManager
except ImportError:
    GDriveManager = None
from telegraph import upload_file as upl
from telethon import Button, events
from telethon.tl.types import MessageMediaWebPage
from telethon.utils import get_peer_id

from pyUltroid.fns.helper import fast_download, progress
from pyUltroid.fns.tools import Carbon, async_searcher, get_paste, telegraph_client
from pyUltroid.startup.loader import Loader

from . import *

# --------------------------------------------------------------------#
telegraph = telegraph_client()
GDrive = GDriveManager() if GDriveManager else None
# --------------------------------------------------------------------#


def text_to_url(event):
    """function to get media url (with|without) Webpage"""
    if isinstance(event.media, MessageMediaWebPage):
        webpage = event.media.webpage
        if not isinstance(webpage, types.WebPageEmpty) and webpage.type in ["photo"]:
            return webpage.display_url
    return event.text


# --------------------------------------------------------------------#

_buttons = {
    "otvars": {
        "text": "Variabel lain untuk diatur Rizmil Userbot:",
        "buttons": [
            [
                Button.inline("Tag Log", data="taglog"),
                Button.inline("Super Fban", data="cbs_sfban"),
            ],
            [
                Button.inline("Sudo Mode", data="sudo"),
                Button.inline("Handler", data="hhndlr"),
            ],
            [
                Button.inline("Extra Plugins", data="plg"),
                Button.inline("Addons", data="eaddon"),
            ],
            [
                Button.inline("Emoji In Help", data="emoj"),
                Button.inline("Set GDrive", data="gdrive"),
            ],
            [
                Button.inline("Inline Pic", data="inli_pic"),
                Button.inline("Sudo Handler", data="shndlr"),
            ],
            [Button.inline("Dual Mode", "cbs_oofdm")],
            [Button.inline("« Kembali", data="setter")],
        ],
    },
    "sfban": {
        "text": "Pengaturan SuperFban:",
        "buttons": [
            [Button.inline("FBAN Group", data="sfgrp")],
            [Button.inline("Exclude Feds", data="abs_sfexf")],
            [Button.inline("« Kembali", data="cbs_otvars")],
        ],
    },
    "apauto": {
        "text": "Ini akan otomatis disetujui pada pesan keluar",
        "buttons": [
            [Button.inline("Auto Approve On", data="apon")],
            [Button.inline("Auto Approve Off", data="apof")],
            [Button.inline("« Kembali", data="cbs_pmcstm")],
        ],
    },
    "alvcstm": {
        "text": f"Sesuaikan {HNDLR} Anda secara langsung. Pilih dari opsi di bawah ini -",
        "buttons": [
            [Button.inline("Alive Text", data="abs_alvtx")],
            [Button.inline("Alive Media", data="alvmed")],
            [Button.inline("Delete Alive Media", data="delmed")],
            [Button.inline("« Kembali", data="setter")],
        ],
    },
    "pmcstm": {
        "text": "Sesuaikan Pengaturan PMPERMIT Anda -",
        "buttons": [
            [
                Button.inline("Pm Text", data="pmtxt"),
                Button.inline("Pm Media", data="pmmed"),
            ],
            [
                Button.inline("Auto Approve", data="cbs_apauto"),
                Button.inline("PMLOG", data="pml"),
            ],
            [
                Button.inline("Set Warns", data="swarn"),
                Button.inline("Delete Pm Media", data="delpmmed"),
            ],
            [Button.inline("Jenis PMPermit", data="cbs_pmtype")],
            [Button.inline("« Kembali", data="cbs_ppmset")],
        ],
    },
    "pmtype": {
        "text": "Pilih jenis PMPermit yang dibutuhkan.",
        "buttons": [
            [Button.inline("Inline", data="inpm_in")],
            [Button.inline("Normal", data="inpm_no")],
            [Button.inline("« Kembali", data="cbs_pmcstm")],
        ],
    },
    "ppmset": {
        "text": "Pengaturan Izin PM:",
        "buttons": [
            [Button.inline("PMPermit Aktif", data="pmon")],
            [Button.inline("PMPermit Tidak Aktif", data="pmoff")],
            [Button.inline("Kostum PMPermit", data="cbs_pmcstm")],
            [Button.inline("« Kembali", data="setter")],
        ],
    },
    "chatbot": {
        "text": "Dari Fitur Ini Anda dapat mengobrol dengan Seseorang Melalui Bot Asisten Anda.",
        "buttons": [
            [
                Button.inline("Chat Bot  Aktif", data="onchbot"),
                Button.inline("Chat Bot  Tidak Aktif", data="ofchbot"),
            ],
            [
                Button.inline("Bot Welcome", data="bwel"),
                Button.inline("Bot Welcome Media", data="botmew"),
            ],
            [Button.inline("Bot Info Text", data="botinfe")],
            [Button.inline("Force Subscribe", data="pmfs")],
            [Button.inline("« Kembali", data="setter")],
        ],
    },
    "vcb": {
        "text": "Dari Fitur Ini Anda dapat memutar lagu dalam obrolan suara grup",
        "buttons": [
            [Button.inline("VC Session", data="abs_vcs")],
            [Button.inline("« Kembali", data="setter")],
        ],
    },
    "oofdm": {
        "text": "Tentang [Dual Mode](https://t.me/kunthulsupport)",
        "buttons": [
            [
                Button.inline("Dual Mode On", "dmof"),
                Button.inline("Dual Mode Off", "dmof"),
            ],
            [Button.inline("Dual Mode Handler", "dmhn")],
            [Button.inline("« Kembali", data="cbs_otvars")],
        ],
    },
    "apiset": {
        "text": get_string("ast_1"),
        "buttons": [
            [Button.inline("Remove.bg API", data="abs_rmbg")],
            [Button.inline("DEEP API", data="abs_dapi")],
            [Button.inline("OCR API", data="abs_oapi")],
            [Button.inline("« Kembali", data="setter")],
        ],
    },
}

_convo = {
    "rmbg": {
        "var": "RMBG_API",
        "name": "Remove.bg API Key",
        "text": get_string("ast_2"),
        "back": "cbs_apiset",
    },
    "dapi": {
        "var": "DEEP_AI",
        "name": "Deep AI Api Key",
        "text": "Get Your Deep Api from deepai.org and send here.",
        "back": "cbs_apiset",
    },
    "oapi": {
        "var": "OCR_API",
        "name": "Ocr Api Key",
        "text": "Get Your OCR api from ocr.space and send that Here.",
        "back": "cbs_apiset",
    },
    "pmlgg": {
        "var": "PMLOGGROUP",
        "name": "Pm Log Group",
        "text": "Send chat id of chat which you want to save as Pm log Group.",
        "back": "pml",
    },
    "vcs": {
        "var": "VC_SESSION",
        "name": "Sesi Obrolan Suara",
        "text": "**Sesi Obrolan Suara**\nMasukkan sesi Baru yang Anda buat untuk bot vc.\n\nGunakan /cancel untuk menghentikan operasi.",
        "back": "cbs_vcb",
    },
    "settag": {
        "var": "TAG_LOG",
        "name": "Tag Log Group",
        "text": f"Buat grup, tambahkan asisten Anda, dan jadikan admin.\nDapatkan `{HNDLR}id` grup itu dan kirimkan ke sini untuk log tag.\n\nGunakan /cancel untuk membatalkan.",
        "back": "taglog",
    },
    "alvtx": {
        "var": "ALIVE_TEXT",
        "name": "Alive Text",
        "text": "**Alive Text**\nMasukkan teks hidup baru.\n\nGunakan /cancel untuk menghentikan operasi.",
        "back": "cbs_alvcstm",
    },
    "sfexf": {
        "var": "EXCLUDE_FED",
        "name": "Excluded Fed",
        "text": "Kirim ID Fed yang ingin Anda kecualikan dalam larangan. Pisahkan dengan spasi.\neg`id1 id2 id3`\nTetapkan sebagai `Tidak ada` jika Anda tidak menginginkannya.\nGunakan /cancel untuk kembali.",
        "back": "cbs_sfban",
    },
}


TOKEN_FILE = "resources/auths/auth_token.txt"


@callback(
    re.compile(
        "sndplug_(.*)",
    ),
    owner=True,
)
async def send(eve):
    key, name = (eve.data_match.group(1)).decode("UTF-8").split("_")
    thumb = "resources/extras/inline.jpg"
    await eve.answer("❀ Sending ❀")
    data = f"uh_{key}_"
    index = None
    if "|" in name:
        name, index = name.split("|")
    key = "plugins" if key == "Official" else key.lower()
    plugin = f"{key}/{name}.py"
    _ = f"pasta-{plugin}"
    if index is not None:
        data += f"|{index}"
        _ += f"|{index}"
    buttons = [
        [
            Button.inline(
                "« ᴘᴀꜱᴛᴇ »",
                data=_,
            )
        ],
        [
            Button.inline("« Kembali", data=data),
        ],
    ]
    try:
        await eve.edit(file=plugin, thumb=thumb, buttons=buttons)
    except Exception as er:
        await eve.answer(str(er), alert=True)


heroku_api, app_name = Var.HEROKU_API, Var.HEROKU_APP_NAME


@callback("updatenow", owner=True)
async def update(eve):
    repo = Repo()
    ac_br = repo.active_branch
    ups_rem = repo.remote("upstream")
    if heroku_api:
        import heroku3

        try:
            heroku = heroku3.from_key(heroku_api)
            heroku_app = None
            heroku_applications = heroku.apps()
        except BaseException as er:
            LOGS.exception(er)
            return await eve.edit("`Wrong HEROKU_API.`")
        for app in heroku_applications:
            if app.name == app_name:
                heroku_app = app
        if not heroku_app:
            await eve.edit("`Wrong HEROKU_APP_NAME.`")
            repo.__del__()
            return
        await eve.edit(get_string("clst_1"))
        ups_rem.fetch(ac_br)
        repo.git.reset("--hard", "FETCH_HEAD")
        heroku_git_url = heroku_app.git_url.replace(
            "https://", f"https://api:{heroku_api}@"
        )

        if "heroku" in repo.remotes:
            remote = repo.remote("heroku")
            remote.set_url(heroku_git_url)
        else:
            remote = repo.create_remote("heroku", heroku_git_url)
        try:
            remote.push(refspec=f"HEAD:refs/heads/{ac_br}", force=True)
        except GitCommandError as error:
            await eve.edit(f"`Here is the error log:\n{error}`")
            repo.__del__()
            return
        await eve.edit("`Berhasil Diperbarui!\nMulai ulang, harap tunggu...`")
    else:
        await eve.edit(get_string("clst_1"))
        call_back()
        await bash("git pull && pip3 install -r requirements.txt")
        execl(sys.executable, sys.executable, "-m", "pyUltroid")


@callback(re.compile("changes(.*)"), owner=True)
async def changes(okk):
    match = okk.data_match.group(1).decode("utf-8")
    await okk.answer(get_string("clst_3"))
    repo = Repo.init()
    button = [[Button.inline("Memperbarui sekarang", data="updatenow")]]
    changelog, tl_chnglog = await gen_chlog(
        repo, f"HEAD..upstream/{repo.active_branch}"
    )
    cli = "\n\nKlik tombol di bawah ini untuk memperbarui!"
    if not match:
        try:
            if len(tl_chnglog) > 700:
                tl_chnglog = f"{tl_chnglog[:700]}..."
                button.append([Button.inline("View Complete", "Perubahan Semua")])
            await okk.edit("࿇ Menulis Changelogs 📝 •")
            img = await Carbon(
                file_name="changelog",
                code=tl_chnglog,
                backgroundColor=choice(ATRA_COL),
                language="md",
            )
            return await okk.edit(
                f"**×͜× Rizmil Userbot ×͜×**{cli}", file=img, buttons=button
            )
        except Exception as er:
            LOGS.exception(er)
    changelog_str = changelog + cli
    if len(changelog_str) > 1024:
        await okk.edit(get_string("upd_4"))
        await asyncio.sleep(2)
        with open("updates.txt", "w+") as file:
            file.write(tl_chnglog)
        await okk.edit(
            get_string("upd_5"),
            file="updates.txt",
            buttons=button,
        )
        remove("updates.txt")
        return
    await okk.edit(
        changelog_str,
        buttons=button,
        parse_mode="html",
    )


@callback(
    re.compile(
        "pasta-(.*)",
    ),
    owner=True,
)
async def _(e):
    ok = (e.data_match.group(1)).decode("UTF-8")
    index = None
    if "|" in ok:
        ok, index = ok.split("|")
    with open(ok, "r") as hmm:
        _, key = await get_paste(hmm.read())
    link = f"https://spaceb.in/{key}"
    raw = f"https://spaceb.in/api/v1/documents/{key}/raw"
    if not _:
        return await e.answer(key[:30], alert=True)
    if ok.startswith("addons"):
        key = "Addons"
    elif ok.startswith("vcbot"):
        key = "VCBot"
    else:
        key = "Official"
    data = f"uh_{key}_"
    if index is not None:
        data += f"|{index}"
    await e.edit(
        "",
        buttons=[
            [Button.url("Link", link), Button.url("Raw", raw)],
            [Button.inline("« Kembali", data=data)],
        ],
    )


@callback(re.compile("cbs_(.*)"), owner=True)
async def _edit_to(event):
    match = event.data_match.group(1).decode("utf-8")
    data = _buttons.get(match)
    if not data:
        return
    await event.edit(data["text"], buttons=data["buttons"], link_preview=False)


@callback(re.compile("abs_(.*)"), owner=True)
async def convo_handler(event: events.CallbackQuery):
    match = event.data_match.group(1).decode("utf-8")
    if not _convo.get(match):
        return
    await event.delete()
    get_ = _convo[match]
    back = get_["back"]
    async with event.client.conversation(event.sender_id) as conv:
        await conv.send_message(get_["text"])
        response = conv.wait_event(events.NewMessage(chats=event.sender_id))
        response = await response
        themssg = response.message.message
        if themssg == "/cancel":
            return await conv.send_message(
                "Dibatalkan!!",
                buttons=get_back_button(back),
            )
        await setit(event, get_["var"], themssg)
        await conv.send_message(
            f"{get_['name']} berubah menjadi `{themssg}`",
            buttons=get_back_button(back),
        )


@callback("authorise", owner=True)
async def _(e):
    if not e.is_private:
        return
    url = GDrive._create_token_file()
    await e.edit("Buka tautan di bawah ini dan kirim kodenya!")
    async with asst.conversation(e.sender_id) as conv:
        await conv.send_message(url)
        code = await conv.get_response()
        if GDrive._create_token_file(code=code.text):
            await conv.send_message(
                "`Berhasil!\nAnda sudah siap untuk menggunakan Google Drive dengan Rizmil Userbot.`",
                buttons=Button.inline("Main Menu", data="setter"),
            )
        else:
            await conv.send_message("Salah kode! Klik otorisasi lagi.")


@callback("folderid", owner=True, func=lambda x: x.is_private)
async def _(e):
    if not e.is_private:
        return
    msg = (
        "Send your FOLDER ID\n\n"
        + "For FOLDER ID:\n"
        + "1. Open Google Drive App.\n"
        + "2. Create Folder.\n"
        + "3. Make that folder public.\n"
        + "4. Send link of that folder."
    )
    await e.delete()
    async with asst.conversation(e.sender_id, timeout=150) as conv:
        await conv.send_message(msg)
        repl = await conv.get_response()
        id = repl.text
        if id.startswith("https"):
            id = id.split("?id=")[-1]
        udB.set_key("GDRIVE_FOLDER_ID", id)
        await repl.reply(
            "`Sukses.`",
            buttons=get_back_button("gdrive"),
        )


@callback("gdrive", owner=True)
async def _(e):
    if not e.is_private:
        return
    await e.edit(
        "Klik Otorisasi dan kirim kodenya.\n\nAnda dapat menggunakan ID Klien dan Rahasia Anda sendiri",
        buttons=[
            [
                Button.inline("Folder ID", data="folderid"),
                Button.inline("Authorise", data="authorise"),
            ],
            [Button.inline("« Kembali", data="cbs_otvars")],
        ],
        link_preview=False,
    )


@callback("dmof", owner=True)
async def rhwhe(e):
    if udB.get_key("DUAL_MODE"):
        udB.del_key("DUAL_MODE")
        key = "Off"
    else:
        udB.set_key("DUAL_MODE", "True")
        key = "On"
    Msg = f"Dual Mode : {key}"
    await e.edit(Msg, buttons=get_back_button("cbs_otvars"))


@callback("dmhn", owner=True)
async def hndlrr(event):
    await event.delete()
    pru = event.sender_id
    var = "DUAL_HNDLR"
    name = "Dual Handler"
    CH = udB.get_key(var) or "/"
    async with event.client.conversation(pru) as conv:
        await conv.send_message(
            f"Kirim Simbol Yang Anda inginkan sebagai Pengendali/Pemicu untuk menggunakan bot Asisten\nPenangan Anda Saat Ini adalah [ `{CH}` ]\n\n gunakan /cancel untuk membatalkan.",
        )
        response = conv.wait_event(events.NewMessage(chats=pru))
        response = await response
        themssg = response.message.message
        if themssg == "/cancel":
            await conv.send_message(
                "Dibatalkan!!",
                buttons=get_back_button("cbs_otvars"),
            )
        elif len(themssg) > 1:
            await conv.send_message(
                "Pengendali Salah",
                buttons=get_back_button("cbs_otvars"),
            )
        else:
            await setit(event, var, themssg)
            await conv.send_message(
                f"{name} berubah menjadi {themssg}",
                buttons=get_back_button("cbs_otvars"),
            )


@callback("emoj", owner=True)
async def emoji(event):
    await event.delete()
    pru = event.sender_id
    var = "EMOJI_IN_HELP"
    name = f"Emoji di `{HNDLR}menu bantuan`"
    async with event.client.conversation(pru) as conv:
        await conv.send_message("Kirim emoji yang ingin Anda setel .\n\nGunakan /cancel untuk membatalkan.")
        response = conv.wait_event(events.NewMessage(chats=pru))
        response = await response
        themssg = response.message.message
        if themssg == "/cancel":
            await conv.send_message(
                "Dibatalkan!!",
                buttons=get_back_button("cbs_otvars"),
            )
        elif themssg.startswith(("/", HNDLR)):
            await conv.send_message(
                "Emoji salah",
                buttons=get_back_button("cbs_otvars"),
            )
        else:
            await setit(event, var, themssg)
            await conv.send_message(
                f"{name} berubah menjadi {themssg}\n",
                buttons=get_back_button("cbs_otvars"),
            )


@callback("plg", owner=True)
async def pluginch(event):
    await event.delete()
    pru = event.sender_id
    var = "PLUGIN_CHANNEL"
    name = "Plugin Channel"
    async with event.client.conversation(pru) as conv:
        await conv.send_message(
            "Kirim id atau nama pengguna saluran tempat Anda ingin memasang semua plugin\n\nSaluran Gunakan /cancel untuk membatalkan.",
        )
        response = conv.wait_event(events.NewMessage(chats=pru))
        response = await response
        themssg = response.message.message
        if themssg == "/cancel":
            await conv.send_message(
                "Dibatalkan!!",
                buttons=get_back_button("cbs_otvars"),
            )
        elif themssg.startswith(("/", HNDLR)):
            await conv.send_message(
                "Saluran salah",
                buttons=get_back_button("cbs_otvars"),
            )
        else:
            await setit(event, var, themssg)
            await conv.send_message(
                f"{name} diubah menjadi {themssg}\n Setelah Mengatur Semua Hal Lakukan Mulai Ulang",
                buttons=get_back_button("cbs_otvars"),
            )


@callback("hhndlr", owner=True)
async def hndlrr(event):
    await event.delete()
    pru = event.sender_id
    var = "HNDLR"
    name = "Handler/ Trigger"
    async with event.client.conversation(pru) as conv:
        await conv.send_message(
            f"Kirim Simbol Yang Anda inginkan sebagai Pengendali/Pemicu untuk menggunakan bot\nPenangan Saat Ini adalah [ `{HNDLR}` ]\n\n gunakan /cancel untuk membatalkan.",
        )
        response = conv.wait_event(events.NewMessage(chats=pru))
        response = await response
        themssg = response.message.message
        if themssg == "/cancel":
            await conv.send_message(
                "Dibatalkan!!",
                buttons=get_back_button("cbs_otvars"),
            )
        elif len(themssg) > 1:
            await conv.send_message(
                "Pengendali Salah",
                buttons=get_back_button("cbs_otvars"),
            )
        elif themssg.startswith(("/", "#", "@")):
            await conv.send_message(
                "Ini tidak dapat digunakan sebagai penangan",
                buttons=get_back_button("cbs_otvars"),
            )
        else:
            await setit(event, var, themssg)
            await conv.send_message(
                f"{name} berubah menjadi {themssg}",
                buttons=get_back_button("cbs_otvars"),
            )


@callback("shndlr", owner=True)
async def hndlrr(event):
    await event.delete()
    pru = event.sender_id
    var = "SUDO_HNDLR"
    name = "Sudo Handler"
    async with event.client.conversation(pru) as conv:
        await conv.send_message(
            "Kirim Simbol Yang Anda inginkan sebagai Sudo Handler/Pemicu untuk menggunakan bot\n\n gunakan /cancel untuk membatalkan."
        )

        response = conv.wait_event(events.NewMessage(chats=pru))
        response = await response
        themssg = response.message.message
        if themssg == "/cancel":
            await conv.send_message(
                "Dibatalkan!!",
                buttons=get_back_button("cbs_otvars"),
            )
        elif len(themssg) > 1:
            await conv.send_message(
                "Pengendali Salah",
                buttons=get_back_button("cbs_otvars"),
            )
        elif themssg.startswith(("/", "#", "@")):
            await conv.send_message(
                "Ini tidak dapat digunakan sebagai penangan",
                buttons=get_back_button("cbs_otvars"),
            )
        else:
            await setit(event, var, themssg)
            await conv.send_message(
                f"{name} berubah menjadi {themssg}",
                buttons=get_back_button("cbs_otvars"),
            )


@callback("taglog", owner=True)
async def tagloggrr(e):
    BUTTON = [
        [Button.inline("SET TAG LOG", data="abs_settag")],
        [Button.inline("DELETE TAG LOG", data="deltag")],
        get_back_button("cbs_otvars"),
    ]
    await e.edit(
        "Pilih Opsi",
        buttons=BUTTON,
    )


@callback("deltag", owner=True)
async def _(e):
    udB.del_key("TAG_LOG")
    await e.answer("Selesai!!! Pencatat Tag telah dimatikan")


@callback("eaddon", owner=True)
async def pmset(event):
    BT = (
        [Button.inline("Addons  Off", data="edof")]
        if udB.get_key("ADDONS")
        else [Button.inline("Addons  On", data="edon")]
    )

    await event.edit(
        "Tambah ~ Plugin Ekstra:",
        buttons=[
            BT,
            [Button.inline("« Kembali", data="cbs_otvars")],
        ],
    )


@callback("edon", owner=True)
async def eddon(event):
    var = "ADDONS"
    await setit(event, var, "True")
    await event.edit(
        "Selesai! ADDONS telah diaktifkan!!\n\n Setelah Mengatur Semua Hal, Lakukan Mulai Ulang",
        buttons=get_back_button("eaddon"),
    )


@callback("edof", owner=True)
async def eddof(event):
    udB.set_key("ADDONS", "False")
    await event.edit(
        "Selesai! ADDONS telah dimatikan!! Setelah Mengatur Semua Hal Lakukan Restart",
        buttons=get_back_button("eaddon"),
    )


@callback("sudo", owner=True)
async def pmset(event):
    BT = (
        [Button.inline("Sudo Mode  Off", data="ofsudo")]
        if udB.get_key("SUDO")
        else [Button.inline("Sudo Mode On", data="onsudo")]
    )

    await event.edit(
        f"MODE SUDO ~ Beberapa orang dapat menggunakan Bot Anda yang Anda pilih. Untuk mengetahui Selengkapnya gunakan `{HNDLR}help Sudo`",
        buttons=[
            BT,
            [Button.inline("« Kembali", data="cbs_otvars")],
        ],
    )


@callback("onsudo", owner=True)
async def eddon(event):
    var = "SUDO"
    await setit(event, var, "True")
    await event.edit(
        "Selesai! MODE SUDO telah diaktifkan!!\n\n Setelah Mengatur Semua Hal Lakukan Restart",
        buttons=get_back_button("sudo"),
    )


@callback("ofsudo", owner=True)
async def eddof(event):
    var = "SUDO"
    await setit(event, var, "False")
    await event.edit(
        "Selesai! MODE SUDO telah dimatikan!! Setelah Mengatur Semua Hal Lakukan Restart",
        buttons=get_back_button("sudo"),
    )


@callback("sfgrp", owner=True)
async def sfgrp(event):
    await event.delete()
    name = "FBan Group ID"
    var = "FBAN_GROUP_ID"
    pru = event.sender_id
    async with asst.conversation(pru) as conv:
        await conv.send_message(
            f"Buat grup, tambahkan @MissRose_Bot, kirim `{HNDLR}id`, salin dan kirim ke sini.\nGunakan /cancel untuk kembali.",
        )
        response = conv.wait_event(events.NewMessage(chats=pru))
        response = await response
        themssg = response.message.message
        if themssg == "/cancel":
            return await conv.send_message(
                "Dibatalkan!!",
                buttons=get_back_button("cbs_sfban"),
            )
        await setit(event, var, themssg)
        await conv.send_message(
            f"{name} berubah menjadi {themssg}",
            buttons=get_back_button("cbs_sfban"),
        )


@callback("alvmed", owner=True)
async def media(event):
    await event.delete()
    pru = event.sender_id
    var = "ALIVE_PIC"
    name = "Alive Media"
    async with event.client.conversation(pru) as conv:
        await conv.send_message(
            "**Alive Media**\Kirimkan saya pic/gif/media untuk ditetapkan sebagai media hidup.\on\nGunakan /cancel untuk menghentikan operasi.",
        )
        response = await conv.get_response()
        try:
            themssg = response.message
            if themssg == "/cancel":
                return await conv.send_message(
                    "Operasi dibatalkan!!",
                    buttons=get_back_button("cbs_alvcstm"),
                )
        except BaseException as er:
            LOGS.exception(er)
        if (
            not (response.text).startswith("/")
            and response.text != ""
            and (not response.media or isinstance(response.media, MessageMediaWebPage))
        ):
            url = text_to_url(response)
        elif response.sticker:
            url = response.file.id
        else:
            media = await event.client.download_media(response, "alvpc")
            try:
                x = upl(media)
                url = f"https://graph.org/{x[0]}"
                remove(media)
            except BaseException as er:
                LOGS.exception(er)
                return await conv.send_message(
                    "Dihentikan.",
                    buttons=get_back_button("cbs_alvcstm"),
                )
        await setit(event, var, url)
        await conv.send_message(
            f"{name} telah di atur.",
            buttons=get_back_button("cbs_alvcstm"),
        )


@callback("delmed", owner=True)
async def dell(event):
    try:
        udB.del_key("ALIVE_PIC")
        return await event.edit(
            get_string("clst_5"), buttons=get_back_button("cbs_alabs_vcstm")
        )
    except BaseException as er:
        LOGS.exception(er)
        return await event.edit(
            get_string("clst_4"),
            buttons=get_back_button("cbs_alabs_vcstm"),
        )


@callback("inpm_in", owner=True)
async def inl_on(event):
    var = "INLINE_PM"
    await setit(event, var, "True")
    await event.edit(
        "Selesai!! Jenis PMPermit telah disetel ke inline!",
        buttons=[[Button.inline("« Kembali", data="cbs_pmtype")]],
    )


@callback("inpm_no", owner=True)
async def inl_on(event):
    var = "INLINE_PM"
    await setit(event, var, "False")
    await event.edit(
        "Selesai!! Jenis PMPermit telah disetel ke normal!",
        buttons=[[Button.inline("« Kembali", data="cbs_pmtype")]],
    )


@callback("pmtxt", owner=True)
async def name(event):
    await event.delete()
    pru = event.sender_id
    var = "PM_TEXT"
    name = "PM Text"
    async with event.client.conversation(pru) as conv:
        await conv.send_message(
            "**Teks PM**\nMasukkan teks izin baru.\n\nu dapat menggunakan `{name}` `{fullname}` `{count}` `{mention}` `{username}` untuk mendapatkan ini dari pengguna Juga\n \nGunakan /cancel untuk menghentikan operasi.",
        )
        response = conv.wait_event(events.NewMessage(chats=pru))
        response = await response
        themssg = response.message.message
        if themssg == "/cancel":
            return await conv.send_message(
                "Dibatalkan!!",
                buttons=get_back_button("cbs_pmcstm"),
            )
        if len(themssg) > 4090:
            return await conv.send_message(
                "Pesan terlalu panjang!\nTolong beri pesan yang lebih pendek!!",
                buttons=get_back_button("cbs_pmcstm"),
            )
        await setit(event, var, themssg)
        await conv.send_message(
            f"{name} perubahan ke {themssg}\in\After Setting All Things Do restart",
            buttons=get_back_button("cbs_pmcstm"),
        )


@callback("swarn", owner=True)
async def name(event):
    m = range(1, 10)
    tultd = [Button.inline(f"{x}", data=f"wrns_{x}") for x in m]
    lst = list(zip(tultd[::3], tultd[1::3], tultd[2::3]))
    lst.append([Button.inline("« Kembali", data="cbs_pmcstm")])
    await event.edit(
        "Pilih jumlah peringatan untuk pengguna sebelum diblokir di PM.",
        buttons=lst,
    )


@callback(re.compile(b"wrns_(.*)"), owner=True)
async def set_wrns(event):
    value = int(event.data_match.group(1).decode("UTF-8"))
    if dn := udB.set_key("PMWARNS", value):
        await event.edit(
            f"Peringatan PM Setel ke {value}.\nPengguna baru akan memiliki peluang {value} di PM sebelum dilarang.",
            buttons=get_back_button("cbs_pmcstm"),
        )
    else:
        await event.edit(
            f"Ada yang tidak beres, harap periksa log {HNDLR}Anda!",
            buttons=get_back_button("cbs_pmcstm"),
        )


@callback("pmmed", owner=True)
async def media(event):
    await event.delete()
    pru = event.sender_id
    var = "PMPIC"
    name = "PM Media"
    async with event.client.conversation(pru) as conv:
        await conv.send_message(
            "**PM Media**\Kirimkan saya gambar/gif/stiker/tautan untuk ditetapkan sebagai median izin pm\nGunakan /cancel untuk menghentikan operasi.",
        )
        response = await conv.get_response()
        try:
            themssg = response.message
            if themssg == "/cancel":
                return await conv.send_message(
                    "Operasi dibatalkan!!",
                    buttons=get_back_button("cbs_pmcstm"),
                )
        except BaseException as er:
            LOGS.exception(er)
        media = await event.client.download_media(response, "pmpc")
        if (
            not (response.text).startswith("/")
            and response.text != ""
            and (not response.media or isinstance(response.media, MessageMediaWebPage))
        ):
            url = text_to_url(response)
        elif response.sticker:
            url = response.file.id
        else:
            try:
                x = upl(media)
                url = f"https://graph.org/{x[0]}"
                remove(media)
            except BaseException as er:
                LOGS.exception(er)
                return await conv.send_message(
                    "Dihentikan.",
                    buttons=get_back_button("cbs_pmcstm"),
                )
        await setit(event, var, url)
        await conv.send_message(
            f"{name} telah di atur.",
            buttons=get_back_button("cbs_pmcstm"),
        )


@callback("delpmmed", owner=True)
async def dell(event):
    try:
        udB.del_key("PMPIC")
        return await event.edit(
            get_string("clst_5"), buttons=get_back_button("cbs_pmcstm")
        )
    except BaseException as er:
        LOGS.exception(er)
        return await event.edit(
            get_string("clst_4"),
            buttons=[[Button.inline("« Pengaturan", data="setter")]],
        )


@callback("apon", owner=True)
async def apon(event):
    var = "AUTOAPPROVE"
    await setit(event, var, "True")
    await event.edit(
        "Selesai!! AUTOAPPROVE Dimulai!!",
        buttons=[[Button.inline("« Kembali", data="cbs_apauto")]],
    )


@callback("apof", owner=True)
async def apof(event):
    try:
        udB.set_key("AUTOAPPROVE", "False")
        return await event.edit(
            "Selesai! AUTOAPPROVE Berhenti!!",
            buttons=[[Button.inline("« Kembali", data="cbs_apauto")]],
        )
    except BaseException as er:
        LOGS.exception(er)
        return await event.edit(
            get_string("clst_4"),
            buttons=[[Button.inline("« Pengaturan", data="setter")]],
        )


@callback("pml", owner=True)
async def l_vcs(event):
    BT = (
        [Button.inline("PMLOGGER MATI", data="pmlogof")]
        if udB.get_key("PMLOG")
        else [Button.inline("PMLOGGER ON1", data="pmlog")]
    )

    await event.edit(
        "PMLOGGER Ini Akan Meneruskan Pm Anda ke Grup Pribadi Anda ",
        buttons=[
            BT,
            [Button.inline("Grup PMLOGGER", "abs_pmlgg")],
            [Button.inline("« Kembali", data="cbs_pmcstm")],
        ],
    )


@callback("pmlog", owner=True)
async def pmlog(event):
    await setit(event, "PMLOG", "True")
    await event.edit(
        "Selesai!! PMLOGGER Dimulai!!",
        buttons=[[Button.inline("« Kembali", data="pml")]],
    )


@callback("pmlogof", owner=True)
async def pmlogof(event):
    try:
        udB.del_key("PMLOG")
        return await event.edit(
            "Selesai! PMLOGGER Berhenti!!",
            buttons=[[Button.inline("« Kembali", data="pml")]],
        )
    except BaseException as er:
        LOGS.exception(er)
        return await event.edit(
            get_string("clst_4"),
            buttons=[[Button.inline("« Pengaturan", data="setter")]],
        )


@callback("pmon", owner=True)
async def pmonn(event):
    var = "PMSETTING"
    await setit(event, var, "True")
    await event.edit(
        "Selesai! PMPermit telah diaktifkan!!",
        buttons=[[Button.inline("« Kembali", data="cbs_ppmset")]],
    )


@callback("pmoff", owner=True)
async def pmofff(event):
    var = "PMSETTING"
    await setit(event, var, "False")
    await event.edit(
        "Selesai! PMPermit telah dimatikan!!",
        buttons=[[Button.inline("« Kembali", data="cbs_ppmset")]],
    )


@callback("botmew", owner=True)
async def hhh(e):
    async with e.client.conversation(e.chat_id) as conv:
        await conv.send_message("Kirim Media Apa Saja agar tetap diterima oleh Bot Anda ")
        msg = await conv.get_response()
        if not msg.media or msg.text.startswith("/"):
            return await conv.send_message(
                "Dihentikan!", buttons=get_back_button("cbs_chatbot")
            )
        udB.set_key("STARTMEDIA", msg.file.id)
        await conv.send_message("Done!", buttons=get_back_button("cbs_chatbot"))


@callback("botinfe", owner=True)
async def hhh(e):
    async with e.client.conversation(e.chat_id) as conv:
        await conv.send_message(
            "Kirim pesan untuk disetel ke Tampilan, saat pengguna Tekan tombol Info di Bot Selamat datang!\n\nskirim `Salah` untuk menghapus tombol itu sepenuhnya.."
        )
        msg = await conv.get_response()
        if msg.media or msg.text.startswith("/"):
            return await conv.send_message(
                "Dihentikan!", buttons=get_back_button("cbs_chatbot")
            )
        udB.set_key("BOT_INFO_START", msg.text)
        await conv.send_message("Done!", buttons=get_back_button("cbs_chatbot"))


@callback("pmfs", owner=True)
async def heheh(event):
    Ll = []
    err = ""
    async with event.client.conversation(event.chat_id) as conv:
        await conv.send_message(
            "❀ Kirim Id Obrolan, yang Anda ingin agar pengguna bergabung Sebelum menggunakan Bot Obrolan/Pm\n\n❀ Kirim /hapus untuk menonaktifkan PmBot Paksa sub..\n❀ ❀ Kirim /cancel untuk menghentikan proses ini..❀"
        )
        await conv.send_message(
            "Contoh : \n`-1001234567\n-100778888`\n\nUntuk Beberapa Obrolan."
        )
        try:
            msg = await conv.get_response()
        except AsyncTimeOut:
            return await conv.send_message("**• Waktu habis!**\nMulai dari /mulai Kembali.")
        if not msg.text or msg.text.startswith("/"):
            timyork = "Dibatalkan!"
            if msg.text == "/clear":
                udB.del_key("PMBOT_FSUB")
                timyork = "Selesai! Paksa Berlangganan Dihentikan\nMulai Ulang Bot Anda!"
            return await conv.send_message(
                "Dibatalkan!", buttons=get_back_button("cbs_chatbot")
            )
        for chat in msg.message.split("\n"):
            if chat.startswith("-") or chat.isdigit():
                chat = int(chat)
            try:
                CHSJSHS = await event.client.get_entity(chat)
                Ll.append(get_peer_id(CHSJSHS))
            except Exception as er:
                err += f"**{chat}** : {er}\n"
        if err:
            return await conv.send_message(err)
        udB.set_key("PMBOT_FSUB", str(Ll))
        await conv.send_message(
            "Selesai!\nMulai Ulang Bot Anda.", buttons=get_back_button("cbs_chatbot")
        )


@callback("bwel", owner=True)
async def name(event):
    await event.delete()
    pru = event.sender_id
    var = "STARTMSG"
    name = "Pesan Selamat Datang Bot:"
    async with event.client.conversation(pru) as conv:
        await conv.send_message(
            "**BOT WELCOME MESSAGE**\nMasukkan pesan yang ingin Anda tampilkan ketika seseorang memulai asisten Anda Bot.\nAnda Dapat menggunakan Parameter `{me}` , `{mention}` Untuk\nGunakan /cancel untuk menghentikan operasi.",
        )
        response = conv.wait_event(events.NewMessage(chats=pru))
        response = await response
        themssg = response.message.message
        if themssg == "/cancel":
            return await conv.send_message(
                "Dibatalkan!!",
                buttons=get_back_button("cbs_chatbot"),
            )
        await setit(event, var, themssg)
        await conv.send_message(
            f"{name} berubah menjadi {themssg}",
            buttons=get_back_button("cbs_chatbot"),
        )


@callback("onchbot", owner=True)
async def chon(event):
    var = "PMBOT"
    await setit(event, var, "True")
    Loader(path="assistant/pmbot.py", key="PM Bot").load_single()
    if AST_PLUGINS.get("pmbot"):
        for i, e in AST_PLUGINS["pmbot"]:
            event.client.remove_event_handler(i)
        for i, e in AST_PLUGINS["pmbot"]:
            event.client.add_event_handler(i, events.NewMessage(**e))
    await event.edit(
        "Selesai! Sekarang Anda Dapat Mengobrol Dengan Orang Melalui Bot Ini",
        buttons=[Button.inline("« Kembali", data="cbs_chatbot")],
    )


@callback("ofchbot", owner=True)
async def chon(event):
    var = "PMBOT"
    await setit(event, var, "False")
    if AST_PLUGINS.get("pmbot"):
        for i, e in AST_PLUGINS["pmbot"]:
            event.client.remove_event_handler(i)
    await event.edit(
        "Selesai! Mengobrol Orang Melalui Bot Ini Berhenti.",
        buttons=[Button.inline("« Kembali", data="cbs_chatbot")],
    )


@callback("inli_pic", owner=True)
async def media(event):
    await event.delete()
    pru = event.sender_id
    var = "INLINE_PIC"
    name = "Inline Media"
    async with event.client.conversation(pru) as conv:
        await conv.send_message(
            "**Inline Media**\Kirimi saya gambar/gif/ atau tautan untuk ditetapkan sebagai media.\n\nGunakan /cancel untuk menghentikan operasi.",
        )
        response = await conv.get_response()
        try:
            themssg = response.message
            if themssg == "/cancel":
                return await conv.send_message(
                    "Operasi dibatalkan!!",
                    buttons=get_back_button("setter"),
                )
        except BaseException as er:
            LOGS.exception(er)
        media = await event.client.download_media(response, "inlpic")
        if (
            not (response.text).startswith("/")
            and response.text != ""
            and (not response.media or isinstance(response.media, MessageMediaWebPage))
        ):
            url = text_to_url(response)
        else:
            try:
                x = upl(media)
                url = f"https://graph.org/{x[0]}"
                remove(media)
            except BaseException as er:
                LOGS.exception(er)
                return await conv.send_message(
                    "Dihentikan.",
                    buttons=get_back_button("setter"),
                )
        await setit(event, var, url)
        await conv.send_message(
            f"{name} has been set.",
            buttons=get_back_button("setter"),
        )


FD_MEDIA = {}


@callback(re.compile("fd(.*)"), owner=True)
async def fdroid_dler(event):
    uri = event.data_match.group(1).decode("utf-8")
    if FD_MEDIA.get(uri):
        return await event.edit(file=FD_MEDIA[uri])
    await event.answer("❀ Mulai mengunduh ❀", alert=True)
    await event.edit("❀ Mengunduh.. ❀")
    URL = f"https://f-droid.org/packages/{uri}"
    conte = await async_searcher(URL, re_content=True)
    BSC = bs(conte, "html.parser", from_encoding="utf-8")
    dl_ = BSC.find("p", "package-version-download").find("a")["href"]
    title = BSC.find("h3", "package-name").text.strip()
    thumb = BSC.find("img", "package-icon")["src"]
    if thumb.startswith("/"):
        thumb = f"https://f-droid.org{thumb}"
    thumb, _ = await fast_download(thumb, filename=f"{uri}.png")
    s_time = time.time()
    file, _ = await fast_download(
        dl_,
        filename=f"{title}.apk",
        progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
            progress(
                d,
                t,
                event,
                s_time,
                "Downloading...",
            )
        ),
    )

    time.time()
    n_file = await event.client.fast_uploader(
        file, show_progress=True, event=event, message="Uploading...", to_delete=True
    )
    buttons = Button.switch_inline("Mencari Kembali", query="fdroid", same_peer=True)
    try:
        msg = await event.edit(
            f"**❀ [{title}]({URL}) ❀**", file=n_file, thumb=thumb, buttons=buttons
        )
    except Exception as er:
        LOGS.exception(er)
        try:
            msg = await event.client.edit_message(
                await event.get_input_chat(),
                event.message_id,
                f"**❀ [{title}]({URL}) ❀**",
                buttons=buttons,
                thumb=thumb,
                file=n_file,
            )
        except Exception as er:
            os.remove(thumb)
            LOGS.exception(er)
            return await event.edit(f"**ERROR**: `{er}`", buttons=buttons)
    if msg and hasattr(msg, "media"):
        FD_MEDIA.update({uri: msg.media})
    os.remove(thumb)
