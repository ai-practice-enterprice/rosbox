DEFAULT_IMAGES = {
    "desktop": {"base":"universal", "ros":"ros-desktop", "entrypoint":"rosbox", "image-name":"rosbox-desktop", "default":"desktop"},
    "desktopjazzy": {"base":"universaljazzy", "ros":"ros-desktopjazzy", "entrypoint":"rosboxjazzy", "image-name":"rosbox-desktopjazzy", "default":"desktopjazzy"},
    "robot-jetracer": {"base":"universal", "ros":"ros-base", "entrypoint":"rosbox", "image-name":"rosbox-robot-jetracer", "default":"robot-jetracer"},
    "robot-jetank": {"base":"universal", "ros":"ros-base", "entrypoint":"rosbox", "image-name":"rosbox-robot-jetank", "default":"robot-jetank"},
    "sim": {"base":"universal", "ros":"ros-simulation", "entrypoint":"rosbox", "image-name":"rosbox-sim", "default":"sim"}
}

DEFAULT_DOCKERHUB_IMAGES = {
    "robot-jetracer": "docker.io/sterren642/rosbox:robot-jetracer-latest",
    "robot-jetank": "docker.io/sterren642/rosbox:robot-jetank-latest",
    "sim": "docker.io/sterren642/rosbox:sim-latest",
    "desktop": "docker.io/sterren642/rosbox:desktop-latest",
    "desktopjazzy": "docker.io/sterren642/rosbox:desktopjazzy-latest"
}
