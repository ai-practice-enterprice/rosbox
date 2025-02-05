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
2. rosbox create:
   ```bash
   rosbox create ros2 test --ros_ws ../ros_ws --ssh_keys
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
  rosbox create <image> <name> [--ros_ws <path_to_ROS_workspace>] [--no_start] [--ssh_keys]
  ```
  - `image`: Specifies the Docker image name to be used.
  - `name`: Defines the name of the rosbox.
  - `--ros_ws`: (Optional) Path to your ROS workspace.
  - `--no_start`: (Optional) Prevents the container from starting immediately after creation.
  - `--ssh_keys`: (Optional) Mounts the host’s SSH directory into the container.
    - Use this option to enable the container to access and use your SSH keys, ensuring secure authentication and remote repository access. By replicating your SSH configuration inside the container, it allows seamless Git operations and remote logins without requiring additional manual key transfers.
  - `-h`: Displays help information for this command, including a summary of available options.

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
  - `-h`: Displays help information for this command.

• Build a new Docker image using templates:
  ```bash
  rosbox build --base <BASE_TEMPLATE> --ros <ROS_TEMPLATE> --name <IMAGE_NAME>
  ```
  - `--base`: (Required) Base image to use. Options are provided by available base templates.
  - `--ros`: (Required) ROS template to use. Choose from the provided ROS templates.
  - `--name`: (Required) Name for the created image.
  - `-h`: Displays help information for this command, including a summary of available options.

• Launch the interactive builder for Docker images:
  ```bash
  rosbox ibuilder <name>
  ```
  - `name`: The name assigned to the image being built.
  - `-h`: Displays help information for this command.
