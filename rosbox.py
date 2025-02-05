from imageBuilder import InteractiveBuilder
import docker
from docker.types import Mount
import subprocess
import argparse
import os

# class for creating, running, entering and stopping the containers
class ContainerManager:
    # global defentions
    rosbox_suffix = 'rosbox'
    dockerfile_path = 'Dockerfile'

    def __init__(self):
        self.client = docker.from_env()
        self.interactive_builder = InteractiveBuilder(self.dockerfile_path)

    def create_container(self, image_tag, container_name, ros_ws_path=None, auto_start=True, ssh_dir=False):
        container_name = f"{container_name}_{self.rosbox_suffix}"
        try:
            # create mounts
            mounts = []
            if ros_ws_path:
                mounts.append(Mount(
                    target="/home/ubuntu/ros_ws",
                    source=os.path.abspath(ros_ws_path),
                    type="bind",
                    read_only=False
                ))
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
            container = self.client.containers.create(
                image_tag, name=container_name,
                hostname=container_name.replace('_' + self.rosbox_suffix, ''),
                detach=True,
                mounts=mounts,
                labels={"type": "rosbox"})
            print(f"Container {container_name.replace('_' + self.rosbox_suffix, '')} created successfully")
            # start container
            if auto_start:
                container.start()
                print(f"Container {container_name.replace('_' + self.rosbox_suffix, '')} started successfully")
        except Exception as e:
            print(f"Error creating container: {str(e)}")
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

    def enter_container(self, container_name):
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

    def stop_container(self, container_name):
        container_name = f"{container_name}_{self.rosbox_suffix}"
        try:
            container = self.client.containers.get(container_name)
            container.stop()
            print(f"Container {container_name.replace('_' + self.rosbox_suffix, '')} stopped successfully")
        except Exception as e:
            print(f"Error stopping container: {str(e)}")
            raise

    def list_containers(self):
        containers = [c for c in self.client.containers.list(all=True, filters={"label": "type=rosbox"})]
        print(f"{'ID':<12} | {'NAME':<20} | {'STATUS':<20} | {'IMAGE':<20}")
        print("-" * 72)
        for container in containers:
            name = container.name.replace("_" + self.rosbox_suffix, "")
            print(f"{container.short_id:<12} | {name:<20} | {container.status:<20} | {container.image.tags[0]:<20}")
        print(("-" * 72) + "\n")

    def remove_container(self, container_name):
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

    def build_image(self, base_template, ros_template, image_name):
        self.interactive_builder.generate_dockerfile(base_template, ros_template, 'rosbox')
        self.interactive_builder.build_image(image_name)

    def build_image_it(self, image_name):
        self.interactive_builder.generate_dockerfile(entryPoint = 'rosbox')
        self.interactive_builder.build_image(image_name)

def main():
    # check first if docker is installed
    if os.system('docker --version') != 0:
        print("Error: Docker is not installed. Please install Docker first!")
        return

    manager = ContainerManager()

    parser = argparse.ArgumentParser(description='rosbox manager')
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # Create parser for "create" command
    create_parser = subparsers.add_parser('create', help='create rosbox')
    create_parser.add_argument('image', help='image name for the rosbox')
    create_parser.add_argument('name', help='name of the rosbox')
    create_parser.add_argument('--ros_ws', help='path to the ROS workspace', default=None)
    create_parser.add_argument('--no_start', help='disable container autostart wen created', action='store_true')
    create_parser.add_argument('--ssh_keys', help='mount the ssh dir from host to container', action='store_true')
    # TODO add nvidia suport

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
    build_parser = subparsers.add_parser('build', help='start rosbox')
    build_parser.add_argument('--base', help=f'Base image to use. Options: {list(manager.interactive_builder.generator.base_templates.keys())}', required=True)
    build_parser.add_argument('--ros', help=f'ROS template to use. Options: {list(manager.interactive_builder.generator.ros_templates.keys())}', required=True)
    build_parser.add_argument('--name', help='name of the image', required=True)

    # Create parser for "ibuilder" command
    ibuilder_parser = subparsers.add_parser('ibuilder', help='Build docker image using a interactive interface to select the templates')
    ibuilder_parser.add_argument('name', help='name of the image')

    args = parser.parse_args()

    if args.command == 'create':
        manager.create_container(args.image, args.name, args.ros_ws, not args.no_start, args.ssh_keys)
    elif args.command == 'start':
        manager.start_container(args.name)
    elif args.command == 'enter':
        manager.enter_container(args.name)
    elif args.command == 'stop':
        manager.stop_container(args.name)
    elif args.command == 'list':
        manager.list_containers()
    elif args.command == 'remove':
        manager.remove_container(args.name)
    elif args.command == 'build':
        manager.build_image(args.base, args.ros, args.name)
    elif args.command == 'ibuilder':
        manager.build_image_it(args.name)

if __name__ == "__main__":
    main()
