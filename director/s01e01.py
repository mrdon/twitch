import logging

from director.obs import DevMattersShow

FFMPEG_SOURCE = "ffmpeg_source"

logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    with DevMattersShow() as show:
        show.set_section(
            title="DEV MATTERS",
            byline="Topic: Can dev productivity be measured?",
            guest_1_title="Dylan Etkin - Sleuth",
        )
        show.set_section(
            title="WAR STORIES",
            byline="When did it all go wrong?",
            b_roll="/home/mrdon/Videos/dev-matters-q1-broll.mp4",
        )
        show.set_section(
            title="METRICS: GOOD AND BAD",
            byline="What metrics to avoid? Any good ones?",
        )
        show.set_section(
            title="ACCELERATE METRICS",
            byline="What are they and why do they matter?",
            b_roll="/home/mrdon/Videos/dev-matters-q3-broll.mp4",
        )
