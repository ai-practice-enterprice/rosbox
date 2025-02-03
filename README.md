# Image Builder
Build different types of Docker images.

## Installation of script
- Install docker.
    - windows: [Docker Desktop](https://www.docker.com/get-started/)
    - linux: [Docker Engine](https://docs.docker.com/engine/install/ubuntu/)
- Clone the repository or download the zip file.
    ```bash
    git clone https://github.com/ai-practice-enterprice/image_builder
    ```
- Install the requirements.
    ```bash
    pip install -r requirements.txt
    ```
## Usage
### Manual
#### Create Dockerfile
- Create a Dockerfile from selected options (all options in `python build_image.py gen -h`).

    ```bash
    python build_image.py gen --base universal --ros ros-desktop --entrypoint it
    ```

#### Build Image
- Build the image from the Dockerfile.

    ```bash
    python build_image.py build --tag ros2
    ```

#### Run Image
- Create a directory for the ROS workspace `ros_ws`.
- Create the container from the image. Do not forget to replace `<path_to_ros_ws>` with the path to the `ros_ws` directory.

    ```bash
    docker run -it --rm --hostname ros-desktop -v <path_to_ros_ws>:/home/ros/ros_ws ros2
    ```
    This wil create a container with the name `ros-desktop` and mount the `ros_ws` directory.
    And will remove the container after it is stopped. To keep the container, remove the `--rm` option.
