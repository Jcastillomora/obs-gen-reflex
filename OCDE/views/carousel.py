import reflex as rx
from ..backend.backend import State


def carousel_item(image_urls: dict, index: int) -> rx.Component:
    """A single item in the carousel."""
    return rx.el.div(
        rx.link(
            rx.image(
                src=image_urls["src"],
                alt=f"Carousel Image {index + 1}",
                class_name="absolute block w-full h-full object-contain sm:object-cover -translate-x-1/2 -translate-y-1/2 top-1/2 left-1/2",
            ),
            href=image_urls["link"],
            is_external=True,
            class_name="absolute inset-0 w-full h-full",
        ),
        class_name=rx.cond(
            State.current_index == index,
            "transition-opacity opacity-100",
            "transition-opacity opacity-0 pointer-events-none",
        ),
        data_carousel_item=rx.cond(State.current_index == index, "active", ""),
    )


def carousel_control_button(is_prev: bool) -> rx.Component:
    """A control button for the carousel (previous or next)."""
    icon_name = "chevron-left" if is_prev else "chevron-right"
    on_click_event = rx.cond(
        is_prev, State.prev_image, State.next_image
    )
    position_class = "start-0" if is_prev else "end-0"
    sr_text = "Previous" if is_prev else "Next"
    return rx.el.button(
        rx.el.span(
            rx.icon(tag=icon_name, class_name="w-3 h-3 text-white"),
            rx.el.span(sr_text, class_name="sr-only"),
            class_name="inline-flex items-center justify-center w-5 h-5 rounded-full bg-white/30 group-hover:bg-white/50 group-focus:ring-4 group-focus:ring-white group-focus:outline-none transition-colors",
        ),
        type="button",
        class_name=f"absolute top-0 {position_class} z-30 flex items-center justify-center h-full px-4 cursor-pointer group focus:outline-none",
        on_click=on_click_event,
        data_carousel_prev=is_prev,
        data_carousel_next=not is_prev,
    )


# def carousel() -> rx.Component:
#     """The image carousel component."""
#     return rx.box(
#         rx.desktop_only(
#             rx.flex(
#                 rx.foreach(
#                     State.image_urls, lambda image_urls, index: carousel_item(image_urls, index)
#                 ),
#                 class_name="relative w-full h-64 sm:h-96 md:h-[500px] lg:h-[600px] overflow-hidden",
#             ),
#         ),
#         rx.mobile_and_tablet(
#             # rx.image(
#             #     src=State.image_urls[State.current_index],
#             #     alt="Carousel Image",
#             #     class_name="w-full h-auto",
#             # ),
#             rx.flex(
#                 rx.foreach(
#                     State.image_urls, lambda image_urls, index: carousel_item(image_urls, index)
#                 ),
#                 class_name="w-full h-auto",
#             ),
#             class_name="sm:relative w-full",
#         ),
#         carousel_control_button(is_prev=True),
#         carousel_control_button(is_prev=False),
#         id="gallery",
#         class_name="w-full max-w-full",
#         data_carousel="slide",
#         on_mount=State.start_autoscroll,
#     )


def carousel() -> rx.Component:
    """The image carousel component."""
    return rx.flex(
        rx.flex(
            rx.foreach(
                State.image_urls, 
                lambda image_urls, index: carousel_item(image_urls, index)
            ),
            class_name="relative w-full h-full md:h-[500px] lg:h-[600px] overflow-hidden",
        ),
        carousel_control_button(is_prev=True),
        carousel_control_button(is_prev=False),
        id="gallery",
        class_name="relative w-full h-full",
        data_carousel="slide",
        on_mount=State.start_autoscroll,
    )