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
    pip install -e .
    ```
5. Now you can use robox anywhere in the command line.
6. test rosbox command:
    ```bash
    rosbox --help
    ```
  - if you get the help message, you have successfully installed rosbox.
  - if you get an error on windows
    - You can use ```python -m rosbox.rosbox``` instead of ```rosbox```
    - Or you may need to add the python scripts folder to your PATH environment variable.

## Basic Example

This is a basic example demonstrating rosbox commands:

1. rosbox create:
   ```bash
   rosbox create desktop ros2 --ros_ws <path_to_ROS_workspace> --ssh_keys
   ```
2. rosbox enter:
   ```bash
   rosbox enter ros2
   ```
3. rosbox stop:
   ```bash
   rosbox stop ros2
   ```
4. rosbox remove:
   ```bash
   rosbox remove ros2
   ```

5. (Only for desktop version): run the zenoh-bridge-ros2dds client to the router in new terminal:
    - Keep the terminal open as long as you want to keep the bridge running.
    - Use ctrl+C to stop the bridge.

    ```bash
    zenoh-bridge-ros2dds -e tcp/<server-ip>:7447
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

- Build a default Docker image:
  ```bash
  rosbox build <image>
  ```
  - `image`: Choose from available default images to build. (`desktop`, `robot-jetracer`, `robot-jetank`, `sim`)
  - `-h`: Displays help information for this command, including a summary of available options.

- Launch the interactive builder for Docker images:
   ```bash
   rosbox ibuilder <name>
   ```
    - `name`: The name assigned to the image being built.
    - `-h`: Displays help information for this command.

## Configuration

rosbox uses a configuration file to store user preferences and settings. The configuration file is automatically created with default values when you first run rosbox.

### Configuration File Location
- Windows: `C:\Users\<username>\AppData\Roaming\rosbox\config.json`
- Linux: `~/.config/rosbox/config.json`

### Default Configuration
```python
DEFAULT_CONFIG = {
    "container_manager": "docker",
    "use_x11": True,
    "mount_dev_dir": True
}
```

### Configuration Options

- **container_manager**: Specifies which container technology to use
  - `docker`: Uses Docker for container management (default)
  - `distrobox`: Uses Distrobox, which provides a more seamless integration with the host system

- **use_x11**: Controls X11 window forwarding for GUI applications
  - `True`: Enables X11 forwarding, allowing GUI applications in the container to display on the host (default)
  - `False`: Disables X11 forwarding, suitable for headless setups or when GUI applications are not needed

- **mount_dev_dir**: Controls whether to mount the host's /dev directory
  - `True`: Mounts the host's /dev directory, providing access to hardware devices like sensors and cameras (default)
  - `False`: Does not mount the /dev directory, providing better isolation but limited hardware access

You can modify these settings by directly editing the configuration file or using the rosbox API programmatically.

## image templates
rosbox comes with several pre-built image templates:

### Available Image Templates

- **desktop**: A comprehensive development environment that includes:
  - Full ROS desktop installation with all core packages
  - Development tools and libraries
  - Simulation tools (Gazebo, RViz, etc.)
  - GUI support for visualization and debugging

- **robot-jetracer**: Replicates the NVIDIA JetRacer platform environment:
  - ROS base installation
  - JetRacer-specific ros libraries
  - Provides exact software configuration as the physical robot for consistent development

- **robot-jetank**: Mirrors the NVIDIA JetBot/JetTank platform environment:
  - ROS base installation
  - JetBot-specific ros libraries
  - Provides exact software configuration as the physical robot for consistent development

- **sim**: Focused on simulation capabilities:
  - ROS base installation
  - Full simulation stack (Gazebo, RViz)
  - Simplified environment for running simulations

You can select these templates when creating a new rosbox or building a custom image.

## Distrobox Support

RosBox offers native support for Distrobox, an alternative container management system that provides more seamless integration with the host Linux system compared to Docker.

### What is Distrobox?

Distrobox is a tool that allows you to use any Linux distribution inside your terminal. It uses containers to create isolated environments while integrating deeply with the host system, providing a more native experience than traditional Docker containers.

### Benefits of Using Distrobox with RosBox

- **Seamless integration**: Access host system resources more naturally
- **Better hardware support**: Easier access to devices and peripherals
- **Common home directory**: Share files between host and container more easily
- **Simplified permissions**: Avoid common Docker permission issues

### Using RosBox with Distrobox

To enable Distrobox support, edit your RosBox configuration file and set:

```json
{
  "container_manager": "distrobox"
}
```

### Command Differences for Distrobox Mode

When using Distrobox mode, some commands have different options:

- **Create a container:**
  ```bash
  rosbox create <image> <name> [--custom] [--ros_home <path>] [--gpu]
  ```
  - `--ros_home`: Specify the container home path (instead of `--ros_ws` in Docker mode)
  - `--gpu`: Enable NVIDIA GPU support
  - Note: `--build`, `--no_start`, `--ssh_keys`, and `--no_host_net` are not available in Distrobox mode

### Limitations

- Distrobox support is only available on Linux hosts
- Some commands like `start` and `stop` are not supported since Distrobox containers behave differently
- Building custom images works differently - RosBox will generate a Dockerfile but not build the image directly

### Example Usage

```bash
# Create a ROS2 desktop container using Distrobox
rosbox create desktop ros2_distro --ros_home /path/to/home --gpu

# Enter the container
rosbox enter ros2_distro

# List all distrobox containers
rosbox list

# Remove a container
rosbox remove ros2_distro
```
