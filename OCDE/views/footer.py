import reflex as rx

def footer_item(text: str, href: str) -> rx.Component:
    return rx.link(rx.text(text, size="3", color_scheme="indigo", high_contrast=True, class_name="text-white"), href=href)


def footer_items_1() -> rx.Component:
    return rx.flex(
        rx.heading(
            "PRODUCTS", size="4", weight="bold", as_="h3"
        ),
        footer_item("Web Design", "/#"),
        footer_item("Web Development", "/#"),
        footer_item("E-commerce", "/#"),
        footer_item("Content Management", "/#"),
        footer_item("Mobile Apps", "/#"),
        spacing="4",
        text_align=["center", "center", "start"],
        flex_direction="column",
        class_name="text-gray-50",
    )


def footer_items_2() -> rx.Component:
    return rx.flex(
        rx.heading(
            "RESOURCES", size="4", weight="bold", as_="h3"
        ),
        footer_item("Blog", "/#"),
        footer_item("Case Studies", "/#"),
        footer_item("Whitepapers", "/#"),
        footer_item("Webinars", "/#"),
        footer_item("E-books", "/#"),
        spacing="4",
        text_align=["center", "center", "start"],
        flex_direction="column",
        class_name="text-gray-50",
    )


def footer_items_3() -> rx.Component:
    return rx.flex(
        rx.heading(
            "ABOUT US", size="4", weight="bold", as_="h3"
        ),
        footer_item("Our Team", "/#"),
        footer_item("Careers", "/#"),
        footer_item("Contact Us", "/#"),
        footer_item("Privacy Policy", "/#"),
        footer_item("Terms of Service", "/#"),
        spacing="4",
        text_align=["center", "center", "start"],
        flex_direction="column",
        class_name="text-gray-50",
    )


def social_link(icon: str, href: str) -> rx.Component:
    return rx.link(rx.icon(icon), href=href)


def socials() -> rx.Component:
    return rx.flex(
        social_link("instagram", "/#"),
        social_link("twitter", "/#"),
        social_link("facebook", "/#"),
        social_link("linkedin", "/#"),
        spacing="3",
        justify_content=["center", "center", "end"],
        width="100%",
        class_name="text-white",
    )


def footer() -> rx.Component:
    return rx.el.footer(
        rx.vstack(
            rx.flex(
                footer_items_1(),
                footer_items_2(),
                footer_items_3(),
                justify="between",
                spacing="6",
                flex_direction=["column", "column", "row"],
                width="100%",
            ),
            rx.divider(),
            rx.flex(
                rx.hstack(
                    rx.link(rx.image(
                        src="https://vrip.ufro.cl/wp-content/uploads/2022/04/newRecurso-3muestra.webp",
                        # width="1em",
                        # height="2em",
                        # border_radius="25%",
                    ), href="https://vrip.ufro.cl/"),
                    rx.text(
                        "© 2024 VRIP UFRO",
                        size="3",
                        white_space="nowrap",
                        weight="medium",
                    ),
                    spacing="2",
                    align="center",
                    justify_content=[
                        "center",
                        "center",
                        "start",
                    ],
                    width="100%",
                ),
                socials(),
                spacing="4",
                flex_direction=["column", "column", "row"],
                width="100%",
                class_name="text-white",
            ),
            spacing="5",
            width="100%",
        ),
        width="100%",
        padding_x=["1.5em", "1.5em", "3em", "5em"],
        padding_y=["1.25em", "1.25em", "2em"],
        # background_color="var(--accent-2)",
        class_name="bg-gradient-to-r from-blue-500 to-sky-400",
    )