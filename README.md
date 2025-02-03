# Image Builder
Build different types of Docker images.

## Manual
### Create Dockerfile
- Create a Dockerfile from selected options (all options in `python build_image.py gen -h`).

    ```bash
    python build_image.py gen --base universal --ros ros-desktop --entrypoint it
    ```

### Build Image
- Build the image from the Dockerfile.

    ```bash
    python build_image.py build --image ros2
    ```

### Run Image
- Create a directory for the ROS workspace `ros_ws`.
- Create the container from the image.

    ```bash
    docker run -it --rm --hostname ros-desktop -v ./ros_ws:/home/ros/ros_ws ros2
    ```