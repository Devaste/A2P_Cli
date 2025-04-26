from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, ListView, ListItem, Input
from textual.containers import Vertical
from textual.reactive import reactive
from textual import events
from textual.screen import Screen, ModalScreen
from rich.text import Text
from logic.update_check import check_for_update
from logic.convert import convert_avif_to_png
from logic.logging_config import log_call
from cli.globals import options_dict
from cli.options_io import save_options, load_options
import threading
from pathlib import Path

STATUS_COLORS = {
    "INFO": "yellow",
    "SUCCESS": "green",
    "ERROR": "red",
}

CANCELED_MSG = "Canceled."
INVALID_QB_MSG = "Invalid: must be 1-8 or blank for full color."
NO_CHANGE_MSG = "No change."

@log_call
def quant_bits_display_dynamic(val, label):
    if val is None:
        return f"Quantization bits ({label}): off (full color)"
    else:
        return f"Quantization bits ({label}): {val} ({2**val} levels)"

@log_call
def get_edit_menu_options(args):
    return [
        ("Input directory", "input_dir"),
        ("Output directory", "output_dir"),
        ("Remove originals?", "remove"),
        ("Recursive search?", "recursive"),
        ("Silent mode?", "silent"),
        (quant_bits_display_dynamic(args.get("qb_color", None), "color"), "qb_color"),
        (quant_bits_display_dynamic(args.get("qb_gray_color", None), "grayscale+one"), "qb_gray_color"),
        (quant_bits_display_dynamic(args.get("qb_gray", None), "grayscale"), "qb_gray"),
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
menu_arg_to_display = {arg: display for display, arg in get_edit_menu_options(options_dict)}

OPTION_VALIDATORS = {
    "output_dir": lambda v: v.strip() or None,
    "remove": lambda v: v.lower() == 'y' if isinstance(v, str) else bool(v),
    "recursive": lambda v: v.lower() == 'y' if isinstance(v, str) else bool(v),
    "silent": lambda v: v.lower() == 'y' if isinstance(v, str) else bool(v),
    "qb_color": lambda v: int(v) if v and v.strip() else None,
    "qb_gray_color": lambda v: int(v) if v and v.strip() else None,
    "qb_gray": lambda v: int(v) if v and v.strip() else None,
    "method": lambda v: int(v),
    "dither": lambda v: int(v),
}

@log_call
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

    @log_call
    def set_status(self, msg: str, status_type: str = "INFO"):
        self.status = msg
        self.status_type = status_type
        self.refresh()

    @log_call
    def render(self):
        color = STATUS_COLORS.get(self.status_type, "yellow")
        msg = self.status or ""
        if msg:
            return Text(msg, style=f"bold {color}")
        return super().render()


class MainMenuApp(App):
    """
    Main TUI application class for A2P_Cli.
    Displays the main menu and manages navigation between screens.
    """
    TITLE = "A2P_Cli - AVIF to PNG Converter"
    CSS_PATH = None
    status: reactive[str] = reactive("")
    edit_status: reactive[str] = reactive("")
    progress: reactive[int] = reactive(0)
    progress_total: reactive[int] = reactive(1)

    @log_call
    def compose(self) -> ComposeResult:
        yield Header()
        yield Vertical(
            ListView(
                *[ListItem(Static(label), id=action) for label, action in MENU_OPTIONS],
                id="menu_list"
            ),
        )
        yield StatusFooter()

    @log_call
    async def on_mount(self) -> None:
        self.query_one("#menu_list").focus()
        self.update_status("")

    @log_call
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

    @log_call
    async def on_list_view_selected(self, event: ListView.Selected) -> None:
        action = event.item.id
        if action == "start":
            if not options_dict['input_dir'] or not str(options_dict['input_dir']).strip():
                self.update_status(f"{menu_arg_to_display['input_dir']} is required. Please set it in 'Edit Options' before starting conversion.", "ERROR")
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
                    filtered_kwargs = {k: v for k, v in options_dict.items() if k not in ['input_dir', 'output_dir', 'remove', 'recursive', 'silent', 'qb_color', 'qb_gray_color', 'qb_gray', 'log_level']}
                    convert_avif_to_png(
                        options_dict['input_dir'],
                        options_dict['output_dir'],
                        remove=options_dict['remove'],
                        recursive=options_dict['recursive'],
                        silent=options_dict['silent'],
                        qb_color=options_dict['qb_color'],
                        qb_gray_color=options_dict['qb_gray_color'],
                        qb_gray=options_dict['qb_gray'],
                        progress_callback=progress_callback,
                        progress_printer=None,
                        **filtered_kwargs
                    )
                    self.call_from_thread(self.update_status, "Conversion finished!", "SUCCESS")
                except Exception as e:
                    self.call_from_thread(self.update_status, f"Exception during conversion: {e}", "ERROR")
            threading.Thread(target=run_conversion, daemon=True).start()
        elif action == "edit":
            await self.push_screen(EditOptionsScreen())
        elif action == "update":
            check_for_update()
            self.update_status("Checked for updates.", "INFO")
        elif action == "quit":
            await self.action_quit()

    @log_call
    async def on_key(self, event: events.Key) -> None:
        if event.key == "q":
            await self.action_quit()
        elif event.key in ("ctrl+q", "^Q", "^q") or (hasattr(event, "ctrl") and event.ctrl and event.key.lower() == "q"):
            self.exit()

    @log_call
    async def action_quit(self):
        self.exit()


class EditOptionsScreen(Screen):
    """
    TUI screen for editing conversion options in A2P_Cli.
    Allows users to modify input/output directories, quantization, and other settings interactively.
    """
    status: reactive[str] = reactive("")

    @log_call
    async def on_list_view_selected(self, event: ListView.Selected) -> None:
        action = event.item.id
        handler = self.ACTION_HANDLERS.get(action)
        if handler:
            await handler(self)

    @log_call
    async def handle_input_dir(self):
        def set_input_dir(val):
            if val is not None and val.strip():
                path = Path(val.strip())
                if path.is_dir():
                    options_dict['input_dir'] = str(path)
                    self.update_status(f"Input directory set to: {options_dict['input_dir']}", "INFO")
                else:
                    self.update_status("Input directory must exist and be a directory.", "ERROR")
            elif val is not None:
                self.update_status("Invalid input. Please try again.", "ERROR")
        await self.app.push_screen(InputDialog("Enter input directory (must exist):", options_dict['input_dir'], callback=set_input_dir))

    @log_call
    async def handle_output_dir(self):
        def set_output_dir(val):
            if val is not None and val.strip():
                path = Path(val.strip())
                # Accept any syntactically valid path for output dir
                try:
                    str(path)  # This will always succeed unless path is invalid type
                    options_dict['output_dir'] = str(path)
                    self.update_status(f"Output directory set to: {options_dict['output_dir']}", "INFO")
                except Exception:
                    self.update_status("Invalid directory path. Please enter a valid full or relative path.", "ERROR")
            elif val is not None:
                options_dict['output_dir'] = None
                self.update_status("Output directory cleared (will use input dir)", "INFO")
        await self.app.push_screen(InputDialog("Enter output directory (full or relative path, blank for same as input):", options_dict['output_dir'] or "", callback=set_output_dir))

    @log_call
    async def handle_qb_color(self):
        def set_qb_color(val):
            prev = options_dict.get('qb_color')
            if val is None or not val.strip():
                options_dict['qb_color'] = None
                self.update_status("Color quantization off (full color)", "INFO")
                return
            try:
                new_val = int(val)
                if 1 <= new_val <= 8:
                    if new_val != prev:
                        options_dict['qb_color'] = new_val
                        self.update_status(f"Quantization bits for color images set to: {options_dict['qb_color']}", "INFO")
                    else:
                        self.update_status(NO_CHANGE_MSG, "INFO")
                else:
                    self.update_status(INVALID_QB_MSG, "ERROR")
            except Exception:
                self.update_status(INVALID_QB_MSG, "ERROR")
        await self.app.push_screen(InputDialog("Quantization bits for color images (1-8, blank/off for full color):", str(options_dict['qb_color']) if options_dict['qb_color'] else "", callback=set_qb_color))

    @log_call
    async def handle_qb_gray_color(self):
        def set_qb_gray_color(val):
            prev = options_dict.get('qb_gray_color')
            if val is None or not val.strip():
                options_dict['qb_gray_color'] = None
                self.update_status("Grayscale+one quantization off (full color)", "INFO")
                return
            try:
                new_val = int(val)
                if 1 <= new_val <= 8:
                    if new_val != prev:
                        options_dict['qb_gray_color'] = new_val
                        self.update_status(f"Quantization bits for grayscale+one images set to: {options_dict['qb_gray_color']}", "INFO")
                    else:
                        self.update_status(NO_CHANGE_MSG, "INFO")
                else:
                    self.update_status(INVALID_QB_MSG, "ERROR")
            except Exception:
                self.update_status(INVALID_QB_MSG, "ERROR")
        await self.app.push_screen(InputDialog("Quantization bits for grayscale+one images (1-8, blank/off for full color):", str(options_dict['qb_gray_color']) if options_dict['qb_gray_color'] else "", callback=set_qb_gray_color))

    @log_call
    async def handle_qb_gray(self):
        def set_qb_gray(val):
            prev = options_dict.get('qb_gray')
            if val is None or not val.strip():
                options_dict['qb_gray'] = None
                self.update_status("Grayscale quantization off (full color)", "INFO")
                return
            try:
                new_val = int(val)
                if 1 <= new_val <= 8:
                    if new_val != prev:
                        options_dict['qb_gray'] = new_val
                        self.update_status(f"Quantization bits for grayscale images set to: {options_dict['qb_gray']}", "INFO")
                    else:
                        self.update_status(NO_CHANGE_MSG, "INFO")
                else:
                    self.update_status(INVALID_QB_MSG, "ERROR")
            except Exception:
                self.update_status(INVALID_QB_MSG, "ERROR")
        await self.app.push_screen(InputDialog("Quantization bits for grayscale images (1-8, blank/off for full color):", str(options_dict['qb_gray']) if options_dict['qb_gray'] else "", callback=set_qb_gray))

    @log_call
    async def handle_method(self):
        def set_method(val):
            prev = options_dict.get('method')
            if val is None:
                self.update_status(CANCELED_MSG, "INFO")
            else:
                new_val = int(val)
                if new_val != prev:
                    options_dict['method'] = new_val
                    self.update_status(f"{menu_arg_to_display['method']} set to: {options_dict['method']}", "INFO")
                else:
                    self.update_status(NO_CHANGE_MSG, "INFO")
        await self.app.push_screen(InputDialog("Quantization method (0=Median Cut, 1=Max Coverage, 2=Fast Octree):", str(options_dict['method']), callback=set_method))

    @log_call
    async def handle_dither(self):
        def set_dither(val):
            prev = options_dict.get('dither')
            if val is None:
                self.update_status(CANCELED_MSG, "INFO")
            else:
                new_val = int(val)
                if new_val != prev:
                    options_dict['dither'] = new_val
                    self.update_status(f"{menu_arg_to_display['dither']} set to: {options_dict['dither']}", "INFO")
                else:
                    self.update_status(NO_CHANGE_MSG, "INFO")
        await self.app.push_screen(InputDialog("Dither (0=None, 1=Floyd-Steinberg):", str(options_dict['dither']), callback=set_dither))

    @log_call
    async def handle_remove(self):
        def set_remove(val):
            prev = options_dict.get('remove')
            if val != prev:
                options_dict['remove'] = val
                self.update_status(f"{menu_arg_to_display['remove']} set to: {options_dict['remove']}", "INFO")
            else:
                self.update_status(NO_CHANGE_MSG, "INFO")
        await self.app.push_screen(YesNoDialog("Remove originals?", options_dict['remove'], callback=set_remove))

    @log_call
    async def handle_recursive(self):
        def set_recursive(val):
            prev = options_dict.get('recursive')
            if val != prev:
                options_dict['recursive'] = val
                self.update_status(f"{menu_arg_to_display['recursive']} set to: {options_dict['recursive']}", "INFO")
            else:
                self.update_status(NO_CHANGE_MSG, "INFO")
        await self.app.push_screen(YesNoDialog("Recursive search?", options_dict['recursive'], callback=set_recursive))

    @log_call
    async def handle_silent(self):
        def set_silent(val):
            prev = options_dict.get('silent')
            if val != prev:
                options_dict['silent'] = val
                self.update_status(f"{menu_arg_to_display['silent']} set to: {options_dict['silent']}", "INFO")
            else:
                self.update_status(NO_CHANGE_MSG, "INFO")
        await self.app.push_screen(YesNoDialog("Silent mode?", options_dict['silent'], callback=set_silent))

    @log_call
    async def handle_back(self):
        save_options("TUI", {k: v for k, v in options_dict.items() if k not in ("input_dir", "output_dir", "log", "version", "check_update")})
        self.app.pop_screen()
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

    @log_call
    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("Edit Options", classes="title")
        yield ListView(id="edit_menu_list")
        yield StatusFooter()

    @log_call
    def get_option_value(self, option_key, all_options_dict):
        val = all_options_dict.get(option_key)
        if option_key in ("remove", "recursive", "silent"):
            return "Yes" if val else "No"
        if option_key == "output_dir":
            if not val:
                input_dir_val = all_options_dict.get("input_dir", "")
                if not input_dir_val:
                    return ""
                return input_dir_val
            return str(val)
        if val is None:
            return "(default)"
        return str(val)

    @log_call
    def build_option_list(self, all_options_dict, menu_display_map):
        options = []
        for label, action in get_edit_menu_options(all_options_dict):
            if 'Quantization bits' in label:
                display_label = label
                menu_display_map[action] = label
            elif action == 'back':
                display_label = label
            else:
                display_label = f"{label} [{self.get_option_value(action, all_options_dict)}]"
            options.append(ListItem(Static(display_label, classes="option-item"), id=action))
        return options

    @log_call
    def refresh_options_list(self):
        options = self.build_option_list(options_dict, menu_arg_to_display)
        list_view = self.query_one("#edit_menu_list", ListView)
        list_view.clear()
        list_view.extend(options)

    @log_call
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

    @log_call
    async def on_mount(self) -> None:
        self.query_one("#edit_menu_list").focus()
        self.update_status("")
        self.refresh_options_list()

    @log_call
    async def on_key(self, event: events.Key) -> None:
        if event.key == "backspace":
            await self.handle_back()
        elif event.key in ("ctrl+q", "^Q", "^q") or (hasattr(event, "ctrl") and event.ctrl and event.key.lower() == "q"):
            self.app.exit()


class InputDialog(ModalScreen):
    """
    Modal dialog screen for text input in the TUI.
    Used for entering or editing configuration values interactively.
    """
    def __init__(self, title: str, initial: str = "", callback=None):
        super().__init__()
        self.title = title
        self.initial = initial
        self.callback = callback

    @log_call
    def compose(self) -> ComposeResult:
        yield Static(self.title, classes="title")
        yield Static(f"Current value: {self.initial if self.initial else '(default)'}", classes="current-value")
        input_widget = Input(value=self.initial, placeholder=self.title, id="input_dialog_input")
        yield input_widget
        yield Static("[Enter] to confirm, [Esc] to cancel", classes="help")

    @log_call
    async def on_mount(self) -> None:
        input_widget = self.query_one("#input_dialog_input", Input)
        input_widget.focus()

    @log_call
    async def on_input_submitted(self, event: Input.Submitted) -> None:
        if self.callback:
            self.callback(event.value)
        self.dismiss()

    @log_call
    async def on_key(self, event: events.Key) -> None:
        if event.key == "escape":
            if self.callback:
                self.callback(None)
            self.dismiss()


class YesNoDialog(ModalScreen):
    """
    Modal dialog screen for yes/no (boolean) input in the TUI.
    Used for toggling boolean configuration values interactively.
    """
    def __init__(self, title: str, initial: bool = False, callback=None):
        super().__init__()
        self.title = title
        self.initial = initial
        self.value = initial
        self.callback = callback

    @log_call
    def compose(self) -> ComposeResult:
        yield Static(self.title, classes="title")
        yield Static(f"Current value: {'Yes' if self.initial else 'No'}", classes="current-value")
        yield ListView(
            ListItem(Static("Yes"), id="yes"),
            ListItem(Static("No"), id="no"),
            id="yesno_menu"
        )
        yield Static("[Enter] to select, [Esc] to cancel", classes="help")

    @log_call
    async def on_mount(self) -> None:
        self.query_one("#yesno_menu").index = 0 if self.initial else 1
        self.query_one("#yesno_menu").focus()

    @log_call
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

    @log_call
    async def on_key(self, event: events.Key) -> None:
        if event.key == "escape":
            if self.callback:
                self.callback(None)
            self.dismiss()


@log_call
def run():
    # Load [TUI] options from options.ini at startup
    from cli.globals import options_dict
    options_dict.update(load_options('TUI'))
    MainMenuApp().run()
