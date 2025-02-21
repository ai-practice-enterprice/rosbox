from jinja2 import Environment
import os
from pick import pick
import json

# defines
current_dir = os.path.dirname(__file__)
base_templates_path = os.path.join(current_dir, 'base_templates')
ros_templates_path = os.path.join(current_dir, 'ros_templates')
entrypoints_templates_path = os.path.join(current_dir, 'entrypoints_templates')
extensions_file = os.path.join(current_dir, 'extensions.json')

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

    def load_extensions_templates_options(self, extensions_path):
        extensions = {}
        with open(extensions_path, 'r') as file:
            data = json.loads(file.read())
            extensions_json = data["template_extensions"]
            for extension_name, sub in extensions_json.items():
                commandstr = ''
                for command in sub["commands"]:
                    commandstr += f"RUN {command}\n"
                extensions[extension_name] = commandstr
        return extensions

    def generate_dockerfile(self, base_template, ros_template, entrypoint_template, extension_list, output_file):
        ros_template = self.ros_templates[ros_template]
        base_template = self.base_templates[base_template]
        entrypoint_template = self.entrypoints_templates[entrypoint_template]
        extensions = self.load_extensions_templates_options(extensions_file)

        # Read the ROS install Dockerfile template from its file
        ros_dockerfile_template = ""
        with open(ros_template, 'r') as file:
            ros_dockerfile_template = file.read()

        # Read the entrypoint Dockerfile template from its file
        entrypoint_template_str = ""
        with open(entrypoint_template, 'r') as file:
            entrypoint_template_str = file.read()

        # generate extension section
        extension_section = ""
        print(extension_list)
        for extension_name in extension_list:
            extension_section += extensions[extension_name]

        # Define the context mapping that will be used to render the base template
        context = {
            'ros_install': ros_dockerfile_template,
            'entrypoint_setup': entrypoint_template_str,
            'extensions_install': extension_section
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
        self.selected_extension = []

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

    def select_extension_template(self):
        title = "Choose your favorite programming language(use space to select)"
        extension_keys = list(self.generator.load_extensions_templates_options(extensions_file).keys())
        out = pick(extension_keys, title, multiselect=True, min_selection_count=0)
        selected_extension_list = []
        for item, _ in out:
            selected_extension_list.append(item)
        out = selected_extension_list
        return out

    def generate_dockerfile(self, base = None, ros = None, entryPoint = None, extension = []):
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
            if extension == []:
                self.selected_extension = self.select_extension_template()
            else:
                self.selected_extension = extension
        else:
            if base != None:
                self.selected_base = base
            if ros != None:
                self.selected_ros = ros
            if entryPoint != None:
                self.selected_entrypoint = entryPoint

        print(self.selected_extension)

        self.generator.generate_dockerfile(
            self.selected_base,
            self.selected_ros,
            self.selected_entrypoint,
            self.selected_extension,
            self.dockerfile_path)
        print("Dockerfile generated successfully")

    def build_image(self, tag = None):
        self.image_builder.build_image(tag if tag is not None else default_image_tag)
        print("Docker image built done")
