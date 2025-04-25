from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, ListView, ListItem, Input
from textual.containers import Vertical
from textual.reactive import reactive
from textual import events
from textual.screen import Screen, ModalScreen
from rich.text import Text
from logic.logging_config import configure_logging
from logic.update_check import check_for_update
from logic.convert import convert_avif_to_png
from cli.globals import cli_args, STATUS_COLORS
from cli.options_io import save_options
import logging
import threading
import traceback

CANCELED_MSG = "Canceled."

def quant_bits_display_dynamic(val, label):
    if val == 0:
        return f"Quantization bits ({label}): off (full color)"
    else:
        return f"Quantization bits ({label}): {val} ({2**val} levels)"

def get_edit_menu_options(args):
    return [
        ("Input directory", "input_dir"),
        ("Output directory", "output_dir"),
        ("Remove originals?", "remove"),
        ("Recursive search?", "recursive"),
        ("Silent mode?", "silent"),
        (quant_bits_display_dynamic(args.get("qb_color", 0), "color"), "qb_color"),
        (quant_bits_display_dynamic(args.get("qb_gray_color", 0), "grayscale+one"), "qb_gray_color"),
        (quant_bits_display_dynamic(args.get("qb_gray", 0), "grayscale"), "qb_gray"),
        ("Quantization method", "method"),
        ("Dither", "dither"),
        ("Back to main menu", "back"),
    ]

MENU_OPTIONS = [
    ("Start Interactive Conversion", "start"),
    ("Edit Options", "edit"),
    ("Check for Updates", "update"),
    ("Quit", "quit"),
]

# Helper to map arg name to menu display name
MENU_ARG_TO_DISPLAY = {arg: display for display, arg in get_edit_menu_options(cli_args)}

OPTION_VALIDATORS = {
    "output_dir": lambda v: v.strip() or None,
    "remove": lambda v: v.lower() == 'y' if isinstance(v, str) else bool(v),
    "recursive": lambda v: v.lower() == 'y' if isinstance(v, str) else bool(v),
    "silent": lambda v: v.lower() == 'y' if isinstance(v, str) else bool(v),
    "qb_color": lambda v: int(v) if v else None,
    "qb_gray_color": lambda v: int(v) if v else None,
    "qb_gray": lambda v: int(v) if v else None,
    "method": lambda v: int(v),
    "dither": lambda v: int(v),
}

def get_validated_input(prompt, default, validator):
    while True:
        val = input(prompt + " [" + str(default) + "]: ")
        if not val:
            return default
        if validator(val):
            return val
        print("Invalid input. Please try again.")


class StatusFooter(Footer):
    status: reactive[str] = reactive("")
    status_type: reactive[str] = reactive("INFO")

    def set_status(self, msg: str, status_type: str = "INFO"):
        self.status = msg
        self.status_type = status_type
        self.refresh()

    def render(self):
        color = STATUS_COLORS.get(self.status_type, "yellow")
        msg = self.status or ""
        if msg:
            return Text(msg, style=f"bold {color}")
        return super().render()


class MainMenuApp(App):
    TITLE = "A2P_Cli - AVIF to PNG Converter"
    CSS_PATH = None
    status: reactive[str] = reactive("")
    edit_status: reactive[str] = reactive("")
    progress: reactive[int] = reactive(0)
    progress_total: reactive[int] = reactive(1)

    def compose(self) -> ComposeResult:
        yield Header()
        yield Vertical(
            ListView(
                *[ListItem(Static(label), id=action) for label, action in MENU_OPTIONS],
                id="menu_list"
            ),
        )
        yield StatusFooter()

    async def on_mount(self) -> None:
        self.query_one("#menu_list").focus()
        self.update_status("")

    def update_status(self, msg: str, status_type: str = "INFO"):
        # Update the status message with the given status type.
        # Usage: self.update_status("Conversion finished!", "SUCCESS")
        # For errors: self.update_status("'input_dir' is required...", "ERROR")
        # For info: self.update_status("Options saved!", "INFO")
        try:
            footer = self.query(StatusFooter).first()
            if footer:
                footer.set_status(msg, status_type)
        except Exception:
            pass

    async def on_list_view_selected(self, event: ListView.Selected) -> None:
        action = event.item.id
        if action == "start":
            if not cli_args['input_dir'] or not str(cli_args['input_dir']).strip():
                self.update_status(f"{MENU_ARG_TO_DISPLAY['input_dir']} is required. Please set it in 'Edit Options' before starting conversion.", "ERROR")
                return
            self.progress = 0
            self.progress_total = 1
            def progress_callback(current, total):
                percent = int(100 * current / total) if total else 100
                self.call_from_thread(self.update_status, f"Conversion: {current}/{total} ({percent}%)", "INFO")
                self.progress = current
                self.progress_total = total
            def run_conversion():
                try:
                    filtered_kwargs = {k: v for k, v in cli_args.items() if k not in ['input_dir', 'output_dir', 'remove', 'recursive', 'silent', 'qb_color', 'qb_gray_color', 'qb_gray', 'log_level']}
                    convert_avif_to_png(
                        cli_args['input_dir'],
                        cli_args['output_dir'],
                        remove=cli_args['remove'],
                        recursive=cli_args['recursive'],
                        silent=cli_args['silent'],
                        qb_color=cli_args['qb_color'],
                        qb_gray_color=cli_args['qb_gray_color'],
                        qb_gray=cli_args['qb_gray'],
                        progress_callback=progress_callback,
                        progress_printer=None,
                        **filtered_kwargs
                    )
                    self.call_from_thread(self.update_status, "Conversion finished!", "SUCCESS")
                except Exception as e:
                    logging.error(f"Exception in run_conversion: {e}\n{traceback.format_exc()}")
                    self.call_from_thread(self.update_status, f"Exception during conversion: {e}", "ERROR")
            threading.Thread(target=run_conversion, daemon=True).start()
        elif action == "edit":
            await self.push_screen(EditOptionsScreen())
        elif action == "update":
            check_for_update()
            self.update_status("Checked for updates.", "INFO")
        elif action == "quit":
            await self.action_quit()

    async def on_key(self, event: events.Key) -> None:
        if event.key == "q":
            await self.action_quit()
        elif event.key in ("ctrl+q", "^Q", "^q") or (hasattr(event, "ctrl") and event.ctrl and event.key.lower() == "q"):
            self.exit()

    async def action_quit(self):
        self.exit()


class EditOptionsScreen(Screen):
    status: reactive[str] = reactive("")

    async def on_list_view_selected(self, event: ListView.Selected) -> None:
        action = event.item.id
        handler = self.ACTION_HANDLERS.get(action)
        if handler:
            await handler(self)

    async def handle_input_dir(self):
        def set_input_dir(val):
            if val is not None and val.strip():
                cli_args['input_dir'] = val.strip()
                self.update_status(f"{MENU_ARG_TO_DISPLAY['input_dir']} set to: {cli_args['input_dir']}", "INFO")
            elif val is not None:
                self.update_status("Invalid input. Please try again.", "ERROR")
        await self.app.push_screen(InputDialog("Enter input directory:", cli_args['input_dir'], callback=set_input_dir))

    async def handle_output_dir(self):
        def set_output_dir(val):
            prev = cli_args.get('output_dir') or ''
            new_val = val.strip() if val and val.strip() else None
            if new_val != prev:
                cli_args['output_dir'] = new_val
                self.update_status(f"{MENU_ARG_TO_DISPLAY['output_dir']} set to: {cli_args['output_dir']}", "INFO")
            else:
                self.update_status("", "INFO")
        await self.app.push_screen(InputDialog("Enter output directory (blank for same as input):", cli_args['output_dir'] or "", callback=set_output_dir))

    async def handle_qb_color(self):
        def set_qb_color(val):
            prev = cli_args.get('qb_color')
            if val is None:
                self.update_status(CANCELED_MSG, "INFO")
            else:
                new_val = int(val) if val.strip() else 0
                if new_val != prev:
                    cli_args['qb_color'] = new_val
                    self.update_status(quant_bits_display_dynamic(new_val, "color"), "INFO")
                else:
                    self.update_status("", "INFO")
        await self.app.push_screen(InputDialog("Quantization bits for color images (1-8, blank/off for full color):", str(cli_args['qb_color']) if cli_args['qb_color'] else "", callback=set_qb_color))

    async def handle_qb_gray_color(self):
        def set_qb_gray_color(val):
            prev = cli_args.get('qb_gray_color')
            if val is None:
                self.update_status(CANCELED_MSG, "INFO")
            else:
                new_val = int(val) if val.strip() else 0
                if new_val != prev:
                    cli_args['qb_gray_color'] = new_val
                    self.update_status(quant_bits_display_dynamic(new_val, "grayscale+one"), "INFO")
                else:
                    self.update_status("", "INFO")
        await self.app.push_screen(InputDialog("Quantization bits for grayscale+one images (1-8, blank/off for full color):", str(cli_args['qb_gray_color']) if cli_args['qb_gray_color'] else "", callback=set_qb_gray_color))

    async def handle_qb_gray(self):
        def set_qb_gray(val):
            prev = cli_args.get('qb_gray')
            if val is None:
                self.update_status(CANCELED_MSG, "INFO")
            else:
                new_val = int(val) if val.strip() else 0
                if new_val != prev:
                    cli_args['qb_gray'] = new_val
                    self.update_status(quant_bits_display_dynamic(new_val, "grayscale"), "INFO")
                else:
                    self.update_status("", "INFO")
        await self.app.push_screen(InputDialog("Quantization bits for grayscale images (1-8, blank/off for full color):", str(cli_args['qb_gray']) if cli_args['qb_gray'] else "", callback=set_qb_gray))

    async def handle_method(self):
        def set_method(val):
            prev = cli_args.get('method')
            if val is None:
                self.update_status(CANCELED_MSG, "INFO")
            else:
                new_val = int(val)
                if new_val != prev:
                    cli_args['method'] = new_val
                    self.update_status(f"{MENU_ARG_TO_DISPLAY['method']} set to: {cli_args['method']}", "INFO")
                else:
                    self.update_status("", "INFO")
        await self.app.push_screen(InputDialog("Quantization method (0=Median Cut, 1=Max Coverage, 2=Fast Octree):", str(cli_args['method']), callback=set_method))

    async def handle_dither(self):
        def set_dither(val):
            prev = cli_args.get('dither')
            if val is None:
                self.update_status(CANCELED_MSG, "INFO")
            else:
                new_val = int(val)
                if new_val != prev:
                    cli_args['dither'] = new_val
                    self.update_status(f"{MENU_ARG_TO_DISPLAY['dither']} set to: {cli_args['dither']}", "INFO")
                else:
                    self.update_status("", "INFO")
        await self.app.push_screen(InputDialog("Dither (0=None, 1=Floyd-Steinberg):", str(cli_args['dither']), callback=set_dither))

    async def handle_remove(self):
        def set_remove(val):
            prev = cli_args.get('remove')
            if val != prev:
                cli_args['remove'] = val
                self.update_status(f"{MENU_ARG_TO_DISPLAY['remove']} set to: {cli_args['remove']}", "INFO")
            else:
                self.update_status("", "INFO")
        await self.app.push_screen(YesNoDialog("Remove originals?", cli_args['remove'], callback=set_remove))

    async def handle_recursive(self):
        def set_recursive(val):
            prev = cli_args.get('recursive')
            if val != prev:
                cli_args['recursive'] = val
                self.update_status(f"{MENU_ARG_TO_DISPLAY['recursive']} set to: {cli_args['recursive']}", "INFO")
            else:
                self.update_status("", "INFO")
        await self.app.push_screen(YesNoDialog("Recursive search?", cli_args['recursive'], callback=set_recursive))

    async def handle_silent(self):
        def set_silent(val):
            prev = cli_args.get('silent')
            if val != prev:
                cli_args['silent'] = val
                self.update_status(f"{MENU_ARG_TO_DISPLAY['silent']} set to: {cli_args['silent']}", "INFO")
            else:
                self.update_status("", "INFO")
        await self.app.push_screen(YesNoDialog("Silent mode?", cli_args['silent'], callback=set_silent))

    async def handle_back(self):
        save_options("TUI", {k: v for k, v in cli_args.items() if k not in ("input_dir", "output_dir", "log", "version", "check_update")})
        await self.app.pop_screen()
        # Show status in main menu after returning
        main_app = self.app if hasattr(self, 'app') else None
        if main_app and hasattr(main_app, 'update_status'):
            main_app.update_status("Options saved!", "SUCCESS")

    ACTION_HANDLERS = {
        "input_dir": lambda self: self.handle_input_dir(),
        "output_dir": lambda self: self.handle_output_dir(),
        "qb_color": lambda self: self.handle_qb_color(),
        "qb_gray_color": lambda self: self.handle_qb_gray_color(),
        "qb_gray": lambda self: self.handle_qb_gray(),
        "method": lambda self: self.handle_method(),
        "dither": lambda self: self.handle_dither(),
        "remove": lambda self: self.handle_remove(),
        "recursive": lambda self: self.handle_recursive(),
        "silent": lambda self: self.handle_silent(),
        "back": lambda self: self.handle_back(),
    }

    def compose(self) -> ComposeResult:
        yield Header()
        yield Vertical(
            Static("Edit Options", classes="title"),
            ListView(id="edit_menu_list"),
        )
        yield StatusFooter()

    def refresh_options_list(self):
        def get_option_value(option_key):
            val = cli_args.get(option_key)
            if option_key in ("remove", "recursive", "silent"):
                return "Yes" if val else "No"
            elif option_key == "output_dir":
                # Show empty string if both output_dir and input_dir are blank/None
                if not val:
                    input_dir_val = cli_args.get("input_dir", "")
                    if not input_dir_val:
                        return ""
                    return input_dir_val
                return str(val)
            elif val is None:
                return "(default)"
            return str(val)
        options = []
        for label, action in get_edit_menu_options(cli_args):
            if 'Quantization bits' in label:
                display_label = label
                MENU_ARG_TO_DISPLAY[action] = label
            elif action == 'back':
                display_label = label
            else:
                display_label = f"{label} [{get_option_value(action)}]"
            options.append(ListItem(Static(display_label, classes="option-item"), id=action))
        list_view = self.query_one("#edit_menu_list", ListView)
        list_view.clear()
        list_view.extend(options)

    def update_status(self, msg: str, status_type: str = "INFO"):
        # Update the status message with the given status type.
        # Usage: self.update_status("Options saved!", "SUCCESS")
        # For errors: self.update_status("Invalid input...", "ERROR")
        # For info: self.update_status("Options saved!", "INFO")
        try:
            footer = self.query(StatusFooter).first()
            if footer:
                footer.set_status(msg, status_type)
        except Exception:
            pass
        self.refresh_options_list()
        self.refresh()

    async def on_mount(self) -> None:
        self.query_one("#edit_menu_list").focus()
        self.update_status("")
        self.refresh_options_list()

    async def on_key(self, event: events.Key) -> None:
        if event.key == "backspace":
            self.app.pop_screen()
        elif event.key in ("ctrl+q", "^Q", "^q") or (hasattr(event, "ctrl") and event.ctrl and event.key.lower() == "q"):
            self.app.exit()


class InputDialog(ModalScreen):
    def __init__(self, title: str, initial: str = "", callback=None):
        super().__init__()
        self.title = title
        self.initial = initial
        self.callback = callback

    def compose(self) -> ComposeResult:
        yield Static(self.title, classes="title")
        yield Static(f"Current value: {self.initial if self.initial else '(default)'}", classes="current-value")
        input_widget = Input(value=self.initial, placeholder=self.title, id="input_dialog_input")
        yield input_widget
        yield Static("[Enter] to confirm, [Esc] to cancel", classes="help")

    async def on_mount(self) -> None:
        input_widget = self.query_one("#input_dialog_input", Input)
        input_widget.focus()

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        if self.callback:
            self.callback(event.value)
        self.dismiss()

    async def on_key(self, event: events.Key) -> None:
        if event.key == "escape":
            if self.callback:
                self.callback(None)
            self.dismiss()


class YesNoDialog(ModalScreen):
    def __init__(self, title: str, initial: bool = False, callback=None):
        super().__init__()
        self.title = title
        self.initial = initial
        self.value = initial
        self.callback = callback

    def compose(self) -> ComposeResult:
        yield Static(self.title, classes="title")
        yield Static(f"Current value: {'Yes' if self.initial else 'No'}", classes="current-value")
        yield ListView(
            ListItem(Static("Yes"), id="yes"),
            ListItem(Static("No"), id="no"),
            id="yesno_menu"
        )
        yield Static("[Enter] to select, [Esc] to cancel", classes="help")

    async def on_mount(self) -> None:
        self.query_one("#yesno_menu").index = 0 if self.initial else 1
        self.query_one("#yesno_menu").focus()

    async def on_list_view_selected(self, event: ListView.Selected) -> None:
        if event.item.id == "yes":
            self.value = True
            if self.callback:
                self.callback(self.value)
            self.dismiss()
        elif event.item.id == "no":
            self.value = False
            if self.callback:
                self.callback(self.value)
            self.dismiss()

    async def on_key(self, event: events.Key) -> None:
        if event.key == "escape":
            if self.callback:
                self.callback(None)
            self.dismiss()


def run():
    from logic.logging_config import configure_logging
    from cli.globals import cli_args
    configure_logging(level=cli_args.get('log_level', 0), log_file='a2pcli.log')
    MainMenuApp().run()
