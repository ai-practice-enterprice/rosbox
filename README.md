# RosBox
rosbox is a ontainer management tool designed explicitly for Docker containers running ROS (Robot Operating System).
It streamlines the process of deploying and managing ROS environments by encapsulating the necessary dependencies within Docker containers.
Additionally, rosbox can build container images based on templates, ensuring consistent and reproducible setups for the project.

## Install
1. Install docker.
   - windows: [Docker Desktop](https://www.docker.com/get-started/)
   - linux: [Docker Engine](https://docs.docker.com/engine/install/ubuntu/)
2. Clone the repository or download the zip file.
   ```bash
   git clone https://github.com/ai-practice-enterprice/image_builder
   ```
3. Go to the root of project.
4. run:
    ```bash
    pip install .
    ```
5. Now you can use robox anywhere in the command line.

## Basic Example

This is a basic example demonstrating rosbox commands:

1. rosbox ibuilder:
   ```bash
   rosbox ibuilder ros2
   ```
    - Select generation method: custom
    - Select the base template: universal
    - Select the ROS template: ros-desktop
2. rosbox create:
   ```bash
   rosbox create ros2 test --ros_ws <path_to_ROS_workspace> --ssh_keys
   ```
3. rosbox enter:
   ```bash
   rosbox enter test
   ```
4. rosbox stop:
   ```bash
   rosbox stop test
   ```
5. rosbox remove:
   ```bash
   rosbox remove test
   ```

## Usage
- Create a new rosbox container:
  ```bash
  rosbox create <image> <name> [--custom] [--build] [--ros_ws <path_to_ROS_workspace>] [--no_start] [--ssh_keys] [--no_host_net]
  ```
  - `image`: The Docker image to use. By default, uses pre-built default images. When used with --custom flag, expects full Docker image name. When used with --build flag, builds the default image locally.
  - `name`: Defines the name of the rosbox.
  - `--custom`, `-c`: (Optional) Use a custom Docker image by providing its full name.
  - `--build`, `-b`: (Optional) Build and use a local default image instead of using pre-built ones.
  - `--ros_ws`, `-w`: (Optional) Path to your ROS workspace.
  - `--no_start`: (Optional) Prevents the container from starting immediately after creation.
  - `--ssh_keys`, `-s`: (Optional) Mounts the host's SSH directory into the container.
    - Use this option to enable the container to access and use your SSH keys, ensuring secure authentication and remote repository access. By replicating your SSH configuration inside the container, it allows seamless Git operations and remote logins without requiring additional manual key transfers.
  - `--no_host_net`: (Optional) Do not use the host network.
    - When enabled, this flag tells rosbox to configure the Docker container with its own isolated network stack instead of sharing the host's network.
    - This setup enhances security and helps prevent potential network conflicts between the container and the host system.
  - `-h`: Displays help information for this command, including a summary of available options.
  - `--gpu`: (Optional) Enables NVIDIA GPU passthrough to the container. (not implemented yet!!!!)

- Start an existing rosbox:
```bash
  rosbox start <name>
```
  - `name`: The name of the rosbox container to start.
  - `-h`: Displays help information for this command, including a summary of available options.

- Enter a running rosbox container:
  ```bash
  rosbox enter <name>
  ```
  - `name`: The name of the rosbox container to access.
  - `-h`: Displays help information for this command, including a summary of available options.

- Stop a running rosbox container:
  ```bash
  rosbox stop <name>
  ```
  - `name`: The name of the rosbox container to stop.
  - `-h`: Displays help information for this command,.

- List all available rosboxes:
  ```bash
  rosbox list
  ```

- Remove an existing rosbox container:
  ```bash
  rosbox remove <name>
  ```
  - `name`: The name of the rosbox container to remove.
  - `--no_build`: (Optional) Skip the image building process. And generate the Dockerfile only.
  - `-h`: Displays help information for this command.

• Build a default Docker image:
  ```bash
  rosbox build <image>
  ```
  - `image`: Choose from available default images to build. (`desktop`, `robot-jetracer`, `robot-jetank`, `sim`)
  - `-h`: Displays help information for this command, including a summary of available options.

• Launch the interactive builder for Docker images:
  ```bash
  rosbox ibuilder <name>
  ```
  - `name`: The name assigned to the image being built.
  - `-h`: Displays help information for this command.

## image templates
### default
- base: ubuntu:20.04
- ros: ros-desktop

### base templates
- universal: ubuntu:20.04
- toolbox: for distrobox not for rosbox
- (in progress) nvidia: nvidia/cuda:11.4.1-cudnn8-devel-ubuntu20.04

### ros templates
- core: ros-core
> minimal Installation with essential ROS 2 communication packages (publish/subscribe,services,etc...) \
> does **not** include visualisation tools or other add-ons
- base: ros-base (extends the `ROS Core`)
> adds some additional CLI tools and basic packages \
> such as the **robot_state_publisher** or **URDF** which will be required when combining `ROS` and `Gazebo`
- desktop: ros-desktop (extends `ROS Base`)
> adds visualisation tools such as **Rviz** (to vizualize URDF files)
- desktop-full: ros-desktop-full (extends `Desktop`)
> adds the `Perception` and `Simulation` packages and `Gazebo` simulation demos
- perception: ros-perception (extends `ROS Base`)
> adds other packages like **vision_opencv** or **laser_geometry** \
> (libraries for working with sensors,computer vision,etc...)
- simulation: ros-simulation (extends `ROS Base`)
> adds other packages like **ros_gz_bridge** or **ros_gz_sim** \
> which are `Gazebo` plugins for `ROS`
