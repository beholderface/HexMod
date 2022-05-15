from sys import argv, stdout
from collections import namedtuple
import json # codec
import re # parsing
import os # listdir

# TO USE: put in Hexcasting root dir, collate_data.py src/main/resources hexcasting thehexbook out.html

# extra info :(
lang = "en_us"
repo_names = {
    "hexcasting": "https://raw.githubusercontent.com/gamma-delta/HexMod/main/src/main/resources",
}
extra_i18n = {
    "item.minecraft.amethyst_shard": "Amethyst Shard",
    "block.hexcasting.slate": "Blank Slate",
}

default_macros = {
    "$(obf)": "$(k)",
    "$(bold)": "$(l)",
    "$(strike)": "$(m)",
    "$(italic)": "$(o)",
    "$(italics)": "$(o)",
    "$(list": "$(li",
    "$(reset)": "$()",
    "$(clear)": "$()",
    "$(2br)": "$(br2)",
    "$(p)": "$(br2)",
    "/$": "$()",
    "<br>": "$(br)",
    "$(nocolor)": "$(0)",
    "$(item)": "$(#b0b)",
    "$(thing)": "$(#490)",
}

colors = {
    "0": None,
    "1": "00a",
    "2": "0a0",
    "3": "0aa",
    "4": "a00",
    "5": "a0a",
    "6": "fa0",
    "7": "aaa",
    "8": "555",
    "9": "55f",
    "a": "5f5",
    "b": "5ff",
    "c": "f55",
    "d": "f5f",
    "e": "ff5",
    "f": "fff",
}
types = {
    "k": "obf",
    "l": "italic",
    "m": "strikethrough",
    "n": "underline",
    "o": "italic",
}

keys = {
    "use": "Right Click",
    "sneak": "Left Shift",
}

bind1 = (lambda: None).__get__(0).__class__

def slurp(filename):
    with open(filename, "r") as fh:
        return json.load(fh)

FormatTree = namedtuple("FormatTree", ["style", "children"])
Style = namedtuple("Style", ["type", "value"])

def parse_style(sty):
    if sty == "br":
        return "<br />", None
    if sty == "br2":
        return "", Style("para", {})
    if sty == "li":
        return "", Style("para", {"clazz": "fake-li"})
    if sty[:2] == "k:":
        return keys[sty[2:]], None
    if sty[:2] == "l:":
        return "", Style("link", sty[2:])
    if sty == "/l":
        return "", Style("link", None)
    if sty == "playername":
        return "[Playername]", None
    if sty[:2] == "t:":
        return "", Style("tooltip", sty[2:])
    if sty == "/t":
        return "", Style("tooltip", None)
    if sty[:2] == "c:":
        return "", Style("cmd_click", sty[2:])
    if sty == "/c":
        return "", Style("cmd_click", None)
    if sty == "r" or not sty:
        return "", Style("base", None)
    if sty in types:
        return "", Style(types[sty], True)
    if sty in colors:   
        return "", Style("color", colors[sty])
    if sty.startswith("#") and len(sty) in [4, 7]:
        return "", Style("color", sty[1:])
    # TODO more style parse
    raise ValueError("Unknown style: " + sty)

def localize(i18n, string):
    return i18n.get(string, string) if i18n else string

format_re = re.compile(r"\$\(([^)]*)\)")
def format_string(root_data, string):
    # resolve lang
    string = localize(root_data["i18n"], string)
    # resolve macros
    old_string = None
    while old_string != string:
        old_string = string
        for macro, replace in root_data["macros"].items():
            string = string.replace(macro, replace)
        else: break

    # lex out parsed styles
    text_nodes = []
    styles = []
    last_end = 0
    extra_text = ""
    for mobj in re.finditer(format_re, string):
        bonus_text, sty = parse_style(mobj.group(1))
        text = string[last_end:mobj.start()] + bonus_text
        if sty:
            styles.append(sty)
            text_nodes.append(extra_text + text)
            extra_text = ""
        else:
            extra_text += text
        last_end = mobj.end()
    text_nodes.append(extra_text + string[last_end:])
    first_node, *text_nodes = text_nodes

    # parse 
    style_stack = [FormatTree(Style("base", True), []), FormatTree(Style("para", {}), [first_node])]
    for style, text in zip(styles, text_nodes):
        tmp_stylestack = []
        if style.type == "base":
            while style_stack[-1].style.type != "para":
                last_node = style_stack.pop()
                style_stack[-1].children.append(last_node)
        elif any(tree.style.type == style.type for tree in style_stack):
            while len(style_stack) >= 2:
                last_node = style_stack.pop()
                style_stack[-1].children.append(last_node)
                if last_node.style.type == style.type:
                    break
                tmp_stylestack.append(last_node.style)
        for sty in tmp_stylestack:
            style_stack.append(FormatTree(sty, []))
        if style.value is None:
            if text: style_stack[-1].children.append(text)
        else:
            style_stack.append(FormatTree(style, [text] if text else []))
    while len(style_stack) >= 2:
        last_node = style_stack.pop()
        style_stack[-1].children.append(last_node)

    return style_stack[0]

test_root = {"i18n": {}, "macros": default_macros, "resource_dir": "src/main/resources"}
test_str = "Write the given iota to my $(l:patterns/readwrite#hexcasting:write/local)$(#490)local$().$(br)The $(l:patterns/readwrite#hexcasting:write/local)$(#490)local$() is a lot like a $(l:items/focus)$(#b0b)Focus$(). It's cleared when I stop casting a Hex, starts with $(l:casting/influences)$(#490)Null$() in it, and is preserved between casts of $(l:patterns/meta#hexcasting:for_each)$(#fc77be)Thoth's Gambit$(). "

def do_localize(root_data, obj, *names):
    for name in names:
        if name in obj:
            obj[name] = localize(root_data["i18n"], obj[name])

def do_format(root_data, obj, *names):
    for name in names:
        if name in obj:
            obj[name] = format_string(root_data, obj[name])

def identity(x): return x

pattern_pat = re.compile(r'HexPattern\.FromAnglesSig\("([qweasd]+)", HexDir\.(\w+)\),\s*prefix\("([^"]+)"\)([^;]*true\);)?')
def fetch_patterns(root_data):
    filename = f"{root_data['resource_dir']}/../java/at/petrak/hexcasting/common/casting/RegisterPatterns.java"
    registry = {}
    with open(filename, "r") as fh:
        pattern_data = fh.read()
        for mobj in re.finditer(pattern_pat, pattern_data):
            string, start_angle, name, is_per_world = mobj.groups()
            registry[root_data["modid"] + ":" + name] = (string, start_angle, bool(is_per_world))
    return registry

def resolve_pattern(root_data, page):
    if "pattern_reg" not in root_data:
        root_data["pattern_reg"] = fetch_patterns(root_data)
    page["op"] = [root_data["pattern_reg"][page["op_id"]]]
    page["name"] = localize(root_data["i18n"], "hexcasting.spell." + page["op_id"])

def fixup_pattern(do_sig, root_data, page):
    patterns = page["patterns"]
    if not isinstance(patterns, list): patterns = [patterns]
    if do_sig:
        inp = page.get("input", None) or "nothing"
        oup = page.get("output", None) or "nothing"
        page["header"] += f" ({inp} \u2192 {oup})"
    page["op"] = [(p["signature"], p["startdir"], False) for p in patterns]

def fetch_recipe_result(root_data, recipe):
    modid, recipeid = recipe.split(":")
    gen_resource_dir = root_data["resource_dir"].replace("/main", "/generated") # TODO hack
    recipe_path = f"{gen_resource_dir}/data/{modid}/recipes/{recipeid}.json"
    recipe_data = slurp(recipe_path)
    return recipe_data["result"]["item"]

def localize_item(root_data, item):
    # TODO hack
    item = re.sub("{.*", "", item.replace(":", "."))
    block = "block." + item
    block_l = localize(root_data["i18n"], block)
    if block_l != block: return block_l
    return localize(root_data["i18n"], "item." + item)

page_types = {
    "hexcasting:pattern": resolve_pattern,
    "hexcasting:manual_pattern": bind1(fixup_pattern, True),
    "hexcasting:manual_pattern_nosig": bind1(fixup_pattern, False),
    "patchouli:link": lambda rd, page: do_localize(rd, page, "link_text"),
    "patchouli:crafting": lambda rd, page: page.__setitem__("item_name", localize_item(rd, fetch_recipe_result(rd, page["recipe"]))),
    "hexcasting:crafting_multi": lambda rd, page: page.__setitem__("item_name", [localize_item(rd, fetch_recipe_result(rd, recipe)) for recipe in page["recipes"]]),
    "patchouli:spotlight": lambda rd, page: page.__setitem__("item_name", localize(rd, page["item"]))
}

def walk_dir(root_dir, prefix):
    search_dir = root_dir + '/' + prefix
    for fh in os.scandir(search_dir):
        if fh.is_dir():
            yield from walk_dir(root_dir, prefix + fh.name + '/')
        elif fh.name.endswith(".json"):
            yield prefix + fh.name

def parse_entry(root_data, entry_path, ent_name):
    data = slurp(f"{entry_path}")
    do_localize(root_data, data, "name")
    for page in data["pages"]:
        do_localize(root_data, page, "header")
        do_format(root_data, page, "text")
        if page["type"] in page_types:
            page_types[page["type"]](root_data, page)
    data["id"] = ent_name

    return data

def parse_category(root_data, base_dir, cat_name):
    data = slurp(f"{base_dir}/categories/{cat_name}.json")
    do_localize(root_data, data, "name")
    do_format(root_data, data, "description")

    entry_dir = f"{base_dir}/entries/{cat_name}"
    entries = []
    for filename in os.listdir(entry_dir):
        if filename.endswith(".json"):
            basename = filename[:-5]
            entries.append(parse_entry(root_data, f"{entry_dir}/{filename}", cat_name + "/" + basename))
    entries.sort(key=lambda ent: (not ent.get("priority", False), ent.get("sortnum", 0), ent["name"]))
    data["entries"] = entries
    data["id"] = cat_name

    return data

def parse_sortnum(cats, name):
    if '/' in name:
        ix = name.rindex('/')
        return parse_sortnum(cats, name[:ix]) + (cats[name].get("sortnum", 0),)
    return cats[name].get("sortnum", 0),

def parse_book(root, mod_name, book_name):
    base_dir = f"{root}/data/{mod_name}/patchouli_books/{book_name}"
    root_info = slurp(f"{base_dir}/book.json")

    root_info["resource_dir"] = root
    root_info["modid"] = mod_name
    root_info.setdefault("macros", {}).update(default_macros)
    if root_info.setdefault("i18n", {}):
        root_info["i18n"] = slurp(f"{root}/assets/{mod_name}/lang/{lang}.json")
        root_info["i18n"].update(extra_i18n)

    book_dir = f"{base_dir}/{lang}"

    categories = []
    for filename in walk_dir(f"{book_dir}/categories", ""):
        basename = filename[:-5]
        categories.append(parse_category(root_info, book_dir, basename))
    cats = {cat["id"]: cat for cat in categories}
    categories.sort(key=lambda cat: (parse_sortnum(cats, cat["id"]), cat["name"]))

    do_localize(root_info, root_info, "name")
    do_format(root_info, root_info, "landing_text")
    root_info["categories"] = categories
    root_info["blacklist"] = set()

    return root_info

def tag_args(kwargs):
    return "".join(f" {'class' if key == 'clazz' else key.replace('_', '-')}={repr(value)}" for key, value in kwargs.items())

class PairTag:
    __slots__ = ["stream", "name", "kwargs"]
    def __init__(self, stream, name, **kwargs):
        self.stream = stream
        self.name = name
        self.kwargs = tag_args(kwargs)
    def __enter__(self):
        print(f"<{self.name}{self.kwargs}>", file=self.stream, end="")
    def __exit__(self, _1, _2, _3):
        print(f"</{self.name}>", file=self.stream, end="")

class Stream:
    __slots__ = ["stream", "thunks"]
    def __init__(self, stream):
        self.stream = stream
        self.thunks = []

    def tag(self, name, **kwargs):
        keywords = tag_args(kwargs)
        print(f"<{name}{keywords} />", file=self.stream, end="")
        return self

    def pair_tag(self, name, **kwargs):
        return PairTag(self.stream, name, **kwargs)

    def text(self, txt):
        print(txt, file=self.stream, end="")
        return self

def get_format(out, ty, value):
    if ty == "para":
        return out.pair_tag("p", **value)
    if ty == "color":
        return out.pair_tag("span", style=f"color: #{value}")
    if ty == "link":
        link = value
        if "://" not in link:
            link = "#" + link.replace("#", "@")
        return out.pair_tag("a", href=link)
    if ty == "tooltip":
        return out.pair_tag("span", clazz="has-tooltip", title=value)
    if ty == "cmd_click":
        return out.pair_tag("span", clazz="has-cmd_click", title="When clicked, would execute: "+value)
    if ty == "obf":
        return out.pair_tag("span", clazz="obfuscated")
    if ty == "bold":
        return out.pair_tag("strong")
    if ty == "italic":
        return out.pair_tag("i")
    if ty == "strikethrough":
        return out.pair_tag("s")
    if ty == "underline":
        return out.pair_tag("span", style="text-decoration: underline")
    raise ValueError("Unknown format type: " + ty)

def write_block(out, block):
    if isinstance(block, str):
        out.text(block)
        return
    sty_type = block.style.type
    if sty_type == "base":
        for child in block.children: write_block(out, child)
        return
    tag = get_format(out, sty_type, block.style.value)
    with tag:
        for child in block.children:
            write_block(out, child)

# TODO modularize
def write_page(out, pageid, page, anchor_id):
    if not anchor_id and "anchor" in page:
        aid = pageid + "@" + page["anchor"]
        with out.pair_tag("div", id=aid):
            write_page(out, pageid, page, aid)
            return

    if "header" in page:
        with out.pair_tag("h4"):
            out.text(page["header"])
            if anchor_id:
                with out.pair_tag("a", href="#" + anchor_id, clazz="permalink small"):
                    with out.pair_tag("i", clazz="bi bi-link-45deg"): pass

    ty = page["type"]
    if ty == "patchouli:text":
        write_block(out, page["text"])
    elif ty == "patchouli:empty": pass
    elif ty == "patchouli:link":
        write_block(out, page["text"])
        with out.pair_tag("p", clazz="linkout"):
            with out.pair_tag("a", href=page["url"]):
                out.text(page["link_text"])
    elif ty == "patchouli:spotlight":
        with out.pair_tag("h4", clazz="spotlight-title page-header"):
            out.text(page["item_name"])
        out.tag("hr", style="margin: 0")
        if "text" in page: write_block(out, page["text"])
    elif ty == "patchouli:crafting":
        with out.pair_tag("p", clazz="crafting-info"):
            out.text(f"[Depicted in the book: The crafting recipe for the")
            with out.pair_tag("code"): out.text(page["item_name"])
            out.text(".]")
        if "text" in page: write_block(out, page["text"])
    elif ty == "patchouli:image":
        with out.pair_tag("p", clazz="img-wrapper"):
            for img in page["images"]:
                modid, coords = img.split(":")
                with out.pair_tag("img", src=f"{repo_names[modid]}/assets/{modid}/{coords}"): pass
        if "text" in page: write_block(out, page["text"])
    elif ty == "hexcasting:crafting_multi":
        recipes = page["item_name"]
        with out.pair_tag("p", clazz="crafting-info"):
            out.text(f"[Depicted in the book: Several crafting recipes, for the")
            with out.pair_tag("code"): out.text(recipes[0])
            for i in recipes[1:]:
                out.text(", ")
                with out.pair_tag("code"): out.text(i)
            out.text(".]")
        if "text" in page: write_block(out, page["text"])
    elif ty == "hexcasting:brainsweep": 
        if "text" in page: write_block(out, page["text"])
    elif ty in ("hexcasting:pattern", "hexcasting:manual_pattern_nosig", "hexcasting:manual_pattern"):
        if "name" in page:
            with out.pair_tag("h4", clazz="pattern-title"):
                inp = page.get("input", None) or "nothing"
                oup = page.get("output", None) or "nothing"
                out.text(f"{page['name']} ({inp} \u2192 {oup})")
                if anchor_id:
                    with out.pair_tag("a", href="#" + anchor_id, clazz="permalink small"):
                        with out.pair_tag("i", clazz="bi bi-link-45deg"): pass
        with out.pair_tag("details", clazz="spell-collapsible"):
            with out.pair_tag("summary", clazz="collapse-spell"): pass
            for string, start_angle, per_world in page["op"]:
                with out.pair_tag("canvas", width=216, height=216, data_string=string, data_start=start_angle.lower(), data_per_world=per_world):
                    out.text("Your browser does not support visualizing patterns. Pattern code: " + string)
        write_block(out, page["text"])
    else:
        with out.pair_tag("p", clazz="todo-note"):
            out.text("TODO: Missing processor for type: " + ty)
        if "text" in page:
            write_block(out, page["text"])
    out.tag("br")

def write_entry(out, entry):
    with out.pair_tag("div", id=entry["id"]):
        with out.pair_tag("h3", clazz="entry-title page-header"):
            write_block(out, entry["name"])
            with out.pair_tag("a", href="#" + entry["id"], clazz="permalink small"):
                with out.pair_tag("i", clazz="bi bi-link-45deg"): pass
        for page in entry["pages"]:
            write_page(out, entry["id"], page, None)

def write_category(out, blacklist, category):
    with out.pair_tag("section", id=category["id"]):
        with out.pair_tag("h2", clazz="category-title page-header"):
            write_block(out, category["name"])
            with out.pair_tag("a", href="#" + category["id"], clazz="permalink small"):
                with out.pair_tag("i", clazz="bi bi-link-45deg"): pass
        write_block(out, category["description"])
        for entry in category["entries"]:
            if entry["id"] not in blacklist:
                write_entry(out, entry)

def write_toc(out, book):
    with out.pair_tag("h2", id="table-of-contents", clazz="page-header"):
        out.text("Table of Contents")
        with out.pair_tag("a", href="#0", clazz="toggle-link small", data_target="toc-category"):
            out.text("(toggle all)")
        with out.pair_tag("a", href="#table-of-contents", clazz="permalink small"):
            with out.pair_tag("i", clazz="bi bi-link-45deg"): pass
    for category in book["categories"]:
        with out.pair_tag("details", clazz="toc-category"):
            with out.pair_tag("summary"):
                with out.pair_tag("a", href="#" + category["id"]):
                    out.text(category["name"])
            with out.pair_tag("ul"):
                for entry in category["entries"]:
                    with out.pair_tag("li"):
                        with out.pair_tag("a", href="#" + entry["id"]):
                            out.text(entry["name"])

def write_book(out, book):
    with out.pair_tag("div", clazz="container"):
        with out.pair_tag("header", clazz="jumbotron"):
            with out.pair_tag("h1", clazz="book-title"):
                write_block(out, book["name"])
            write_block(out, book["landing_text"])
        with out.pair_tag("nav"):
            write_toc(out, book)
        with out.pair_tag("main", clazz="book-body"):
            for category in book["categories"]:
                write_category(out, book["blacklist"], category)

def main(argv):
    if len(argv) < 3:
        print(f"Usage: {argv[0]} <resources dir> <mod name> <book name> [<output>]")
        return
    root = argv[1]
    mod_name = argv[2]
    book_name = argv[3]
    book = parse_book(root, mod_name, book_name)
    with open("template.html", "r") as fh:
        with stdout if len(argv) < 5 else open(argv[4], "w") as out:
            for line in fh:
                if line.startswith("#DO_NOT_RENDER"):
                    _, *blacklist = line.split()
                    book["blacklist"].update(blacklist)
                elif line == "#DUMP_BODY_HERE\n":
                    write_book(Stream(out), book)
                    print('', file=out)
                else: print(line, end='', file=out)

if __name__ == "__main__":
    main(argv)
