DEFAULT_IMAGES = {
    "desktop": {"base":"universal", "ros":"ros-desktop", "entrypoint":"rosbox", "image-name":"rosbox-desktop"},
    "robot_jetracer": {"base":"universal", "ros":"ros-base", "entrypoint":"rosbox", "image-name":"rosbox-robot-jetracer"},
    "robot_jetank": {"base":"universal", "ros":"ros-base", "entrypoint":"rosbox", "image-name":"rosbox-robot-jetank"},
    "sim": {"base":"universal", "ros":"ros-simulation", "entrypoint":"rosbox", "image-name":"rosbox-sim"}
}

DEFAULT_DOCKERHUB_IMAGES = {
    "desktop": "yourdockerhub_username/rosbox:ros-desktop",
    "robot_jetracer": "yourdockerhub_username/rosbox:ros-base",
    "robot_jetank": "yourdockerhub_username/rosbox:ros-base",
    "sim": "yourdockerhub_username/rosbox:ros-simulation"
}
