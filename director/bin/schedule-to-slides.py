import os
from slugify import slugify

import sys
sys.path.append(os.path.abspath("."))

from director.schedule import get_scheduled_events


def main():
    for event in get_scheduled_events():
        if not event.sections:
            continue

        title = slugify(event.title)
        path = f"director/templates/slides/{title}.html"
        if os.path.exists(path):
            print(f"[SKIP]   {path}")
            continue

        print(f"[CREATE] {path}")
        with open(path, "w") as f:
            f.write("""
{% extends "slides_master.html" %}
            """)
            f.write("{% block title %}" + event.title + "{% endblock %}")
            f.write("""
{% block content %}
            """)
            f.write(f"""
            <section>
                <h2>{event.title}</h2>
                <small>Don Brown<br />CTO/Co-founder, Sleuth</small>
            </section>
                            """)
            for section in event.sections:

                f.write(f"""
<section>
    <h2>{section.title}</h2>
    <p>
    {section.byline}
    </p>
</section>
                """)

            f.write("""
{%  endblock %}
            """)


if __name__ == "__main__":
    main()