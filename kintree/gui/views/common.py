from math import pi
from typing import Optional

from flet import Page, View, AppBar, NavigationRail, VerticalDivider
from flet import Column, Container, Icon, Row, Text, Radio, icons, padding
from flet import IconButton, TextField, Dropdown
from flet_core.animation import Animation
from flet_core.control import Control
from flet_core.types import ScaleValue


class CommonView(View):
    '''Common view to all GUI views'''

    page = None
    navigation_rail = None
    navidx = None
    NAV_BAR_INDEX = {}
    column = None
    fields = {}
    
    def __init__(self, page: Page, appbar: AppBar, navigation_rail: NavigationRail):
        # Store page pointer
        self.page = page

        # Init view
        super().__init__(route=self.route, appbar=appbar)

        # Set navigation rail
        if not self.navigation_rail:
            self.navigation_rail = navigation_rail

        # Build column
        if not self.column:
            self.column = self.build_column()

        # Build controls
        if not self.controls:
            self.controls = self.build_controls()

    def build_column(self):
        # Empty column (to be set inside the children views)
        return Column()

    def build_controls(self):
        return [
            Row(
                controls=[
                    self.navigation_rail,
                    VerticalDivider(width=1),
                    self.column,
                ],
                expand=True,
            ),
        ]


class Collapsible(Column):
    def __init__(
        self,
        title: str,
        content: Control,
        icon: Optional[Control] = None,
        spacing: float = 3,
        radio: Optional[Radio] = None,
        scale: ScaleValue = 1,
    ):
        super().__init__()
        self.icon = icon
        self.title = title
        self.scale = scale
        self.shevron = Icon(
            icons.KEYBOARD_ARROW_RIGHT_ROUNDED,
            animate_rotation=100,
            rotate=0,
            scale=self.scale,
        )
        self.content = Column(
            [Container(height=spacing), content],
            height=0,
            spacing=0,
            animate_size=100,
            opacity=0,
            animate_opacity=100,
            scale=self.scale,
        )
        self.spacing = 0
        self.radio = radio
        self.radio.scale = self.scale

    def header_click(self, e):
        self.content.height = None if self.content.height == 0 else 0
        self.content.opacity = 0 if self.content.height == 0 else 1
        self.shevron.rotate = pi/2 if self.shevron.rotate == 0 else 0
        self.update()

    def _build(self):
        title_row = Row()
        if self.icon != None:
            title_row.controls.append(self.icon)
        if self.radio:
            title_row.controls.append(self.radio)
        else:
            title_row.controls.append(Text(self.title))
        self.controls = [
                Container(
                    Row([title_row, self.shevron], alignment="spaceBetween"),
                    padding=padding.only(left=8, right=8),
                    height=38,
                    border_radius=4,
                    ink=True,
                    on_click=self.header_click,
                ),
                self.content,
            ]


class DropdownWithSearch():
    '''Implements a dropdown with search box'''
    container = None
    dropdown = None
    dropdown_width = None
    search_button = None
    search_field = None
    search_field_width = None
    search_box = None

    def __init__(self,
                 label: str,
                 width: int,
                 dense: bool,
                 options=None,
    ):
        self.dropdown_width = width
        self.search_field_width = width
        self.options = options
        self.dropdown = Dropdown(
            label=label,
            width=self.dropdown_width,
            dense=dense,
            options=options
        )
        self.search_button = IconButton('search', on_click=self.search_now)
        self.search_field = TextField(
            border="none",
            width=self.search_field_width,
            dense=dense,
            on_change=self.on_search,
        )
        self.search_box = Container(
            content=self.search_field,
            width=0,
            animate=Animation(200),
        )
        self._build()

    @property
    def value(self):
        return self.dropdown.value
    
    def update_option_list(self, input: str):
        new_list_options = []
        for option in self.options:
            if input.lower() in option.key.lower():
                new_list_options.append(option)
        return new_list_options

    def on_search(self, e):
        if self.search_field.value.replace(" ", ""):
            self.dropdown.options = self.update_option_list(self.search_field.value)
            if len(self.dropdown.options) == 1:
                self.dropdown.value = self.dropdown.options[0].key
            else:
                self.dropdown.value = None
        else:
            self.dropdown.options = self.options
        self.dropdown.update()

    def search_now(self, e):
        self.search_box.width = self.search_field_width
        self.search_box.update()
        self.search_button.icon = 'highlight_remove'
        self.search_button.on_click = self.done_search
        self.search_button.update()
        self.search_field.border = "outline"
        self.search_field.update()
        self.search_field.focus()
        if self.search_field.value:
            self.on_search(e)
    
    def done_search(self, e):
        self.search_box.width = 0
        self.search_box.update()
        self.search_button.icon = 'search'
        self.search_button.on_click = self.search_now
        self.search_button.update()
        self.search_field.border = "none"
        self.search_field.update()
        self.dropdown.options = self.options
        self.dropdown.update()

    def _build(self):
        self.container = Container(
            content=Row(
                controls=[
                    self.dropdown,
                    self.search_box,
                    self.search_button,
                ],
                alignment="center",
            ),
        )

        
class MenuButton(Container):
    def __init__(
        self,
        title: str,
        icon: Optional[Control] = None,
        selected: bool = False,
        radio: Optional[Radio] = None,
    ):
        super().__init__()
        self.icon = icon
        self.title = title
        self._selected = selected
        self.padding = padding.only(left=43)
        self.height = 38
        self.border_radius = 4
        self.ink = True
        self.on_click = self.item_click
        self.radio = radio

    def item_click(self, _):
        pass

    def _build(self):
        row = Row()
        if self.icon != None:
            row.controls.append(self.icon)
        if self.radio:
            row.controls.append(self.radio)
        else:
            row.controls.append(Text(self.title))
        self.content = row

    def _before_build_command(self):
        self.bgcolor = "surfacevariant" if self._selected else None
        super()._before_build_command()
