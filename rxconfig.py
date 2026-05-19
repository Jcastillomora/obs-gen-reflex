import reflex as rx

config = rx.Config(
    app_name="OCDE",
    plugins=[
        rx.plugins.TailwindV4Plugin(),
        rx.plugins.SitemapPlugin(),
    ],
    db_url="sqlite:///data/ocde.db",
)