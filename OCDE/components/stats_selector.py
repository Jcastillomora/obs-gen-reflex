import reflex as rx
from ..backend.backend import State
# from ..backend.data_items import teams_dict, position_dict, college_dict
from ..backend.data_items import años_dict, disciplinas_dict, unidades_dict
from .item_badges import _selected_item_badge, _unselected_item_badge


def _add_all_button(on_click: callable) -> rx.Component:
    return rx.button(
        rx.icon("plus", size=16),
        "Add All",
        variant="soft",
        size="2",
        on_click=on_click,
        color_scheme="green",
        cursor="pointer",
    )


def _clear_button(on_click: callable) -> rx.Component:
    return rx.button(
        rx.icon("trash", size=16),
        "Clear",
        variant="soft",
        size="2",
        on_click=on_click,
        color_scheme="tomato",
        cursor="pointer",
    )


def _items_selector(item: str, items_dict: dict) -> rx.Component:
    return rx.vstack(
        rx.flex(
            rx.hstack(
                _add_all_button(State.add_all_selected(item)),
                _clear_button(State.clear_selected(item)),
                spacing="2",
                justify="end",
                width="100%",
            ),
            direction="row",
            align="center",
            width="100%",
        ),
        rx.flex(
            rx.foreach(
                State.selected_items[item],
                lambda selected_item: _selected_item_badge(item, items_dict, selected_item),
            ),
            wrap="wrap",
        ),
        rx.divider(),
        rx.flex(
            rx.foreach(
                items_dict, lambda unselected_item: _unselected_item_badge(item, items_dict, unselected_item)
            ),
            wrap="wrap",
        ),
        width="100%",
    )



def _accordion_header_stat(icon: str, text: str, item: str) -> rx.Component:
    return rx.hstack(
        rx.icon(icon, size=24),
        rx.heading(text + f" ({(State.selected_items[item].length())})", size="5"),
        spacing="2",
        align="center",
        width="100%",
    )


def _accordion_header(icon: str, text: str) -> rx.Component:
    return rx.hstack(
        rx.icon(icon, size=24),
        rx.heading(text, size="5"),
        spacing="2",
        align="center",
        width="100%",
    )


# def _age_selector() -> rx.Component:
#     return rx.vstack(
#         rx.slider(
#             default_value=[19, 40],
#             min=19,
#             variant="soft",
#             max=40,
#             on_change=State.set_age,
#         ),
#         rx.hstack(
#             rx.badge("Min Age: ", State.age[0]),
#             rx.spacer(),
#             rx.badge("Max Age: ", State.age[1]),
#             width="100%",
#         ),
#         width="100%",
#     )


# def _salary_selector() -> rx.Component:
#     return rx.vstack(
#         rx.slider(
#             default_value=[0, 25000000],
#             min=0,
#             variant="soft",
#             max=25000000,
#             on_value_commit=State.set_salary,
#         ),
#         rx.hstack(
#             rx.badge("Min Salary: ", State.salary[0]),
#             rx.spacer(),
#             rx.badge("Max Salary: ", State.salary[1]),
#             width="100%",
#         ),
#         width="100%",
#     )


def stats_selector() -> rx.Component:
    return rx.accordion.root(
        rx.accordion.item(
            header=_accordion_header_stat("calendar", "Años", "años"),
            # content=_items_selector("teams", teams_dict),
            content=_items_selector("años", años_dict),
            value="años",
        ),
        rx.accordion.item(
            header=_accordion_header_stat("list", "Disciplinas", "disciplinas"),
            # content=_items_selector("positions", position_dict),
            content=_items_selector("disciplinas", disciplinas_dict),
            value="disciplinas",
        ),
        rx.accordion.item(
            header=_accordion_header_stat("school", "Unidad", "unidades"),
            # content=_items_selector("colleges", college_dict),
            content=_items_selector("unidades", unidades_dict),
            value="unidades",
        ),

        collapsible=True,
        default_value="teams",
        type="single",
        variant="ghost",
        width="100%",
    )



