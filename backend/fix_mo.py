"""Recompile .po to .mo with proper UTF-8 encoding and metadata-first ordering."""
import struct
import array


def parse_po(path):
    messages = {}
    msgid = None
    msgstr = None
    section = None
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("msgid "):
                if msgid is not None:
                    messages[msgid] = msgstr or ""
                msgid = line[6:].strip().strip('"')
                msgstr = None
                section = "id"
            elif line.startswith("msgstr "):
                msgstr = line[7:].strip().strip('"')
                section = "str"
            elif line.startswith('"') and section == "id":
                msgid += line.strip('"')
            elif line.startswith('"') and section == "str":
                msgstr = (msgstr or "") + line.strip('"')
    if msgid is not None:
        messages[msgid] = msgstr or ""
    return messages


def write_mo(path, messages):
    # Metadata entry must be FIRST in the file
    metadata = "Content-Type: text/plain; charset=UTF-8\n"

    # Build key list: metadata first, then sorted keys
    keys = [""] + sorted(k for k in messages.keys() if k != "")
    all_messages = {"": metadata}
    all_messages.update(messages)

    offsets = []
    ids = strs = b""
    for k in keys:
        id_bytes = k.encode("utf-8")
        str_bytes = all_messages[k].encode("utf-8")
        offsets.append((len(ids), len(id_bytes), len(strs), len(str_bytes)))
        ids += id_bytes + b"\x00"
        strs += str_bytes + b"\x00"
    n = len(keys)
    keystart = 7 * 4 + 16 * n
    valuestart = keystart + len(ids)
    koffsets = []
    voffsets = []
    for o1, l1, o2, l2 in offsets:
        koffsets += [l1, o1 + keystart]
        voffsets += [l2, o2 + valuestart]
    # Magic, version, nstrings, offset of orig table, offset of trans table, hash size, hash offset
    output = struct.pack("Iiiiiii", 0x950412DE, 0, n, 7 * 4, 7 * 4 + n * 8, 0, 0)
    output += array.array("i", koffsets).tobytes()
    output += array.array("i", voffsets).tobytes()
    output += ids + strs
    with open(path, "wb") as f:
        f.write(output)


if __name__ == "__main__":
    import sys

    po_path = sys.argv[1] if len(sys.argv) > 1 else "locale/kn/LC_MESSAGES/django.po"
    mo_path = sys.argv[2] if len(sys.argv) > 2 else "locale/kn/LC_MESSAGES/django.mo"
    messages = parse_po(po_path)
    write_mo(mo_path, messages)
    print(f"Compiled {len(messages)} messages to {mo_path}")
