DEFAULT_IMAGES = {
    "desktop": {"base":"universal", "ros":"ros-desktop", "entrypoint":"rosbox", "image-name":"rosbox-desktop"},
    "robot_jetracer": {"base":"universal", "ros":"ros-base", "entrypoint":"rosbox", "image-name":"rosbox-robot-jetracer"},
    "robot_jetank": {"base":"universal", "ros":"ros-base", "entrypoint":"rosbox", "image-name":"rosbox-robot-jetank"},
    "sim": {"base":"universal", "ros":"ros-simulation", "entrypoint":"rosbox", "image-name":"rosbox-sim"}
}

DEFAULT_DOCKERHUB_IMAGES = {
    "robot_jetracer": "terren642/rosbox:robot_jetracer-latest",
    "robot_jetank": "sterren642/rosbox:robot_jetank-latest",
    "sim": "sterren642/rosbox:sim-latest",
    "desktop": "sterren642/rosbox:desktop-latest"
}
