DEFAULT_IMAGES = {
    "desktop": {"base":"universal", "ros":"ros-desktop", "entrypoint":"rosbox", "image-name":"rosbox-desktop", "default":"desktop"},
    "robot-jetracer": {"base":"universal", "ros":"ros-base", "entrypoint":"rosbox", "image-name":"rosbox-robot-jetracer", "default":"robot-jetracer"},
    "robot-jetank": {"base":"universal", "ros":"ros-base", "entrypoint":"rosbox", "image-name":"rosbox-robot-jetank", "default":"robot-jetank"},
    "sim": {"base":"universal", "ros":"ros-simulation", "entrypoint":"rosbox", "image-name":"rosbox-sim", "default":"sim"}
}

DEFAULT_DOCKERHUB_IMAGES = {
    "robot-jetracer": "terren642/rosbox:robot-jetracer-latest",
    "robot-jetank": "sterren642/rosbox:robot-jetank-latest",
    "sim": "sterren642/rosbox:sim-latest",
    "desktop": "sterren642/rosbox:desktop-latest"
}
