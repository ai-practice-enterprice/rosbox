from importlib.metadata import entry_points
from jinja2 import Environment
import os
import argparse
from pick import pick

# defines
base_templates_path = 'base_templates'
ros_templates_path = 'ros_templates'
entrypoints_templates_path = 'entrypoints_templates'
default_base_template = 'universal'
default_ros_template = 'ros-desktop'
default_entrypoint_template = 'it'
default_image_tag = 'ros2'

# Class to generate Dockerfile
class DockerfileGenerator:
    def __init__(self):
        self.base_templates = self.load_base_templates_options()
        self.ros_templates = self.load_ros_templates_options()
        self.entrypoints_templates = self.load_entrypoints_templates_options()

    def load_base_templates_options(self):
        template_files = {}
        for filename in os.listdir(base_templates_path):
            if filename.endswith('.jinja'):
                key = filename.replace('.jinja', '')
                key = key.replace('Dockerfile.', '')
                template_files[key] = os.path.join(base_templates_path, filename)
        return template_files

    def load_ros_templates_options(self):
        template_files = {}
        for filename in os.listdir(ros_templates_path):
            if filename.endswith('.template'):
                key = filename.replace('.template', '')
                key = key.replace('Dockerfile.', '')
                template_files[key] = os.path.join(ros_templates_path, filename)
        return template_files

    def load_entrypoints_templates_options(self):
        template_files = {}
        for filename in os.listdir(entrypoints_templates_path):
            if filename.endswith('.template'):
                key = filename.replace('.template', '')
                key = key.replace('Dockerfile.', '')
                template_files[key] = os.path.join(entrypoints_templates_path, filename)
        return template_files

    def generate_dockerfile(self, base_template, ros_template, entrypoint_template, output_file):
        ros_template = self.ros_templates[ros_template]
        base_template = self.base_templates[base_template]
        entrypoint_template = self.entrypoints_templates[entrypoint_template]

        # Read the ROS install Dockerfile template from its file
        with open(ros_template, 'r') as file:
            ros_dockerfile_template = file.read()

        # Read the entrypoint Dockerfile template from its file
        with open(entrypoint_template, 'r') as file:
            entrypoint_template_str = file.read()

        # Define the context mapping that will be used to render the base template
        context = {
            'ros_install': ros_dockerfile_template,
            'entrypoint_setup': entrypoint_template_str
        }

        # Render the base template with the provided context data
        with open(base_template, 'r') as file:
            base_template_str = file.read()
        env = Environment()
        template_obj = env.from_string(base_template_str)
        rendered_dockerfile = template_obj.render(context)

        # Write the rendered content to the specified output file
        with open(output_file, 'w') as f:
            f.write(rendered_dockerfile)

# class to build the image
class ImageBuilder:
    def __init__(self, dockerfile_path):
        self.dockerfile_path = dockerfile_path

    def build_image(self, tag):
        if os.path.exists(self.dockerfile_path):
            try:
                return_code = os.system(f'docker build -t {tag} -f {self.dockerfile_path} .')
                if return_code == 0:
                    print("Docker image built successfully")
                else:
                    raise Exception(f"Docker build failed with return code {return_code}")
            except Exception as e:
                print(f"Error building Docker image: {str(e)}")
                raise
        else:
            print("Error: Dockerfile not found. Please generate the Dockerfile first!")

# class to build the image using an interactive interface
class InteractiveBuilder:
    def __init__(self, dockerfile_path):
        self.dockerfile_path = dockerfile_path
        self.generator = DockerfileGenerator()
        self.image_builder = ImageBuilder(self.dockerfile_path)
        self.selected_base = default_base_template
        self.selected_ros = default_ros_template
        self.selected_entrypoint = default_entrypoint_template

    def select_base_template(self):
        options = list(self.generator.base_templates.keys())
        title = "Choose a base template:"
        self.selected_base, _ = pick(options, title)

    def select_ros_template(self):
        options = list(self.generator.ros_templates.keys())
        title = "Choose a ROS template:"
        self.selected_ros, _ = pick(options, title)

    def select_entrypoint_template(self):
        options = list(self.generator.entrypoints_templates.keys())
        title = "Choose an entrypoint template:"
        self.selected_entrypoint, _ = pick(options, title)

    def generate_dockerfile(self, base = None, ros = None, entryPoint = None):
        options = ["default", "custom"]
        title = "Choose a generation method:"
        selected_option, _ = pick(options, title)
        if selected_option == "custom":
            if base == None:
                self.select_base_template()
            else:
                self.selected_base = base
            if ros == None:
                self.select_ros_template()
            else:
                self.selected_ros = ros
            if entryPoint == None:
                self.select_entrypoint_template()
            else:
                self.selected_entrypoint = entryPoint

        self.generator.generate_dockerfile(self.selected_base, self.selected_ros, self.selected_entrypoint, self.dockerfile_path)
        print("Dockerfile generated successfully")

    def build_image(self, tag = None):
        self.image_builder.build_image(tag if tag is not None else default_image_tag)
        print("Docker image built done")

    def run(self):
        self.generate_dockerfile()
        option = ["yes", "no"]
        title = "Do you want to build the image?"
        selected_option, _ = pick(option, title)
        if selected_option == "yes":
            self.build_image()

def main():
    # check first if docker is installed
    if os.system('docker --version') != 0:
        print("Error: Docker is not installed. Please install Docker first!")
        return

    generator = DockerfileGenerator()
    parser = argparse.ArgumentParser(description='Docker image builder')
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # Create parser for "gen" command
    gen_parser = subparsers.add_parser('gen', help='Generate Dockerfile')
    gen_parser.add_argument('--base', help=f'Base image to use. Options: {list(generator.base_templates.keys())}', required=True)
    gen_parser.add_argument('--ros', help=f'ROS template to use. Options: {list(generator.ros_templates.keys())}', required=True)
    gen_parser.add_argument('--entrypoint', help=f'Entrypoint template to use. Options: {list(generator.entrypoints_templates.keys())}', required=True)

    # Create parser for "build" command
    build_parser = subparsers.add_parser('build', help='Build Docker image')
    build_parser.add_argument('--tag', help='Tag for the image', default=default_image_tag)
    build_parser.add_argument('--dockerfile', help='Path to the Dockerfile', default='Dockerfile')

    subparsers.add_parser('ibuilder', help='Build docker image using a interactive interface to select the templates')

    args = parser.parse_args()

    if args.command == 'gen':
        # Use the selected templates for generation
        print("Selected Base Template:", args.base)
        print("Selected ROS Template:", args.ros)
        print("Selected Entrypoint Template:", args.entrypoint)
        generator.generate_dockerfile(args.base, args.ros, args.entrypoint, 'Dockerfile')
        print("Dockerfile generated successfully")

    elif args.command == 'build':
        dockerfile_path = 'Dockerfile'
        builder = ImageBuilder(dockerfile_path)
        builder.build_image(args.tag)

    elif args.command == 'ibuilder':
        dockerfile_path = 'Dockerfile'
        IB = InteractiveBuilder(dockerfile_path)
        IB.run()


if __name__ == '__main__':
    main()
