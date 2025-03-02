from .config import load_config, save_config, update_config
from .imageBuilder import InteractiveBuilder
from .defaults import DEFAULT_IMAGES, DEFAULT_DOCKERHUB_IMAGES
import docker
from docker.types import Mount
import subprocess
import argparse
import os

def check_docker():
    try:
        result = subprocess.run(['docker', '--version'],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                encoding='utf-8')
        if result.returncode != 0:
            print("Error: Docker is not installed. Please install Docker first!")
            exit(1)
    except Exception as e:
        print("Error running docker --version:", e)
        exit(1)

def check_os():
    if os.name == 'nt':
        return 'windows'
    elif os.name == 'posix':
        return 'linux'
    else:
        return 'unknown'

# class for creating, running, entering and stopping the containers
class ContainerManager:
    # global defentions
    rosbox_suffix = 'rosbox'
    dockerfile_path = 'Dockerfile'

    def __init__(self):
        self.client = docker.from_env()
        self.interactive_builder = InteractiveBuilder(self.dockerfile_path)
        self.config = load_config()

    def pull_image(self, image):
        try:
            print("Downloading image...")
            for line in self.client.api.pull(DEFAULT_DOCKERHUB_IMAGES[image], stream=True, decode=True):
                if 'progress' in line:
                    print(f"\r{line['status']}: {line['progress']}", end='')
                elif 'status' in line:
                    print(f"\r{line['status']}", end='')
            print("\nDownload complete!")
            return DEFAULT_DOCKERHUB_IMAGES[image]
        except Exception as e:
            print(f"Error pulling image: {str(e)}")
            exit(1)

    def select_default_image(self, image, pullOrBuild: bool):
        if image in DEFAULT_IMAGES:
            if pullOrBuild:
                print(f'use default image {DEFAULT_IMAGES[image]["image-name"]} from dockerhub')
                # First check if image exists locally
                try:
                    local_image = self.client.images.get(DEFAULT_DOCKERHUB_IMAGES[image])
                    try:
                        # Check for updates
                        print("Checking for updates...")
                        return self.pull_image(image)
                        return DEFAULT_DOCKERHUB_IMAGES[image]
                    except Exception as e:
                        print(f"Warning: Could not check for updates: {str(e)}")
                        return DEFAULT_DOCKERHUB_IMAGES[image]
                except docker.errors.ImageNotFound:
                    print(f"Image '{DEFAULT_DOCKERHUB_IMAGES[image]}' not found locally. Pulling from Docker Hub...")
                    return self.pull_image(image)
            else:
                print(f'use default image {DEFAULT_IMAGES[image]["image-name"]} and build locally')
                try:
                    self.client.images.get(DEFAULT_IMAGES[image]["image-name"])
                    return DEFAULT_IMAGES[image]["image-name"]
                except docker.errors.ImageNotFound:
                    print(f"Error: Local image '{DEFAULT_IMAGES[image]['image-name']}' not found. Please build it first using:")
                    print(f"  rosbox build {image}")
                    exit(1)
        else:
            print(f"Error: Image '{image}' not found in DEFAULT_IMAGES")
            exit(1)

    # TODO add nvidia suport
    def create_container_docker(self, image_tag, container_name, ros_ws_path=None, auto_start=True, ssh_dir=False, host_net=True, gpu=False):
        container_name = f"{container_name}_{self.rosbox_suffix}"
        try:
            existing_container = self.client.containers.get(container_name)
            print(f"Error: Container with name '{container_name.replace('_' + self.rosbox_suffix, '')}' already exists")
            exit(1)
        except docker.errors.NotFound:
            pass
        try:
            # create mounts
            mounts = []
            if ssh_dir:
                ssh_path = os.path.expanduser("~/.ssh")
                if os.path.exists(ssh_path):
                    mounts.append(Mount(
                        target="/home/ubuntu/.ssh",
                        source=ssh_path,
                        type="bind",
                        read_only=True  # Read-only for security
                    ))
            # create container
            if check_os() == 'windows': # for running on windows
                # add ros_ws mount for ROS workspace
                if ros_ws_path:
                    mounts.append(Mount(
                        target="/home/ubuntu/ros_ws",
                        source=os.path.abspath(ros_ws_path),
                        type="bind",
                        read_only=False
                    ))
                # add X11 mount for GUI support on windows
                mounts.append(Mount(target="/tmp/.X11-unix", source="/run/desktop/mnt/host/wslg/.X11-unix", type="bind"))
                mounts.append(Mount(target="/dev", source="/dev", type="bind"))
                container = self.client.containers.create(
                    image_tag, name=container_name,
                    hostname=container_name.replace('_' + self.rosbox_suffix, ''),
                    detach=True,
                    mounts=mounts,
                    labels={"type": "rosbox"},
                    network_mode="host" if host_net else "bridge",
                    environment=["DISPLAY=:0"],
                    privileged = True
                )
            elif check_os() == 'linux': # for running on linux
                # add ros_ws mount for ROS workspace
                if ros_ws_path:
                    mounts.append(Mount(
                        target="/home/ubuntu/ros_ws",
                        source=os.path.abspath(ros_ws_path),
                        type="bind",
                        read_only=False,
                        propagation="rslave"
                    ))
                # add X11 and Xauthority mounts for GUI support on linux
                mounts.append(Mount(target="/tmp/.X11-unix", source="/tmp/.X11-unix", type="bind"))
                mounts.append(Mount(target=os.environ.get('XAUTHORITY'), source=os.environ.get('XAUTHORITY'), type="bind", read_only=True))
                mounts.append(Mount(target="/dev", source="/dev", type="bind"))
                # create container
                container = self.client.containers.create(
                    image_tag, name=container_name,
                    hostname=container_name.replace('_' + self.rosbox_suffix, ''),
                    detach=True,
                    mounts=mounts,
                    labels={"type": "rosbox"},
                    network_mode="host" if host_net else "bridge",
                    environment=["DISPLAY=:0", "XAUTHORITY=" + str(os.environ.get('XAUTHORITY'))],
                    privileged=True
                )
            else:
                print("Error: Unsupported OS")
                exit(1)

            print(f"Container {container_name.replace('_' + self.rosbox_suffix, '')} created successfully")
            # start container
            if auto_start:
                container.start()
                print(f"Container {container_name.replace('_' + self.rosbox_suffix, '')} started successfully")
        except Exception as e:
            print(f"Error creating container: {str(e)}")
            raise

    def create_container_distrobox(self, image_tag, container_name, home_dir=None):
        container_name = f"{container_name}_{self.rosbox_suffix}"
        try:
            # Check if distrobox is installed
            result = subprocess.run(['which', 'distrobox'],
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE,
                                  encoding='utf-8')
            if result.returncode != 0:
                print("Error: distrobox is not installed. Please install distrobox first!")
                exit(1)

            # Prepare command
            cmd = ['distrobox', 'create', '-i', image_tag, '-n', container_name]

            # Add home directory if specified
            if home_dir:
                cmd.extend(['--home', os.path.abspath(home_dir)])

            # Create the distrobox container
            result = subprocess.run(cmd,
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE,
                                  encoding='utf-8')

            if result.returncode != 0:
                print(f"Error creating distrobox container: {result.stderr}")
                exit(1)
            else:
                print(f"Distrobox container {container_name.replace('_' + self.rosbox_suffix, '')} created successfully")

        except Exception as e:
            print(f"Error creating distrobox container: {str(e)}")
            raise

    def start_container(self, container_name):
        container_name = f"{container_name}_{self.rosbox_suffix}"
        try:
            container = self.client.containers.get(container_name)
            container.start()
            print(f"Container {container_name.replace('_' + self.rosbox_suffix, '')} started successfully")
        except Exception as e:
            print(f"Error starting container: {str(e)}")
            raise

    def enter_container_docker(self, container_name):
        container_name = f"{container_name}_{self.rosbox_suffix}"
        try:
            container = self.client.containers.get(container_name)
            if container.status != 'running':
                container.start()
                print(f"Container {container_name.replace('_' + self.rosbox_suffix, '')} started before entering")
            command = f"docker exec -it {container_name} bash"
            subprocess.run(command, shell=True)
        except Exception as e:
            print(f"Error entering container: {str(e)}")
            raise

    def enter_container_distrobox(self, cotnaienr_name):
        container_name = f"{cotnaienr_name}_{self.rosbox_suffix}"
        try:
            # Check if distrobox is installed
            result = subprocess.run(['which', 'distrobox'],
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE,
                                  encoding='utf-8')
            if result.returncode != 0:
                print("Error: distrobox is not installed. Please install distrobox first!")
                exit(1)

            # Enter the distrobox container
            command = f"distrobox enter {container_name}"
            subprocess.run(command, shell=True)
        except Exception as e:
            print(f"Error entering distrobox container: {str(e)}")
            raise

    def stop_container(self, container_name):
        container_name = f"{container_name}_{self.rosbox_suffix}"
        try:
            container = self.client.containers.get(container_name)
            container.stop()
            print(f"Container {container_name.replace('_' + self.rosbox_suffix, '')} stopped successfully")
        except Exception as e:
            print(f"Error stopping container: {str(e)}")
            raise

    def list_containers_docker(self):
        containers = [c for c in self.client.containers.list(all=True, filters={"label": "type=rosbox"})]
        print(f"{'ID':<12} | {'NAME':<20} | {'STATUS':<20} | {'IMAGE':<20}")
        print("-" * 72)
        for container in containers:
            name = container.name.replace("_" + self.rosbox_suffix, "")
            print(f"{container.short_id:<12} | {name:<20} | {container.status:<20} | {container.image.tags[0]:<20}")
        print(("-" * 72) + "\n")

    def list_containers_distrobox(self):
        try:
            # Check if distrobox is installed
            result = subprocess.run(['which', 'distrobox'],
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE,
                                  encoding='utf-8')
            if result.returncode != 0:
                print("Error: distrobox is not installed. Please install distrobox first!")
                return

            # List all distrobox containers
            result = subprocess.run(['distrobox', 'list'],
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE,
                                  encoding='utf-8')

            if result.returncode != 0:
                print(f"Error listing distrobox containers: {result.stderr}")
                return

            # Filter only distrobox containers with _rosbox suffix
            containers = []
            lines = result.stdout.strip().split('\n')

            # Skip header line
            if len(lines) > 1:
                header = lines[0]
                print(header)
                print("-" * len(header))

                for line in lines[1:]:
                    if f"_{self.rosbox_suffix}" in line:
                        print(line)
                        containers.append(line)

                if not containers:
                    print(f"No distrobox containers with _{self.rosbox_suffix} suffix found.")
            else:
                print("No distrobox containers found.")

        except Exception as e:
            print(f"Error listing distrobox containers: {str(e)}")

    def remove_container_docker(self, container_name):
        container_name = f"{container_name}_{self.rosbox_suffix}"
        try:
            container = self.client.containers.get(container_name)
            if container.status == 'running':
                print(f"Please stop the {container_name.replace('_' + self.rosbox_suffix, '')} first.")
                return
            container.remove()
            print(f"Container {container_name.replace('_' + self.rosbox_suffix, '')} removed successfully")
        except Exception as e:
            print(f"Error removing container: {str(e)}")
            raise

    def remove_container_distrobox(self, container_name):
        container_name = f"{container_name}_{self.rosbox_suffix}"
        try:
            # Check if distrobox is installed
            result = subprocess.run(['which', 'distrobox'],
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE,
                                  encoding='utf-8')
            if result.returncode != 0:
                print("Error: distrobox is not installed. Please install distrobox first!")
                exit(1)

            # Remove the distrobox container
            result = subprocess.run(['distrobox', 'rm', container_name],
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE,
                                  encoding='utf-8')

            if result.returncode != 0:
                print(f"Error removing distrobox container: {result.stderr}")
                exit(1)
            else:
                print(f"Distrobox container {container_name.replace('_' + self.rosbox_suffix, '')} removed successfully")

        except Exception as e:
            print(f"Error removing distrobox container: {str(e)}")
            raise

    def build_image(self, image):
        if image not in DEFAULT_IMAGES:
            print(f"Error: Image '{image}' not found in DEFAULT_IMAGES")
            exit(1)
        image_name = DEFAULT_IMAGES[image]["image-name"]
        print(f"Building image {image_name}...")
        base_template = DEFAULT_IMAGES[image]["base"]
        ros_template = DEFAULT_IMAGES[image]["ros"]
        enteryPoint_template = DEFAULT_IMAGES[image]["entrypoint"]
        default_template = DEFAULT_IMAGES[image]["default"]
        self.interactive_builder.generator.generate_dockerfile(base_template, ros_template, enteryPoint_template, self.interactive_builder.dockerfile_path, default_template)
        self.interactive_builder.image_builder.build_image(image_name)

    def build_image_it(self, image_name, no_build):
        self.interactive_builder.generate_dockerfile(entryPoint = 'rosbox')
        if not no_build:
            self.interactive_builder.build_image(image_name)

def main():
    # check first if docker is installed
    check_docker()

    manager = ContainerManager()

    parser = argparse.ArgumentParser(description='rosbox manager')
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # Create parser for "create" command
    create_parser = subparsers.add_parser('create', help='create rosbox')
    create_parser.add_argument('image',
        help='If no flags: default images {' + ', '.join(DEFAULT_IMAGES.keys()) + '}. ' +
             'If --custom: full Docker image name. ' +
             'If --build: name default images to build locally')
    if manager.config["container_manager"] == "distrobox":
        create_parser.add_argument('name', help='name of the rosbox')
        create_parser.add_argument('--ros_home', '-w', help='path to the container home', default=None)
        create_parser.add_argument('--custom', '-c', help='Use a custom image (provide full image name)', action='store_true')
    else:
        create_parser.add_argument('name', help='name of the rosbox')
        create_parser.add_argument('--custom', '-c', help='Use a custom Docker image (provide full image name)', action='store_true')
        create_parser.add_argument('--build', '-b', help='Use locally built default image instead of prebuilt one', action='store_true')
        create_parser.add_argument('--ros_ws', '-w', help='path to the ROS workspace', default=None)
        create_parser.add_argument('--no_start', help='disable container autostart wen created', action='store_true')
        create_parser.add_argument('--ssh_keys', '-s', help='mount the ssh dir from host to container', action='store_true')
        create_parser.add_argument('--no_host_net', help='do not use the host network', action='store_true')
    # TODO add nvidia suport
    # create_parser.add_argument('--gpu', help='use nvidia runtime', action='store_true')

    # Create parser for "start" command
    start_parser = subparsers.add_parser('start', help='start rosbox')
    start_parser.add_argument('name', help='name of the rosbox')

    # Create parser for "enter" command
    enter_parser = subparsers.add_parser('enter', help='start rosbox')
    enter_parser.add_argument('name', help='name of the rosbox')

    # Create parser for "stop" command
    stop_parser = subparsers.add_parser('stop', help='start rosbox')
    stop_parser.add_argument('name', help='name of the rosbox')

    # Create parser for "list" command
    subparsers.add_parser('list', help='start rosbox')

    # Create parser for "remove" command
    remove_parser = subparsers.add_parser('remove', help='start rosbox')
    remove_parser.add_argument('name', help='name of the rosbox')

    # Create parser for "build" command
    build_parser = subparsers.add_parser('build', help='build a default image')
    build_parser.add_argument('image', help='default image choose from {' + ', '.join(DEFAULT_IMAGES.keys()) + '}')

    # Create parser for "ibuilder" command
    ibuilder_parser = subparsers.add_parser('ibuilder', help='Build docker image using a interactive interface to select the templates')
    ibuilder_parser.add_argument('name', help='name of the image')
    ibuilder_parser.add_argument('--no_build', help='do not build the image but only generate the Dockerfile', action='store_true')

    args = parser.parse_args()

    if args.command == 'create':
        if manager.config["container_manager"] == "docker":
            if args.custom:
                image = args.image
            elif args.build:
                image = manager.select_default_image(args.image, False)
            else:
                image = manager.select_default_image(args.image, True)
            manager.create_container_docker(image, args.name, args.ros_ws, not args.no_start, args.ssh_keys, not args.no_host_net)
        elif manager.config["container_manager"] == "distrobox":
            if check_os() != "linux":
                print("Distrobox is only supported on Linux")
                exit(1)
            if args.custom:
                image = args.image
            else:
                image = manager.select_default_image(args.image, True)
            manager.create_container_distrobox(image, args.name, args.ros_home,)
    elif args.command == 'start':
        if manager.config["container_manager"] == "distrobox":
            print("command not supported for distrobox")
            exit(1)
        manager.start_container(args.name)
    elif args.command == 'enter':
        if manager.config["container_manager"] == "docker":
            manager.enter_container_docker(args.name)
        elif manager.config["container_manager"] == "distrobox":
            manager.enter_container_distrobox(args.name)
    elif args.command == 'stop':
        if manager.config["container_manager"] == "distrobox":
            print("command not supported for distrobox")
            exit(1)
        manager.stop_container(args.name)
    elif args.command == 'list':
        if manager.config["container_manager"] == "docker":
            manager.list_containers_docker()
        elif manager.config["container_manager"] == "distrobox":
            manager.list_containers_distrobox()
    elif args.command == 'remove':
        if manager.config["container_manager"] == "docker":
            manager.remove_container_docker(args.name)
        elif manager.config["container_manager"] == "distrobox":
            manager.remove_container_distrobox(args.name)
    elif args.command == 'build':
        if manager.config["container_manager"] == "distrobox":
            print("for distrobox will not build the image just save a dockerfile")
            manager.build_image(args.image)
        else:
            manager.build_image(args.image)
    elif args.command == 'ibuilder':
        if manager.config["container_manager"] == "distrobox":
            print("for distrobox will not build the image just save a dockerfile")
            manager.build_image_it(args.name, True)
        else:
            manager.build_image_it(args.name, args.no_build)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
